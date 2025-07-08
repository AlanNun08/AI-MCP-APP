from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import openai
from openai import OpenAI
import json
import httpx
import asyncio
import time
import base64
import re
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Walmart API setup
WALMART_CONSUMER_ID = os.environ['WALMART_CONSUMER_ID']
WALMART_KEY_VERSION = os.environ['WALMART_KEY_VERSION']
WALMART_PRIVATE_KEY = os.environ['WALMART_PRIVATE_KEY']

# Create the main app without a prefix
app = FastAPI(title="AI Recipe & Grocery App", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    name: str
    email: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []

class Recipe(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: int  # in minutes
    cook_time: int  # in minutes
    servings: int
    cuisine_type: str
    dietary_tags: List[str] = []
    difficulty: str  # easy, medium, hard
    # New fields for healthy recipes
    calories_per_serving: Optional[int] = None
    is_healthy: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

class RecipeGenRequest(BaseModel):
    user_id: str
    cuisine_type: Optional[str] = None
    dietary_preferences: List[str] = []
    ingredients_on_hand: List[str] = []
    prep_time_max: Optional[int] = None
    servings: int = 4
    difficulty: str = "medium"
    # New healthy options
    is_healthy: bool = False
    max_calories_per_serving: Optional[int] = None
    # New budget options
    is_budget_friendly: bool = False
    max_budget: Optional[float] = None

class WalmartProduct(BaseModel):
    product_id: str
    name: str
    price: float
    thumbnail_image: Optional[str] = None
    availability: str = "Available"

class GroceryCart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    items: List[Dict[str, Any]]  # {product_id, name, quantity, price, original_ingredient}
    total_price: float
    walmart_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Walmart API functions
def get_walmart_auth_headers():
    """Generate Walmart API authentication headers"""
    try:
        # Load private key
        private_key = serialization.load_pem_private_key(
            WALMART_PRIVATE_KEY.encode(),
            password=None
        )
        
        # Generate timestamp
        timestamp = str(int(time.time() * 1000))
        
        # Create message to sign
        message = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n".encode("utf-8")
        
        # Sign the message
        signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        
        # Return headers
        return {
            "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
            "WM_CONSUMER.INTIMESTAMP": timestamp,
            "WM_SEC.KEY_VERSION": WALMART_KEY_VERSION,
            "WM_SEC.AUTH_SIGNATURE": signature_b64,
            "Content-Type": "application/json"
        }
    except Exception as e:
        logging.error(f"Error generating Walmart auth headers: {str(e)}")
        return None

async def search_walmart_product(ingredient_name: str) -> Optional[WalmartProduct]:
    """Search for a product on Walmart using their API"""
    try:
        headers = get_walmart_auth_headers()
        if not headers:
            return None
        
        # Clean ingredient name for search
        clean_ingredient = clean_ingredient_name(ingredient_name)
        
        # Walmart API endpoint
        url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search"
        params = {
            "query": clean_ingredient,
            "numItems": 5  # Get top 5 results
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response and find best match
                if "items" in data and len(data["items"]) > 0:
                    # Get the first/best match
                    item = data["items"][0]
                    
                    return WalmartProduct(
                        product_id=str(item.get("itemId", "")),
                        name=item.get("name", clean_ingredient),
                        price=float(item.get("salePrice", 0.0)),
                        thumbnail_image=item.get("thumbnailImage", ""),
                        availability="Available"
                    )
                else:
                    logging.warning(f"No Walmart products found for: {clean_ingredient}")
                    return None
            else:
                logging.error(f"Walmart API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logging.error(f"Error searching Walmart for {ingredient_name}: {str(e)}")
        return None

def clean_ingredient_name(ingredient: str) -> str:
    """Clean ingredient name for better search results"""
    # Remove quantities and measurements
    ingredient = re.sub(r'\d+[\s]*(?:cups?|tbsp|tsp|tablespoons?|teaspoons?|oz|ounces?|lbs?|pounds?|grams?|kg|ml|liters?)', '', ingredient, flags=re.IGNORECASE)
    
    # Remove common cooking terms
    cooking_terms = ['chopped', 'diced', 'sliced', 'minced', 'fresh', 'dried', 'ground', 'crushed', 'finely', 'roughly', 'large', 'small', 'medium']
    for term in cooking_terms:
        ingredient = re.sub(rf'\b{term}\b', '', ingredient, flags=re.IGNORECASE)
    
    # Remove extra whitespace and clean up
    ingredient = re.sub(r'\s+', ' ', ingredient).strip()
    
    # Remove leading/trailing punctuation
    ingredient = ingredient.strip('.,;:-')
    
    return ingredient

def extract_quantity_from_ingredient(ingredient: str) -> int:
    """Extract quantity from ingredient string"""
    # Look for numbers at the beginning
    match = re.search(r'^(\d+)', ingredient.strip())
    if match:
        return int(match.group(1))
    
    # Look for fractions or decimals
    fraction_match = re.search(r'(\d+/\d+|\d*\.\d+)', ingredient)
    if fraction_match:
        fraction_str = fraction_match.group(1)
        if '/' in fraction_str:
            num, den = fraction_str.split('/')
            return max(1, int(float(num) / float(den)))
        else:
            return max(1, int(float(fraction_str)))
    
    return 1  # Default quantity

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AI Recipe & Grocery App API"}

# User management
@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserCreate):
    user_dict = user_update.dict()
    user_dict["id"] = user_id
    user_obj = User(**user_dict)
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": user_obj.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_obj

# Recipe generation
@api_router.post("/recipes/generate", response_model=Recipe)
async def generate_recipe(request: RecipeGenRequest):
    try:
        # Get user preferences
        user = await db.users.find_one({"id": request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build the prompt
        prompt = f"""
        Generate a detailed recipe with the following requirements:
        - Cuisine type: {request.cuisine_type or 'any'}
        - Dietary preferences: {', '.join(request.dietary_preferences) if request.dietary_preferences else 'none'}
        - User allergies to avoid: {', '.join(user.get('allergies', [])) if user.get('allergies') else 'none'}
        - Ingredients on hand: {', '.join(request.ingredients_on_hand) if request.ingredients_on_hand else 'none'}
        - Maximum prep time: {request.prep_time_max or 'any'} minutes
        - Servings: {request.servings}
        - Difficulty: {request.difficulty}
        - User's favorite cuisines: {', '.join(user.get('favorite_cuisines', [])) if user.get('favorite_cuisines') else 'any'}
        
        Please respond with a JSON object containing:
        {{
            "title": "Recipe name",
            "description": "Brief description of the dish",
            "ingredients": ["ingredient 1", "ingredient 2", ...],
            "instructions": ["step 1", "step 2", ...],
            "prep_time": prep_time_in_minutes,
            "cook_time": cook_time_in_minutes,
            "servings": number_of_servings,
            "cuisine_type": "cuisine_type",
            "dietary_tags": ["tag1", "tag2", ...],
            "difficulty": "easy|medium|hard"
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef and recipe developer. Always respond with valid JSON only. Do not include any text before or after the JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and clean the response content
        response_content = response.choices[0].message.content.strip()
        
        # Remove any markdown formatting if present
        if response_content.startswith('```json'):
            response_content = response_content[7:]
        if response_content.endswith('```'):
            response_content = response_content[:-3]
        
        # Clean any extra whitespace
        response_content = response_content.strip()
        
        # Log the response for debugging
        logging.info(f"OpenAI Response: {response_content}")
        
        try:
            recipe_data = json.loads(response_content)
        except json.JSONDecodeError as json_error:
            logging.error(f"JSON parsing error: {json_error}")
            logging.error(f"Response content: {response_content}")
            raise HTTPException(status_code=500, detail="Failed to parse recipe from AI response")
        
        # Create recipe object
        recipe = Recipe(
            title=recipe_data["title"],
            description=recipe_data["description"],
            ingredients=recipe_data["ingredients"],
            instructions=recipe_data["instructions"],
            prep_time=recipe_data["prep_time"],
            cook_time=recipe_data["cook_time"],
            servings=recipe_data["servings"],
            cuisine_type=recipe_data["cuisine_type"],
            dietary_tags=recipe_data["dietary_tags"],
            difficulty=recipe_data["difficulty"],
            user_id=request.user_id
        )
        
        # Save to database
        await db.recipes.insert_one(recipe.dict())
        
        return recipe
        
    except Exception as e:
        logging.error(f"Error generating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recipe")

# Recipe management
@api_router.get("/recipes", response_model=List[Recipe])
async def get_recipes(user_id: Optional[str] = None):
    filter_dict = {}
    if user_id:
        filter_dict["user_id"] = user_id
    
    recipes = await db.recipes.find(filter_dict).to_list(100)
    return [Recipe(**recipe) for recipe in recipes]

@api_router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    recipe = await db.recipes.find_one({"id": recipe_id})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Recipe(**recipe)

@api_router.post("/recipes/{recipe_id}/save")
async def save_recipe(recipe_id: str, user_id: str):
    recipe = await db.recipes.find_one({"id": recipe_id})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Add to user's saved recipes
    await db.users.update_one(
        {"id": user_id},
        {"$addToSet": {"saved_recipes": recipe_id}}
    )
    
    return {"message": "Recipe saved successfully"}

# Walmart integration with real API
@api_router.post("/grocery/cart", response_model=GroceryCart)
async def create_grocery_cart(recipe_id: str, user_id: str):
    # Get recipe
    recipe = await db.recipes.find_one({"id": recipe_id})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Map ingredients to Walmart products using real API
    cart_items = []
    total_price = 0
    walmart_product_ids = []
    
    logging.info(f"Processing {len(recipe['ingredients'])} ingredients for Walmart search")
    
    # Process ingredients in parallel for better performance
    search_tasks = []
    for ingredient in recipe["ingredients"]:
        search_tasks.append(search_walmart_product(ingredient))
    
    # Execute all searches concurrently
    walmart_products = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    for i, ingredient in enumerate(recipe["ingredients"]):
        walmart_product = walmart_products[i]
        
        # Extract quantity from ingredient
        quantity = extract_quantity_from_ingredient(ingredient)
        
        if isinstance(walmart_product, WalmartProduct) and walmart_product.product_id:
            # Successfully found Walmart product
            item_total = walmart_product.price * quantity
            
            cart_items.append({
                "product_id": walmart_product.product_id,
                "name": walmart_product.name,
                "quantity": quantity,
                "price": walmart_product.price,
                "total": item_total,
                "original_ingredient": ingredient,
                "status": "found",
                "thumbnail": walmart_product.thumbnail_image
            })
            
            total_price += item_total
            
            # Add to Walmart URL
            if quantity > 1:
                walmart_product_ids.append(f"{walmart_product.product_id}_{quantity}")
            else:
                walmart_product_ids.append(walmart_product.product_id)
                
        else:
            # Product not found or error occurred
            cart_items.append({
                "product_id": None,
                "name": clean_ingredient_name(ingredient),
                "quantity": quantity,
                "price": 0.0,
                "total": 0.0,
                "original_ingredient": ingredient,
                "status": "not_found",
                "thumbnail": None
            })
            
            logging.warning(f"Could not find Walmart product for: {ingredient}")
    
    # Generate Walmart affiliate URL
    if walmart_product_ids:
        walmart_url = f"https://affil.walmart.com/cart/addToCart?items={','.join(walmart_product_ids)}"
    else:
        walmart_url = "https://walmart.com"  # Fallback URL
    
    # Create cart
    cart = GroceryCart(
        user_id=user_id,
        recipe_id=recipe_id,
        items=cart_items,
        total_price=round(total_price, 2),
        walmart_url=walmart_url
    )
    
    # Save to database
    await db.grocery_carts.insert_one(cart.dict())
    
    logging.info(f"Created grocery cart with {len([item for item in cart_items if item['status'] == 'found'])} found items out of {len(cart_items)} total")
    
    return cart

@api_router.get("/grocery/cart/{cart_id}", response_model=GroceryCart)
async def get_grocery_cart(cart_id: str):
    cart = await db.grocery_carts.find_one({"id": cart_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return GroceryCart(**cart)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
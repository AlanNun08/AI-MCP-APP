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
app = FastAPI(title="AI Recipe & Grocery App", version="2.0.0")

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

class WalmartProduct(BaseModel):
    product_id: str
    name: str
    price: float
    thumbnail_image: Optional[str] = None
    availability: str = "Available"
    size: Optional[str] = None
    brand: Optional[str] = None

class IngredientOption(BaseModel):
    ingredient_name: str
    original_ingredient: str
    quantity: int
    options: List[WalmartProduct]  # 3 options: main + 2 alternatives

class GroceryCartWithOptions(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    ingredient_options: List[IngredientOption]  # Multiple options per ingredient
    total_ingredients: int
    found_ingredients: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserIngredientSelection(BaseModel):
    ingredient_name: str
    selected_product_id: str
    quantity: int

class CustomCartRequest(BaseModel):
    cart_id: str
    selections: List[UserIngredientSelection]

class CustomCart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    cart_id: str
    selections: List[Dict[str, Any]]  # Selected products with details
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

async def search_walmart_products(ingredient_name: str, num_results: int = 3) -> List[WalmartProduct]:
    """Search for multiple product options on Walmart"""
    try:
        headers = get_walmart_auth_headers()
        if not headers:
            return []
        
        # Clean ingredient name for search
        clean_ingredient = clean_ingredient_name(ingredient_name)
        
        # Walmart API endpoint
        url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search"
        params = {
            "query": clean_ingredient,
            "numItems": 25  # Get more results to find alternatives
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                products = []
                
                if "items" in data and len(data["items"]) > 0:
                    # Filter and sort products by relevance and price diversity
                    items = data["items"]
                    
                    # Sort by price to get variety
                    items_by_price = sorted(items, key=lambda x: float(x.get("salePrice", 999)))
                    
                    # Get up to num_results products with different price points
                    selected_items = []
                    if len(items_by_price) >= num_results:
                        # Get cheapest, mid-range, and most expensive options
                        selected_items = [
                            items_by_price[0],  # Cheapest
                            items_by_price[len(items_by_price)//2],  # Mid-range
                            items_by_price[-1] if len(items_by_price) > 1 else items_by_price[0]  # Most expensive
                        ]
                    else:
                        selected_items = items_by_price[:num_results]
                    
                    for item in selected_items:
                        products.append(WalmartProduct(
                            product_id=str(item.get("itemId", "")),
                            name=item.get("name", clean_ingredient),
                            price=float(item.get("salePrice", 0.0)),
                            thumbnail_image=item.get("thumbnailImage", ""),
                            availability="Available",
                            size=item.get("size", ""),
                            brand=item.get("brandName", "")
                        ))
                
                return products[:num_results]
            else:
                logging.error(f"Walmart API error: {response.status_code} - {response.text}")
                return []
                
    except Exception as e:
        logging.error(f"Error searching Walmart for {ingredient_name}: {str(e)}")
        return []

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
    return {"message": "AI Recipe & Grocery App API v2.0 - Now with Healthy & Budget Features!"}

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

# Enhanced Recipe generation with healthy and budget options
@api_router.post("/recipes/generate", response_model=Recipe)
async def generate_recipe(request: RecipeGenRequest):
    try:
        # Get user preferences
        user = await db.users.find_one({"id": request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build enhanced prompt with healthy and budget constraints
        health_constraint = ""
        if request.is_healthy and request.max_calories_per_serving:
            health_constraint = f"- HEALTHY RECIPE: Maximum {request.max_calories_per_serving} calories per serving. Focus on lean proteins, vegetables, whole grains, and minimal processed ingredients."
        
        budget_constraint = ""
        if request.is_budget_friendly and request.max_budget:
            budget_constraint = f"- BUDGET-FRIENDLY: Total ingredient cost should be around ${request.max_budget}. Use affordable ingredients like beans, rice, pasta, seasonal vegetables, and budget-friendly proteins."
        
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
        {health_constraint}
        {budget_constraint}
        
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
            "difficulty": "easy|medium|hard",
            "calories_per_serving": estimated_calories_per_serving_as_number
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef and nutritionist. Always respond with valid JSON only. Include accurate calorie estimates. Do not include any text before or after the JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
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
            calories_per_serving=recipe_data.get("calories_per_serving"),
            is_healthy=request.is_healthy,
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

# Enhanced Walmart integration with multiple options per ingredient
@api_router.post("/grocery/cart-options", response_model=GroceryCartWithOptions)
async def create_grocery_cart_with_options(recipe_id: str, user_id: str):
    """Create grocery cart with 3 options per ingredient for budget-friendly shopping"""
    # Get recipe
    recipe = await db.recipes.find_one({"id": recipe_id})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    ingredient_options = []
    total_ingredients = len(recipe["ingredients"])
    found_ingredients = 0
    
    logging.info(f"Processing {total_ingredients} ingredients for Walmart search with 3 options each")
    
    # Process ingredients in parallel for better performance
    search_tasks = []
    for ingredient in recipe["ingredients"]:
        search_tasks.append(search_walmart_products(ingredient, num_results=3))
    
    # Execute all searches concurrently
    all_product_options = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    for i, ingredient in enumerate(recipe["ingredients"]):
        product_options = all_product_options[i]
        quantity = extract_quantity_from_ingredient(ingredient)
        
        if isinstance(product_options, list) and len(product_options) > 0:
            # Successfully found product options
            found_ingredients += 1
            
            ingredient_options.append(IngredientOption(
                ingredient_name=clean_ingredient_name(ingredient),
                original_ingredient=ingredient,
                quantity=quantity,
                options=product_options
            ))
        else:
            # No products found
            logging.warning(f"Could not find Walmart products for: {ingredient}")
            
            # Add empty options
            ingredient_options.append(IngredientOption(
                ingredient_name=clean_ingredient_name(ingredient),
                original_ingredient=ingredient,
                quantity=quantity,
                options=[]
            ))
    
    # Create cart with options
    cart = GroceryCartWithOptions(
        user_id=user_id,
        recipe_id=recipe_id,
        ingredient_options=ingredient_options,
        total_ingredients=total_ingredients,
        found_ingredients=found_ingredients
    )
    
    # Save to database
    await db.grocery_carts_options.insert_one(cart.dict())
    
    logging.info(f"Created grocery cart with options: {found_ingredients}/{total_ingredients} ingredients found")
    
    return cart

@api_router.get("/grocery/cart-options/{cart_id}", response_model=GroceryCartWithOptions)
async def get_grocery_cart_options(cart_id: str):
    cart = await db.grocery_carts_options.find_one({"id": cart_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return GroceryCartWithOptions(**cart)

@api_router.post("/grocery/custom-cart", response_model=CustomCart)
async def create_custom_cart(request: CustomCartRequest):
    """Create final cart based on user's ingredient selections"""
    # Get the original cart with options
    cart_options = await db.grocery_carts_options.find_one({"id": request.cart_id})
    if not cart_options:
        raise HTTPException(status_code=404, detail="Cart options not found")
    
    selected_products = []
    total_price = 0
    walmart_product_ids = []
    
    # Process each user selection
    for selection in request.selections:
        # Find the matching ingredient option
        ingredient_option = None
        for ing_opt in cart_options["ingredient_options"]:
            if ing_opt["ingredient_name"] == selection.ingredient_name:
                ingredient_option = ing_opt
                break
        
        if not ingredient_option:
            continue
        
        # Find the selected product
        selected_product = None
        for product in ingredient_option["options"]:
            if product["product_id"] == selection.selected_product_id:
                selected_product = product
                break
        
        if selected_product:
            item_total = selected_product["price"] * selection.quantity
            
            selected_products.append({
                "product_id": selected_product["product_id"],
                "name": selected_product["name"],
                "price": selected_product["price"],
                "quantity": selection.quantity,
                "total": item_total,
                "original_ingredient": ingredient_option["original_ingredient"],
                "thumbnail": selected_product.get("thumbnail_image", "")
            })
            
            total_price += item_total
            
            # Add to Walmart URL
            if selection.quantity > 1:
                walmart_product_ids.append(f"{selected_product['product_id']}_{selection.quantity}")
            else:
                walmart_product_ids.append(selected_product["product_id"])
    
    # Generate custom Walmart affiliate URL
    if walmart_product_ids:
        walmart_url = f"https://affil.walmart.com/cart/addToCart?items={','.join(walmart_product_ids)}"
    else:
        walmart_url = "https://walmart.com"
    
    # Create custom cart
    custom_cart = CustomCart(
        user_id=cart_options["user_id"],
        recipe_id=cart_options["recipe_id"],
        cart_id=request.cart_id,
        selections=selected_products,
        total_price=round(total_price, 2),
        walmart_url=walmart_url
    )
    
    # Save to database
    await db.custom_carts.insert_one(custom_cart.dict())
    
    logging.info(f"Created custom cart with {len(selected_products)} selected items, total: ${total_price:.2f}")
    
    return custom_cart

@api_router.get("/grocery/custom-cart/{cart_id}", response_model=CustomCart)
async def get_custom_cart(cart_id: str):
    cart = await db.custom_carts.find_one({"id": cart_id})
    if not cart:
        raise HTTPException(status_code=404, detail="Custom cart not found")
    return CustomCart(**cart)

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
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

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

class WalmartProduct(BaseModel):
    product_id: str
    name: str
    price: float
    category: str
    common_ingredient_names: List[str]

class GroceryCart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    items: List[Dict[str, Any]]  # {product_id, name, quantity, price}
    total_price: float
    walmart_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Walmart product mapping (mock data for now)
WALMART_PRODUCTS = {
    "chicken breast": {"product_id": "945193065", "name": "Chicken Breast", "price": 8.99, "category": "meat"},
    "ground beef": {"product_id": "660768274", "name": "Ground Beef", "price": 6.99, "category": "meat"},
    "rice": {"product_id": "123456789", "name": "White Rice", "price": 2.99, "category": "grains"},
    "pasta": {"product_id": "987654321", "name": "Pasta", "price": 1.99, "category": "grains"},
    "tomatoes": {"product_id": "456789123", "name": "Fresh Tomatoes", "price": 3.49, "category": "produce"},
    "onions": {"product_id": "789123456", "name": "Yellow Onions", "price": 2.29, "category": "produce"},
    "garlic": {"product_id": "321654987", "name": "Fresh Garlic", "price": 1.99, "category": "produce"},
    "olive oil": {"product_id": "654987321", "name": "Olive Oil", "price": 5.99, "category": "condiments"},
    "salt": {"product_id": "147258369", "name": "Table Salt", "price": 1.49, "category": "spices"},
    "pepper": {"product_id": "369258147", "name": "Black Pepper", "price": 2.99, "category": "spices"},
    "cheese": {"product_id": "258147369", "name": "Cheddar Cheese", "price": 4.99, "category": "dairy"},
    "milk": {"product_id": "741852963", "name": "Whole Milk", "price": 3.99, "category": "dairy"},
    "eggs": {"product_id": "852963741", "name": "Large Eggs", "price": 2.99, "category": "dairy"},
    "bread": {"product_id": "963741852", "name": "White Bread", "price": 2.49, "category": "bakery"},
    "butter": {"product_id": "159753486", "name": "Butter", "price": 4.49, "category": "dairy"}
}

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

# Walmart integration
@api_router.post("/grocery/cart", response_model=GroceryCart)
async def create_grocery_cart(recipe_id: str, user_id: str):
    # Get recipe
    recipe = await db.recipes.find_one({"id": recipe_id})
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # Map ingredients to Walmart products
    cart_items = []
    total_price = 0
    walmart_product_ids = []
    
    for ingredient in recipe["ingredients"]:
        # Simple ingredient matching (can be improved with NLP)
        ingredient_lower = ingredient.lower()
        matched = False
        
        for key, product in WALMART_PRODUCTS.items():
            if key in ingredient_lower:
                quantity = 1  # Default quantity
                # Try to extract quantity from ingredient string
                import re
                qty_match = re.search(r'(\d+)', ingredient)
                if qty_match:
                    quantity = int(qty_match.group(1))
                
                cart_items.append({
                    "product_id": product["product_id"],
                    "name": product["name"],
                    "quantity": quantity,
                    "price": product["price"],
                    "original_ingredient": ingredient
                })
                
                total_price += product["price"] * quantity
                
                # Add to Walmart URL
                if quantity > 1:
                    walmart_product_ids.append(f"{product['product_id']}_{quantity}")
                else:
                    walmart_product_ids.append(product["product_id"])
                
                matched = True
                break
        
        if not matched:
            # Add as unmatched item
            cart_items.append({
                "product_id": None,
                "name": ingredient,
                "quantity": 1,
                "price": 0,
                "original_ingredient": ingredient,
                "status": "not_found"
            })
    
    # Generate Walmart URL
    walmart_url = f"https://affil.walmart.com/cart/addToCart?items={','.join(walmart_product_ids)}"
    
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
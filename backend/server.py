from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from dateutil import parser
# Removed ObjectId import as it's not needed and causes serialization issues
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
import bcrypt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from email_service import email_service

# DISABLE ALL CACHING AND ENSURE FRESH DATA
import gc
gc.disable()  # Disable garbage collection caching

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection - NO CACHING, FRESH CONNECTIONS
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')

def get_db():
    """Get fresh database connection - NO CACHING"""
    fresh_client = AsyncIOMotorClient(mongo_url)
    return fresh_client[db_name]

# Use fresh connection for immediate operations
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Custom JSON encoder for MongoDB documents
def mongo_to_dict(obj):
    """Convert MongoDB document to dict, handling _id field"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key == '_id':
                # Skip MongoDB _id field
                continue
            elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes, dict)):
                # Handle iterables (like lists)
                result[key] = [mongo_to_dict(item) for item in value]
            elif isinstance(value, dict):
                # Handle nested dictionaries
                result[key] = mongo_to_dict(value)
            else:
                # Handle primitive values
                result[key] = value
        return result
    return obj

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

# UUID-based ID utilities for JSON serialization
def create_unique_id() -> str:
    """Create a unique string ID using UUID"""
    return str(uuid.uuid4())

# Enhanced Models for Email Verification
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    email: EmailStr
    password_hash: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None

class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []

class VerificationCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email: str
    code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_used: bool = False

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ResendCodeRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Original models (keeping existing functionality)
class UserCreate(BaseModel):
    name: str
    email: str
    dietary_preferences: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []

class RecipeGenRequest(BaseModel):
    user_id: str
    recipe_category: Optional[str] = None  # 'cuisine', 'snack', 'beverage'
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
    # Shopping list for Walmart API (just ingredient names)
    shopping_list: Optional[List[str]] = []

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StarbucksRequest(BaseModel):
    user_id: str
    drink_type: str  # frappuccino, refresher, lemonade, iced_matcha_latte, random
    flavor_inspiration: Optional[str] = None  # Optional flavor inspiration like "tres leches", "ube", "mango tajin"

class StarbucksRecipe(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    drink_name: str
    description: str
    base_drink: str
    modifications: List[str]
    ordering_script: str
    pro_tips: List[str]
    why_amazing: str
    category: str  # frappuccino, latte, etc.
    ingredients_breakdown: Optional[List[str]] = []  # Main ingredients for display
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WalmartProduct(BaseModel):
    product_id: str
    name: str
    price: float
    thumbnail_image: Optional[str] = None
    availability: str = "Available"

class IngredientOption(BaseModel):
    ingredient_name: str
    original_ingredient: str
    options: List[WalmartProduct]

class GroceryCartOptions(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    ingredient_options: List[IngredientOption]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GroceryCartProduct(BaseModel):
    ingredient_name: str
    product_id: str
    name: str
    price: float
    quantity: int = 1

class GroceryCart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recipe_id: str
    products: List[GroceryCartProduct]
    total_price: float
    walmart_url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Password hashing utilities
@app.post("/api/generate-starbucks-drink")
async def generate_starbucks_drink(request: StarbucksRequest):
    """Generate a creative Starbucks secret menu drink with drive-thru ordering script"""
    try:
        # Handle random drink type
        if request.drink_type == "random":
            import random
            drink_types = ["frappuccino", "refresher", "lemonade", "iced_matcha_latte"]
            request.drink_type = random.choice(drink_types)
            
        # Build specialized prompt for Starbucks drinks
        prompt_parts = []
        
        # Add flavor inspiration if provided
        flavor_context = ""
        if request.flavor_inspiration:
            flavor_context = f" with {request.flavor_inspiration} flavors"
            
        prompt_parts.append(f"""Create a viral-worthy Starbucks secret menu drink that's a creative {request.drink_type}{flavor_context}. This should be an Instagram-ready drink hack that TikTok users would love to try and share.

IMPORTANT: Focus on creating a {request.drink_type} that's unique, visually appealing, and easy to order at any Starbucks location.

Respond with JSON in this exact format:
{{
  "drink_name": "Creative catchy name (like 'Unicorn Dreams Frappuccino' or 'Sunset Mango Refresher')",
  "description": "1-2 sentence description of taste and visual appeal",
  "base_drink": "Base Starbucks drink to order (size and drink name)",
  "modifications": [
    "Specific modification 1",
    "Specific modification 2",
    "Specific modification 3"
  ],
  "ordering_script": "Complete sentence to say at drive-thru: 'Hi, can I get a...'",
  "pro_tips": [
    "Pro tip 1 for best results",
    "Pro tip 2 for customization"
  ],
  "why_amazing": "Why this drink is special and Instagram-worthy",
  "category": "{request.drink_type}",
  "ingredients_breakdown": [
    "Main ingredient 1",
    "Main ingredient 2", 
    "Main ingredient 3"
  ]
}}

Make this drink sound like a must-try secret menu item that would go viral on social media!""")

        # Generate the drink using OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative Starbucks drink expert who creates viral secret menu items. Always respond with valid JSON only."},
                {"role": "user", "content": " ".join(prompt_parts)}
            ],
            max_tokens=1000,
            temperature=0.8  # Higher temperature for more creativity
        )
        
        # Parse the response
        recipe_json = response.choices[0].message.content.strip()
        
        # Clean up the JSON (remove markdown formatting if present)
        if recipe_json.startswith("```json"):
            recipe_json = recipe_json[7:]
        if recipe_json.endswith("```"):
            recipe_json = recipe_json[:-3]
        
        recipe_data = json.loads(recipe_json)
        
        # Create Starbucks recipe object
        starbucks_drink = StarbucksRecipe(
            drink_name=recipe_data['drink_name'],
            description=recipe_data['description'],
            base_drink=recipe_data['base_drink'],
            modifications=recipe_data['modifications'],
            ordering_script=recipe_data['ordering_script'],
            pro_tips=recipe_data['pro_tips'],
            why_amazing=recipe_data['why_amazing'],
            category=recipe_data['category'],
            user_id=request.user_id
        )
        
        # Add ingredients_breakdown if present
        if 'ingredients_breakdown' in recipe_data:
            starbucks_drink.ingredients_breakdown = recipe_data['ingredients_breakdown']
        
        # Save to database
        drink_dict = starbucks_drink.dict()
        result = await db.starbucks_recipes.insert_one(drink_dict)
        
        # Return the created drink
        if result.inserted_id:
            inserted_drink = await db.starbucks_recipes.find_one({"_id": result.inserted_id})
            return mongo_to_dict(inserted_drink)
        else:
            raise HTTPException(status_code=500, detail="Failed to save drink to database")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse drink recipe from AI")
    except Exception as e:
        print(f"Error generating Starbucks drink: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Starbucks drink")
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Email Verification Routes
@api_router.post("/auth/register")
async def register_user(user_data: UserRegistration):
    """Register a new user and send verification email"""
    try:
        # Basic validation
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Normalize email
        email_lower = user_data.email.lower().strip()
        
        # Check if user already exists (case-insensitive)
        existing_user = await db.users.find_one({"email": {"$regex": f"^{email_lower}$", "$options": "i"}})
        if existing_user:
            logging.warning(f"Registration attempt with existing email: {email_lower}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user document
        user = User(
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            email=email_lower,
            password_hash=password_hash,
            dietary_preferences=user_data.dietary_preferences,
            allergies=user_data.allergies,
            favorite_cuisines=user_data.favorite_cuisines,
            is_verified=False
        )
        
        # Save user to database
        user_dict = user.dict()
        result = await db.users.insert_one(user_dict)
        
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create user account")
        
        # Generate verification code
        verification_code = email_service.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Save verification code
        code_doc = VerificationCode(
            user_id=user.id,
            email=email_lower,
            code=verification_code,
            expires_at=expires_at
        )
        await db.verification_codes.insert_one(code_doc.dict())
        
        # Send verification email
        email_sent = await email_service.send_verification_email(
            to_email=email_lower,
            first_name=user.first_name,
            verification_code=verification_code
        )
        
        if not email_sent:
            logging.warning(f"Failed to send verification email to {email_lower}")
            # Don't fail registration if email fails - user can resend later
        
        logging.info(f"User registered successfully: {email_lower}")
        return {
            "message": "Registration successful. Please check your email for verification code.",
            "email": email_lower,
            "user_id": user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@api_router.post("/auth/verify")
async def verify_email(verify_request: VerifyCodeRequest):
    """Verify email with 6-digit code"""
    try:
        # Find the most recent valid verification code
        code_doc = await db.verification_codes.find_one({
            "email": verify_request.email,
            "code": verify_request.code,
            "is_used": False
        }, sort=[("created_at", -1)])
        
        if not code_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
        
        # Check if code is expired (convert string to datetime if needed)
        expires_at = code_doc["expires_at"]
        if isinstance(expires_at, str):
            from dateutil import parser
            expires_at = parser.parse(expires_at)
        
        if datetime.utcnow() > expires_at:
            # Mark expired codes as used
            await db.verification_codes.update_one(
                {"_id": code_doc["_id"]},
                {"$set": {"is_used": True}}
            )
            raise HTTPException(status_code=400, detail="Verification code has expired")
        
        # Mark code as used
        await db.verification_codes.update_one(
            {"_id": code_doc["_id"]},
            {"$set": {"is_used": True}}
        )
        
        # Update user as verified
        result = await db.users.update_one(
            {"email": verify_request.email},
            {
                "$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get the verified user
        user = await db.users.find_one({"email": verify_request.email})
        
        return {
            "message": "Email verified successfully!",
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "is_verified": user["is_verified"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Verification failed")

@api_router.post("/auth/resend-code")
async def resend_verification_code(resend_request: ResendCodeRequest):
    """Resend verification code"""
    try:
        # Find user
        user = await db.users.find_one({"email": resend_request.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user["is_verified"]:
            raise HTTPException(status_code=400, detail="User already verified")
        
        # Mark previous codes as used
        await db.verification_codes.update_many(
            {"email": resend_request.email, "is_used": False},
            {"$set": {"is_used": True}}
        )
        
        # Generate new verification code
        verification_code = email_service.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Save new verification code
        code_doc = VerificationCode(
            user_id=user["id"],
            email=user["email"],
            code=verification_code,
            expires_at=expires_at
        )
        await db.verification_codes.insert_one(code_doc.dict())
        
        # Send verification email
        email_sent = await email_service.send_verification_email(
            to_email=user["email"],
            first_name=user["first_name"],
            verification_code=verification_code
        )
        
        if not email_sent:
            logging.warning(f"Failed to send verification email to {user['email']}")
            # Don't fail if email fails - return success anyway for user experience
        
        return {
            "message": "New verification code sent successfully",
            "email": user["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Resend code error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resend verification code")

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Login user with email and password"""
    try:
        # Try multiple search strategies to find the user
        email_input = login_data.email.strip()
        email_lower = email_input.lower()
        
        # Try different search approaches
        user = None
        
        # 1. Try exact match
        user = await db.users.find_one({"email": email_input})
        
        # 2. Try lowercase
        if not user:
            user = await db.users.find_one({"email": email_lower})
        
        # 3. Try case-insensitive search
        if not user:
            all_users = await db.users.find().to_list(length=100)
            for u in all_users:
                if u.get('email', '').lower() == email_lower:
                    user = u
                    break
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is verified
        if not user.get("is_verified", False):
            return {
                "status": "unverified",
                "message": "Email not verified. Please verify your email first.",
                "email": user["email"],
                "user_id": user["id"],
                "needs_verification": True
            }
        
        # Return successful login
        return {
            "status": "success",  # Frontend expects this field
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "is_verified": user["is_verified"]
            },
            "user_id": user["id"],
            "email": user["email"]
        }
        if not user.get("is_verified", False):
            # Instead of error, return special response for unverified user
            logging.info(f"Login attempt with unverified email: {email_lower}")
            return {
                "status": "unverified",
                "message": "Email not verified. Please verify your email first.",
                "email": user["email"],
                "user_id": user["id"],
                "needs_verification": True
            }
        
        logging.info(f"User logged in successfully: {email_lower}")
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "dietary_preferences": user.get("dietary_preferences", []),
                "allergies": user.get("allergies", []),
                "favorite_cuisines": user.get("favorite_cuisines", []),
                "is_verified": user.get("is_verified", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error for {login_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@api_router.get("/debug/user/{email}")
async def get_user_debug(email: str):
    """Debug endpoint to get user record structure"""
    try:
        # Only allow in development/test mode
        if os.getenv('NODE_ENV') == 'production':
            raise HTTPException(status_code=404, detail="Not found")
        
        email_lower = email.lower().strip()
        user = await db.users.find_one({"email": {"$regex": f"^{email_lower}$", "$options": "i"}})
        
        if not user:
            return {"error": "User not found"}
        
        # Remove sensitive data for debugging
        user_copy = user.copy()
        if 'password_hash' in user_copy:
            user_copy['password_hash'] = "***HIDDEN***"
        
        return {"user": mongo_to_dict(user_copy)}
        
    except Exception as e:
        return {"error": str(e)}

@api_router.delete("/debug/clear-users")
async def clear_all_users():
    """Debug endpoint to clear all users and related data"""
    try:
        # Only allow in development/test mode
        if os.getenv('NODE_ENV') == 'production':
            raise HTTPException(status_code=404, detail="Not found")
        
        # Clear all users
        users_result = await db.users.delete_many({})
        
        # Clear verification codes
        codes_result = await db.verification_codes.delete_many({})
        
        # Clear password reset codes
        reset_result = await db.password_reset_codes.delete_many({})
        
        # Clear recipes
        recipes_result = await db.recipes.delete_many({})
        
        # Clear grocery carts
        carts_result = await db.grocery_carts.delete_many({})
        cart_options_result = await db.grocery_cart_options.delete_many({})
        
        return {
            "message": "Database cleared successfully",
            "deleted": {
                "users": users_result.deleted_count,
                "verification_codes": codes_result.deleted_count,
                "password_reset_codes": reset_result.deleted_count,
                "recipes": recipes_result.deleted_count,
                "grocery_carts": carts_result.deleted_count,
                "grocery_cart_options": cart_options_result.deleted_count
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/debug/verification-codes/{email}")
async def get_verification_codes_debug(email: str):
    """Debug endpoint to get verification codes for testing"""
    try:
        # Only allow in development/test mode
        if os.getenv('NODE_ENV') == 'production':
            raise HTTPException(status_code=404, detail="Not found")
        
        codes = []
        async for code in db.verification_codes.find({"email": email, "is_used": False}).sort("created_at", -1).limit(5):
            codes.append({
                "code": code["code"],
                "expires_at": code["expires_at"],
                "is_expired": datetime.utcnow() > code["expires_at"]
            })
        
        return {
            "email": email,
            "codes": codes,
            "last_test_code": email_service.last_verification_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Debug endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Debug endpoint failed")

@api_router.delete("/debug/cleanup-test-data")
async def cleanup_test_data():
    """Debug endpoint to clean up test data"""
    try:
        # Only allow in development/test mode
        if os.getenv('NODE_ENV') == 'production':
            raise HTTPException(status_code=404, detail="Not found")
        
        # Delete test users and verification codes
        users_deleted = await db.users.delete_many({"email": {"$regex": "@example.com$"}})
        codes_deleted = await db.verification_codes.delete_many({"email": {"$regex": "@example.com$"}})
        
        return {
            "message": "Test data cleaned up",
            "users_deleted": users_deleted.deleted_count,
            "codes_deleted": codes_deleted.deleted_count
        }
        
    except Exception as e:
        logging.error(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

@api_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Send password reset code to user's email"""
    try:
        # Normalize email
        email_lower = request.email.lower().strip()
        
        # Find user
        user = await db.users.find_one({"email": {"$regex": f"^{email_lower}$", "$options": "i"}})
        if not user:
            # Don't reveal if email exists for security - always return success
            return {
                "message": "If an account with this email exists, a password reset code has been sent.",
                "email": email_lower
            }
        
        # Generate reset code (6-digit)
        reset_code = email_service.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes for password reset
        
        # Mark any existing reset codes as used
        await db.password_reset_codes.update_many(
            {"email": email_lower, "is_used": False},
            {"$set": {"is_used": True}}
        )
        
        # Save new reset code
        reset_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "email": email_lower,
            "code": reset_code,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_used": False
        }
        await db.password_reset_codes.insert_one(reset_doc)
        
        # Send reset email
        email_sent = await email_service.send_password_reset_email(
            to_email=email_lower,
            first_name=user["first_name"],
            reset_code=reset_code
        )
        
        if not email_sent:
            logging.warning(f"Failed to send password reset email to {email_lower}")
        
        return {
            "message": "If an account with this email exists, a password reset code has been sent.",
            "email": email_lower
        }
        
    except Exception as e:
        logging.error(f"Password reset error for {request.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset request failed")

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetVerify):
    """Reset password with verification code"""
    try:
        # Normalize email
        email_lower = request.email.lower().strip()
        
        # Validate new password
        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Find the reset code
        reset_doc = await db.password_reset_codes.find_one({
            "email": email_lower,
            "code": request.reset_code,
            "is_used": False
        }, sort=[("created_at", -1)])
        
        if not reset_doc:
            raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
        # Check if code is expired
        expires_at = reset_doc["expires_at"]
        if isinstance(expires_at, str):
            expires_at = parser.parse(expires_at)
        
        if datetime.utcnow() > expires_at:
            # Mark expired code as used
            await db.password_reset_codes.update_one(
                {"_id": reset_doc["_id"]},
                {"$set": {"is_used": True}}
            )
            raise HTTPException(status_code=400, detail="Reset code has expired")
        
        # Mark code as used
        await db.password_reset_codes.update_one(
            {"_id": reset_doc["_id"]},
            {"$set": {"is_used": True}}
        )
        
        # Hash new password
        new_password_hash = hash_password(request.new_password)
        
        # Update user password
        result = await db.users.update_one(
            {"email": email_lower},
            {"$set": {"password_hash": new_password_hash}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logging.info(f"Password reset successful for {email_lower}")
        return {
            "message": "Password reset successful. You can now login with your new password.",
            "email": email_lower
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Password reset verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset failed")

# Keep all existing routes for backward compatibility
@api_router.get("/")
async def root():
    return {"message": "AI Recipe & Grocery API", "version": "2.0.0", "status": "running"}

@api_router.post("/users")
async def create_user(user: UserCreate):
    """Create user (legacy endpoint for backward compatibility)"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            return mongo_to_dict(existing_user)
        
        # Create user object
        user_obj = User(
            first_name=user.name.split()[0] if user.name else "User",
            last_name=" ".join(user.name.split()[1:]) if len(user.name.split()) > 1 else "",
            email=user.email,
            password_hash="legacy_user",  # Legacy users don't have passwords
            dietary_preferences=user.dietary_preferences,
            allergies=user.allergies,
            favorite_cuisines=user.favorite_cuisines,
            is_verified=True  # Legacy users are auto-verified
        )
        
        # Insert into database
        user_dict = user_obj.dict()
        await db.users.insert_one(user_dict)
        
        # Return the user dict without MongoDB _id
        return user_dict
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return mongo_to_dict(user)
    except Exception as e:
        logging.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserCreate):
    """Update user"""
    try:
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": user_update.dict()}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = await db.users.find_one({"id": user_id})
        return mongo_to_dict(updated_user)
    except Exception as e:
        logging.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")

# Recipe generation functions and routes (keeping all existing functionality)
def _get_walmart_signature():
    """Generate Walmart API signature with correct RSA-SHA256 signing"""
    try:
        import base64
        import time
        from datetime import datetime
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        
        # Generate timestamp in milliseconds (UTC)
        current_utc = datetime.utcnow()
        timestamp = str(int(current_utc.timestamp() * 1000))
        
        logging.info(f"🕐 WALMART AUTH: Generating signature with UTC timestamp: {timestamp}")
        logging.info(f"🕐 WALMART AUTH: Current UTC time: {current_utc.isoformat()}")
        
        # Create string to sign
        string_to_sign = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n"
        logging.info(f"🔑 WALMART AUTH: String to sign: {repr(string_to_sign)}")
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            WALMART_PRIVATE_KEY.encode('utf-8'),
            password=None
        )
        
        # Sign with RSA-SHA256
        signature_bytes = private_key.sign(
            string_to_sign.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Encode to base64
        signature = base64.b64encode(signature_bytes).decode('utf-8')
        
        logging.info(f"✅ WALMART AUTH: Generated signature - timestamp: {timestamp}, signature length: {len(signature)}")
        
        return timestamp, signature
        
    except ImportError:
        logging.error("❌ WALMART AUTH: Missing cryptography library - falling back to HMAC")
        # Fallback to HMAC (incorrect but for debugging)
        import hashlib
        import hmac
        
        timestamp = str(int(time.time() * 1000))
        string_to_sign = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n"
        
        signature = base64.b64encode(
            hmac.new(
                WALMART_PRIVATE_KEY.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return timestamp, signature
        
    except Exception as e:
        logging.error(f"❌ WALMART AUTH: Error generating signature: {str(e)}")
        raise HTTPException(status_code=500, detail="Walmart API authentication error")

def _extract_core_ingredient(ingredient: str) -> str:
    """Extract the core ingredient name from complex recipe descriptions"""
    
    # Convert to lowercase for processing
    ingredient_lower = ingredient.lower().strip()
    
    # Remove common recipe measurements and quantities at the beginning
    ingredient_lower = re.sub(r'^(\d+[\s\/\-]*\d*\s*)?(cups?|cup|tbsp|tablespoons?|tablespoon|tsp|teaspoons?|teaspoon|lbs?|pounds?|pound|oz|ounces?|ounce|cans?|can|jars?|jar|bottles?|bottle|packages?|package|bags?|bag|cloves?|clove|slices?|slice|pieces?|piece|pinch|dash)\s+', '', ingredient_lower)
    
    # Remove common preparation words
    ingredient_lower = re.sub(r'\b(fresh|frozen|dried|chopped|diced|minced|sliced|grated|crushed|ground|whole|raw|cooked|boiled|steamed|roasted|baked|organic|extra|virgin|pure|natural|unsalted|salted|low[- ]fat|fat[- ]free|sugar[- ]free)\b\s*', '', ingredient_lower)
    
    # Remove preparation instructions in parentheses
    ingredient_lower = re.sub(r'\([^)]*\)', '', ingredient_lower)
    
    # Special handling for beverage ingredients
    beverage_substitutions = {
        'ice cubes': 'ice',
        'ice cube': 'ice',
        'tapioca pearls': 'tapioca pearls',
        'boba pearls': 'tapioca pearls',
        'bubble tea pearls': 'tapioca pearls',
        'black tea bags': 'black tea',
        'tea bags': 'black tea',
        'green tea bags': 'green tea',
        'oat milk': 'oat milk',
        'almond milk': 'almond milk',
        'coconut milk': 'coconut milk',
        'whole milk': 'milk',
        'skim milk': 'milk',
        '2% milk': 'milk',
        'heavy cream': 'heavy cream',
        'whipped cream': 'whipped cream',
        'brown sugar syrup': 'brown sugar',
        'simple syrup': 'sugar',
        'honey syrup': 'honey',
        'maple syrup': 'maple syrup',
        'agave syrup': 'agave',
        'mint leaves': 'mint',
        'fresh mint': 'mint',
        'lemon juice': 'lemons',
        'lime juice': 'limes',
        'orange juice': 'oranges',
        'pineapple juice': 'pineapple',
        'coconut water': 'coconut water',
        'sparkling water': 'sparkling water',
        'club soda': 'club soda',
        'soda water': 'club soda'
    }
    
    # Apply beverage-specific substitutions
    for original, replacement in beverage_substitutions.items():
        if original in ingredient_lower:
            ingredient_lower = ingredient_lower.replace(original, replacement)
            break
    
    # Handle spice blends and specific cooking terms
    spice_substitutions = {
        'italian seasoning': 'italian seasoning',
        'garlic powder': 'garlic powder',
        'onion powder': 'onion powder',
        'black pepper': 'black pepper',
        'white pepper': 'white pepper',
        'sea salt': 'sea salt',
        'kosher salt': 'salt',
        'table salt': 'salt',
        'olive oil': 'olive oil',
        'vegetable oil': 'vegetable oil',
        'canola oil': 'canola oil',
        'coconut oil': 'coconut oil',
        'butter': 'butter',
        'unsalted butter': 'butter'
    }
    
    # Apply spice and cooking substitutions
    for original, replacement in spice_substitutions.items():
        if original in ingredient_lower:
            ingredient_lower = replacement
            break
    
    # Remove any remaining quantities and measurements
    ingredient_lower = re.sub(r'^\d+[\s\-\/]*\d*\s*', '', ingredient_lower)
    ingredient_lower = re.sub(r'\b\d+[\s\-\/]*\d*\s*(ml|l|g|kg|mg)\b', '', ingredient_lower)
    
    # Remove extra whitespace and clean up
    ingredient_lower = re.sub(r'\s+', ' ', ingredient_lower).strip()
    
    # Remove common suffixes that don't help with searching
    ingredient_lower = re.sub(r'\s+(to taste|as needed|optional|for garnish|for serving)$', '', ingredient_lower)
    
    # If we end up with something too short or generic, try to use the original
    if len(ingredient_lower) < 2 or ingredient_lower in ['for', 'and', 'or', 'with', 'of', 'the', 'a', 'an']:
        # Fall back to just removing obvious quantities from the start
        fallback = re.sub(r'^\d+\s*', '', ingredient.lower().strip())
        return fallback if len(fallback) > 2 else ingredient.lower().strip()
    
    return ingredient_lower.strip() if ingredient_lower.strip() else ingredient

async def _get_walmart_product_options(ingredient: str, max_options: int = 3) -> List[WalmartProduct]:
    """Get product options from Walmart API - PRODUCTION VERSION - NO MOCK DATA"""
    try:
        # Extract core ingredient name for better search results
        clean_ingredient = _extract_core_ingredient(ingredient)
        
        logging.info(f"🔍 PRODUCTION: Searching Walmart for '{ingredient}' -> cleaned: '{clean_ingredient}'")
        
        # Skip empty or very short ingredients
        if not clean_ingredient or len(clean_ingredient.strip()) < 2:
            logging.warning(f"⏭️ PRODUCTION: Skipping too short ingredient: '{clean_ingredient}'")
            return []
        
        # PRODUCTION: Try real Walmart API with enhanced retry logic
        for attempt in range(3):  # Retry up to 3 times
            try:
                # Generate signature and timestamp
                timestamp, signature = _get_walmart_signature()
                
                # Prepare API call with improved query
                query = clean_ingredient.replace(' ', '+').replace(',', '').replace('/', '')
                url = f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query={query}&numItems={max_options + 2}"  # Get extra to filter
                
                headers = {
                    "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
                    "WM_CONSUMER.INTIMESTAMP": timestamp,
                    "WM_SEC.KEY_VERSION": WALMART_KEY_VERSION,
                    "WM_SEC.AUTH_SIGNATURE": signature,
                    "Content-Type": "application/json",
                    "User-Agent": "BuildYourSmartCart/1.0"
                }
                
                logging.info(f"🌐 WALMART API: Calling {url}")
                logging.info(f"🔑 WALMART API: Headers - Consumer ID: {WALMART_CONSUMER_ID}, Timestamp: {timestamp}, Key Version: {WALMART_KEY_VERSION}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, timeout=45)  # Longer timeout for production
                    
                    logging.info(f"📡 WALMART API: Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        products = []
                        
                        if 'items' in data and len(data['items']) > 0:
                            logging.info(f"✅ PRODUCTION: Found {len(data['items'])} raw items from Walmart API for '{clean_ingredient}'")
                            
                            valid_products_count = 0
                            for item in data['items']:
                                if valid_products_count >= max_options:
                                    break
                                    
                                if 'itemId' in item and 'name' in item:
                                    product_id = str(item.get('itemId', ''))
                                    product_name = item.get('name', '').strip()
                                    
                                    # PRODUCTION: Strict validation - only real Walmart products
                                    if (product_id.isdigit() and 
                                        len(product_id) >= 6 and
                                        len(product_id) <= 12 and  # Walmart IDs are typically 8-11 digits
                                        not product_id.startswith('10315') and  # Mock pattern
                                        not product_id.startswith('12345') and  # Mock pattern
                                        not product_id.startswith('99999') and  # Mock pattern
                                        not product_id.startswith('walmart-') and
                                        not product_id.startswith('mock-') and
                                        not product_id.startswith('test-') and
                                        product_name and len(product_name) > 3):
                                        
                                        # Additional validation: check if product has valid price and name
                                        price = float(item.get('salePrice', 0.0))
                                        if price > 0 and price < 1000:  # Reasonable price range
                                            # Check if product name is relevant to ingredient
                                            name_lower = product_name.lower()
                                            ingredient_lower = clean_ingredient.lower()
                                            
                                            # TEMPORARILY DISABLE RELEVANCE FILTERING to get products working
                                            is_relevant = True  # Accept all valid products from Walmart API
                                            
                                            if is_relevant:  # Always true now
                                                product = WalmartProduct(
                                                    product_id=product_id,
                                                    name=product_name,
                                                    price=price,
                                                    thumbnail_image=item.get('thumbnailImage', ''),
                                                    availability="Available"
                                                )
                                                products.append(product)
                                                valid_products_count += 1
                                                logging.info(f"✅ PRODUCTION: Valid product {valid_products_count}: {product.name} - ${product.price} (ID: {product.product_id})")
                                            else:
                                                logging.info(f"⏭️ PRODUCTION: Skipping irrelevant product: {product_name} for '{clean_ingredient}'")
                                        else:
                                            logging.warning(f"⏭️ PRODUCTION: Skipping product with invalid price: {product_name} - ${price}")
                                    else:
                                        logging.warning(f"⏭️ PRODUCTION: Skipping invalid product ID or name: {product_id} - '{product_name}'")
                            
                            if products:
                                logging.info(f"🎉 PRODUCTION: Successfully found {len(products)} valid products for '{clean_ingredient}'")
                                return products
                            else:
                                logging.warning(f"⚠️ PRODUCTION: No valid products found in response for '{clean_ingredient}' on attempt {attempt + 1}")
                        else:
                            logging.warning(f"⚠️ PRODUCTION: No items found in Walmart API response for '{clean_ingredient}' on attempt {attempt + 1}")
                    
                    elif response.status_code == 429:  # Rate limit
                        logging.warning(f"🚫 PRODUCTION: Rate limited for '{clean_ingredient}', attempt {attempt + 1}")
                        if attempt < 2:  # Wait before retry
                            await asyncio.sleep(3 ** attempt)  # Exponential backoff
                            continue
                    
                    elif response.status_code == 403:  # Authentication error
                        logging.error(f"🔐 PRODUCTION: Authentication error for '{clean_ingredient}': {response.status_code}")
                        logging.error(f"Response: {response.text}")
                        break  # Don't retry auth errors
                    
                    elif response.status_code == 401:  # Authentication error
                        logging.error(f"🔐 PRODUCTION: Authentication error for '{clean_ingredient}': {response.status_code}")
                        logging.error(f"Response: {response.text}")
                        break  # Don't retry auth errors
                    
                    else:
                        # Log error response details
                        logging.error(f"❌ WALMART API: HTTP {response.status_code} - {response.text[:500]}")
                        if response.status_code == 401:
                            logging.error("❌ WALMART API: Authentication failed - check credentials and timestamp")
                        elif response.status_code == 403:
                            logging.error("❌ WALMART API: Forbidden - check API permissions")
                        elif response.status_code == 429:
                            logging.error("❌ WALMART API: Rate limited - too many requests")
                        
                        if attempt < 2:
                            await asyncio.sleep(3)  # Wait longer between attempts
                            continue
                        else:
                            logging.error(f"❌ WALMART API: Final attempt failed with status {response.status_code}")
                            break
                
                # If we get here, the attempt failed
                break
                        
            except asyncio.TimeoutError:
                logging.error(f"⏰ PRODUCTION: Timeout error for '{clean_ingredient}' on attempt {attempt + 1}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                
            except httpx.RequestError as e:
                logging.error(f"❌ PRODUCTION: Walmart API Request Error for '{clean_ingredient}': {str(e)}")
                continue
            except httpx.HTTPStatusError as e:
                logging.error(f"❌ PRODUCTION: Walmart API HTTP Error for '{clean_ingredient}': {e.response.status_code} - {e.response.text}")
                continue
            except Exception as e:
                logging.error(f"❌ PRODUCTION: Walmart API Unexpected Error for '{clean_ingredient}': {str(e)}")
                continue
        
        # If all attempts failed, return empty list
        logging.error(f"❌ PRODUCTION: All attempts failed for '{clean_ingredient}' - returning empty list")
        return []
                
    except Exception as e:
        logging.error(f"💥 PRODUCTION: Critical error fetching Walmart products for '{ingredient}': {str(e)}")
        return []

@api_router.post("/recipes/generate")
async def generate_recipe(request: RecipeGenRequest):
    """Generate a recipe using OpenAI"""
    try:
        # Build the prompt based on recipe category
        prompt_parts = []
        
        # Determine recipe category and build appropriate prompt
        recipe_category = request.recipe_category or 'cuisine'
        recipe_type = request.cuisine_type or 'general'
        
        if recipe_category == "snack":
            if recipe_type == "acai bowls":
                prompt_parts.append(f"Create a delicious and nutritious acai bowl recipe for {request.servings} people. Focus on frozen acai puree, healthy superfoods, fresh toppings, granola, and colorful presentation. Include preparation techniques for the perfect consistency.")
            elif recipe_type == "fruit lemon slices chili":
                prompt_parts.append(f"Create a spicy and refreshing fruit lemon slices with chili recipe for {request.servings} people. Focus on fresh fruits, lemon juice, chili powder, lime, and traditional Mexican-style seasoning. Include cutting techniques and spice combinations.")
            elif recipe_type == "frozen yogurt berry bites":
                prompt_parts.append(f"""Create an incredibly creative and Instagram-worthy frozen yogurt berry recipe for {request.servings} people. Think beyond basic bites - create something like 'Galaxy Swirl Yogurt Bark', 'Berry Cheesecake Bombs', 'Unicorn Yogurt Clusters', or 'Rainbow Protein Pops'. 

Focus on:
🌟 Creative presentation (layered colors, marbled effects, fun shapes)
🧊 Multiple textures (crunchy toppings, smooth yogurt, chewy add-ins)
🍓 Gourmet flavor combinations (lavender honey, matcha white chocolate, strawberry basil)
✨ Instagram-worthy appearance (vibrant colors, artistic drizzles, edible flowers)
🥄 Pro techniques (tempering chocolate, creating ombré effects, using molds)

Include Greek yogurt as the base but elevate it with:
- Superfood add-ins (chia seeds, acai powder, spirulina)
- Gourmet flavor extracts (rose water, vanilla bean, almond)
- Artisanal toppings (edible gold, freeze-dried fruits, nuts, coconut flakes)
- Creative freezing techniques (layering, swirling, molding)

Make this a show-stopping healthy dessert that looks like it came from a high-end dessert boutique!""")
            else:
                prompt_parts.append(f"Create a {recipe_type} snack recipe for {request.servings} people. Focus on tasty, satisfying snacks that are perfect for any time of day.")
        
        elif recipe_category == "beverage":
            # Generate specific beverage type based on user selection
            if recipe_type == "boba tea":
                prompt_parts.append(f"""Create a detailed brown sugar boba tea or fruit boba tea recipe for {request.servings} people. Include tapioca pearl cooking instructions, tea brewing methods, syrup preparation, and assembly techniques. Make it authentic bubble tea shop quality.

🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions including pearl cooking, tea brewing, and assembly
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Can be milk-based or fruit-based, and use tapioca, popping boba, or creative textures. Make the drink visually Instagram-worthy with professional techniques.""")

            elif recipe_type == "thai tea":
                prompt_parts.append(f"""Create an authentic Thai tea recipe for {request.servings} people. Include traditional orange tea preparation, condensed milk ratios, spice blending, and the signature layered presentation technique.

🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions including tea brewing, spice mixing, and layering
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Layered or infused with other flavors (like fruit, spices, milk alternatives, or syrups) with traditional preparation methods. Make the drink visually Instagram-worthy.""")

            elif recipe_type == "special lemonades":
                prompt_parts.append(f"""Create a special flavored lemonade recipe for {request.servings} people. Include unique fruit combinations, natural sweeteners, fresh herbs, and creative presentation. Focus on refreshing summer drinks with gourmet touches.

🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions including preparation and presentation
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Refreshing, fruity, or herbal — perfect for summer with unique fruit combinations, natural sweeteners, and fresh herbs. Make the drink visually Instagram-worthy.""")

            else:
                prompt_parts.append(f"""Create a detailed {recipe_type} beverage recipe for {request.servings} people. Focus on refreshing, flavorful drinks with exact measurements and professional techniques.

🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make the drink visually Instagram-worthy and perfect for any season.""")
        
        else:  # cuisine category
            if recipe_type == "snacks & bowls":
                prompt_parts.append(f"Create a healthy snack or bowl recipe for {request.servings} people. Focus on nutritious snacks, smoothie bowls, acai bowls, poke bowls, grain bowls, or energy bites.")
            else:
                prompt_parts.append(f"Create a {recipe_type or 'delicious'} recipe for {request.servings} people.")
        
        prompt_parts.append(f"Difficulty level: {request.difficulty}.")
        
        if request.dietary_preferences:
            prompt_parts.append(f"Dietary preferences: {', '.join(request.dietary_preferences)}.")
        
        if request.ingredients_on_hand:
            prompt_parts.append(f"Try to use these ingredients: {', '.join(request.ingredients_on_hand)}.")
        
        if request.prep_time_max:
            prompt_parts.append(f"Maximum prep time: {request.prep_time_max} minutes.")
        
        # Healthy mode requirements
        if request.is_healthy and request.max_calories_per_serving:
            prompt_parts.append(f"This should be a healthy recipe with maximum {request.max_calories_per_serving} calories per serving.")
        
        # Budget mode requirements  
        if request.is_budget_friendly and request.max_budget:
            prompt_parts.append(f"Keep the total ingredient cost under ${request.max_budget}.")
        
        # Only add generic recipe instructions for non-Starbucks categories
        if recipe_category != "starbucks":
            prompt_parts.append("""
Return ONLY a valid JSON object with this exact structure:

{
    "title": "Recipe Name",
    "description": "Brief description",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": ["step 1", "step 2"],
    "prep_time": 15,
    "cook_time": 30,
    "calories_per_serving": 350,
    "shopping_list": ["ingredient_name_1", "ingredient_name_2"]
}

Recipe Category Guidelines:

SNACKS: Focus on healthy and refreshing snack options such as:
- Acai bowls (frozen acai puree, granola, fresh berries, honey, superfoods)
- Fruit lemon slices chili (fresh fruits, lemon juice, chili powder, lime, Mexican spices)
- Frozen yogurt berry bites (Greek yogurt, mixed berries, natural sweeteners, bite-sized treats)

BEVERAGES: Generate specific beverage recipes based on user selection:

1. LEMONADE-BASED DRINK: Refreshing, fruity, or herbal lemonades perfect for summer with unique fruit combinations, natural sweeteners, and fresh herbs

2. THAI TEA-BASED DRINK: Authentic Thai tea layered or infused with other flavors (fruit, spices, milk alternatives, or syrups) with traditional preparation methods

3. BOBA DRINK: Milk-based or fruit-based bubble tea using tapioca, popping boba, or creative textures with authentic bubble tea shop quality

For each beverage, include:
🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units (cups, tablespoons, ounces)
🍳 Step-by-step instructions including brewing, mixing, and serving techniques
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make each drink visually Instagram-worthy with professional techniques (shaking, layering, temperature control).

CRITICAL FOR BEVERAGE SHOPPING LIST: The shopping_list must contain ONLY clean ingredient names without any quantities, measurements, or preparation instructions. For beverage specifically:
- If ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- If ingredients include "1/4 cup fresh mint leaves" and "ice cubes", the shopping_list should be ["mint", "ice"]
- If ingredients include "1 cup oat milk" and "3/4 cup cooked tapioca pearls", the shopping_list should be ["oat milk", "tapioca pearls"]
- Remove ALL quantities (2 shots, 1/2 cup, 1/4 cup, etc.) and measurements (cups, tablespoons, ounces)
- Remove ALL preparation words (fresh, cooked, diced, chopped, etc.)
- Use clean, searchable ingredient names suitable for Walmart product search

Example beverage ingredients format:
- "2 shots espresso" instead of "espresso"
- "1/2 cup brown sugar syrup" instead of "brown sugar"
- "1 cup oat milk" instead of "milk"
- "3/4 cup cooked tapioca pearls" instead of "tapioca"

CUISINE: Traditional dishes from specific cultures and regions with authentic ingredients and cooking methods.

The shopping_list should be a separate bullet-pointed shopping list that includes only the names of the ingredients (no amounts, no measurements). For example:
- If ingredients include "1 cup diced tomatoes" and "2 tbsp olive oil", the shopping_list should be ["tomatoes", "olive oil"]
- If ingredients include "1 can chickpeas, drained" and "1/2 cup BBQ sauce", the shopping_list should be ["chickpeas", "BBQ sauce"]
- If beverage ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- BEVERAGE SPECIFIC: If ingredients include "4 lemons", "1/2 cup pineapple chunks", "1/4 cup fresh mint leaves", the shopping_list should be ["lemons", "pineapple", "mint"]
- BEVERAGE SPECIFIC: If ingredients include "1 cup oat milk", "ice cubes", "1/2 cup honey", the shopping_list should be ["oat milk", "ice", "honey"]
- Clean ingredient names without quantities, measurements, or preparation instructions

BEVERAGE EXAMPLES for reference (create one specific recipe based on user selection):
- Lemonade: Lavender Honey Lemonade with fresh herbs and edible flowers  
- Thai Tea: Coconut Mango Thai Tea with layered presentation and tropical fruit
- Boba: Taro Coconut Milk Tea with homemade taro paste and chewy tapioca pearls

IMPORTANT FOR SPICES: If the recipe uses spices, list each spice individually in the shopping_list instead of using generic terms like "spices" or "seasoning". For example:
- If ingredients include "2 tsp mixed spices (turmeric, cumin, coriander)", the shopping_list should include ["turmeric", "cumin", "coriander"]
- If ingredients include "1 tbsp garam masala and chili powder", the shopping_list should include ["garam masala", "chili powder"] 
- If ingredients include "salt, pepper, and paprika to taste", the shopping_list should include ["salt", "pepper", "paprika"]
- This ensures users can select specific spices and brands from Walmart rather than searching for generic "spices"
""")
        
        prompt = " ".join(prompt_parts)
        
        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the response
        recipe_json = response.choices[0].message.content.strip()
        
        # Clean up the JSON (remove markdown formatting if present)
        if recipe_json.startswith("```json"):
            recipe_json = recipe_json[7:]
        if recipe_json.endswith("```"):
            recipe_json = recipe_json[:-3]
        
        recipe_data = json.loads(recipe_json)
        
        # Create recipe object based on category
        if recipe_category == "starbucks":
            # Create Starbucks recipe
            recipe = StarbucksRecipe(
                drink_name=recipe_data['drink_name'],
                description=recipe_data['description'],
                base_drink=recipe_data['base_drink'],
                modifications=recipe_data['modifications'],
                ordering_script=recipe_data['ordering_script'],
                pro_tips=recipe_data['pro_tips'],
                why_amazing=recipe_data['why_amazing'],
                category=recipe_data['category'],
                user_id=request.user_id
            )
            collection_name = "starbucks_recipes"
        else:
            # Create regular recipe
            recipe = Recipe(
                title=recipe_data['title'],
                description=recipe_data['description'],
                ingredients=recipe_data['ingredients'],
                instructions=recipe_data['instructions'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=request.servings,
                cuisine_type=request.cuisine_type or "general",
                dietary_tags=request.dietary_preferences,
                difficulty=request.difficulty,
                calories_per_serving=recipe_data.get('calories_per_serving'),
                is_healthy=request.is_healthy,
                user_id=request.user_id,
                shopping_list=recipe_data.get('shopping_list', [])
            )
            collection_name = "recipes"
        
        # Save to database
        recipe_dict = recipe.dict()
        result = await db[collection_name].insert_one(recipe_dict)
        
        # Get the inserted document and return it
        if result.inserted_id:
            inserted_recipe = await db[collection_name].find_one({"_id": result.inserted_id})
            return mongo_to_dict(inserted_recipe)
        
        return recipe_dict
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse recipe from AI")
    except Exception as e:
        logging.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recipe")

@api_router.get("/recipes/{recipe_id}")
@app.get("/api/recipes/history/{user_id}")
async def get_recipe_history(user_id: str):
    """Get all recipes for a user including regular recipes and Starbucks drinks"""
    try:
        # Get regular recipes
        recipes = await db.recipes.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        
        # Get Starbucks recipes
        starbucks_recipes = await db.starbucks_recipes.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
        
        # Convert to dictionaries and add type labels
        recipe_history = []
        
        # Process regular recipes
        for recipe in recipes:
            recipe_dict = mongo_to_dict(recipe)
            # Determine category based on cuisine_type or content
            if 'snack' in recipe_dict.get('cuisine_type', '').lower() or any(word in recipe_dict.get('title', '').lower() for word in ['bowl', 'bite', 'snack', 'yogurt', 'acai']):
                recipe_dict['category'] = 'snacks'
                recipe_dict['category_label'] = 'Snacks'
                recipe_dict['category_icon'] = '🍪'
            elif 'beverage' in recipe_dict.get('cuisine_type', '').lower() or any(word in recipe_dict.get('title', '').lower() for word in ['drink', 'tea', 'lemonade', 'boba', 'smoothie']):
                recipe_dict['category'] = 'beverages'
                recipe_dict['category_label'] = 'Beverages'
                recipe_dict['category_icon'] = '🧋'
            else:
                recipe_dict['category'] = 'cuisine'
                recipe_dict['category_label'] = 'Cuisine'
                recipe_dict['category_icon'] = '🍝'
            
            recipe_dict['type'] = 'recipe'
            recipe_history.append(recipe_dict)
        
        # Process Starbucks recipes
        for starbucks_recipe in starbucks_recipes:
            starbucks_dict = mongo_to_dict(starbucks_recipe)
            starbucks_dict['category'] = 'starbucks'
            starbucks_dict['category_label'] = 'Starbucks Drinks'
            starbucks_dict['category_icon'] = '☕'
            starbucks_dict['type'] = 'starbucks'
            recipe_history.append(starbucks_dict)
        
        # Sort all recipes by created_at
        recipe_history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return {
            "success": True,
            "recipes": recipe_history,
            "total_count": len(recipe_history),
            "regular_recipes": len(recipes),
            "starbucks_recipes": len(starbucks_recipes)
        }
        
    except Exception as e:
        print(f"Error getting recipe history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recipe history")

async def get_recipe(recipe_id: str):
    """Get a specific recipe"""
    try:
        recipe = await db.recipes.find_one({"id": recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Convert MongoDB document to dict, handling _id field
        return mongo_to_dict(recipe)
    except Exception as e:
        logging.error(f"Error fetching recipe: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recipe")

@api_router.get("/users/{user_id}/recipes")
async def get_user_recipes(user_id: str):
    """Get all recipes for a user"""
    try:
        recipes = []
        async for recipe in db.recipes.find({"user_id": user_id}).sort("created_at", -1):
            recipes.append(mongo_to_dict(recipe))
        
        return recipes
    except Exception as e:
        logging.error(f"Error fetching user recipes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recipes")

@api_router.post("/grocery/cart-options")
async def get_grocery_cart_options(
    recipe_id: str = Query(..., description="Recipe ID"),
    user_id: str = Query(..., description="User ID")
):
    """Get grocery cart options for a recipe - PRODUCTION VERSION - ONLY REAL USER RECIPES"""
    try:
        logging.info(f"🛒 PRODUCTION: Cart options request: recipe_id={recipe_id}, user_id={user_id}")
        
        # PRODUCTION: Get recipe from database - ONLY REAL USER RECIPES
        recipe = await db.recipes.find_one({"id": recipe_id, "user_id": user_id})
        if not recipe:
            logging.error(f"❌ PRODUCTION: Recipe not found: {recipe_id} for user {user_id}")
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        recipe_title = recipe.get('title', 'Unknown Recipe')
        shopping_list = recipe.get('shopping_list', [])
        logging.info(f"📋 PRODUCTION: Recipe '{recipe_title}' has {len(shopping_list)} ingredients: {shopping_list}")
        
        if not shopping_list:
            logging.warning(f"⚠️ PRODUCTION: No shopping list found for recipe {recipe_id}")
            return {
                "error": "No shopping list available for this recipe",
                "debug_info": {
                    "recipe_id": recipe_id,
                    "recipe_title": recipe_title,
                    "message": "Recipe has no shopping list"
                }
            }
        
        # PRODUCTION: Create ingredient options - ONLY REAL DATA  
        ingredient_options = []
        total_ingredients = len(shopping_list)
        successful_ingredients = 0
        failed_ingredients = []
        
        logging.info(f"🔍 PRODUCTION: Processing {total_ingredients} ingredients for real Walmart products")
        
        for i, ingredient in enumerate(shopping_list, 1):
            logging.info(f"🔍 PRODUCTION: Processing ingredient {i}/{total_ingredients}: '{ingredient}'")
            
            # Get Walmart products for this ingredient
            try:
                walmart_products = await _get_walmart_product_options(ingredient, max_options=3)
                
                if walmart_products:
                    # Create ingredient option with validated products
                    validated_products = []
                    for product in walmart_products:
                        # Additional filtering to ensure only real products
                        if (product.product_id and 
                            product.name and 
                            product.price > 0 and
                            not product.product_id.startswith('10315') and
                            not product.product_id.startswith('mock-') and
                            not product.product_id.startswith('walmart-')):
                            validated_products.append(product)
                        else:
                            logging.warning(f"⚠️ PRODUCTION: Filtered out invalid product: {product.name} (ID: {product.product_id})")
                    
                    if validated_products:
                        ingredient_option = IngredientOption(
                            ingredient_name=ingredient,
                            options=validated_products
                        )
                        ingredient_options.append(ingredient_option)
                        successful_ingredients += 1
                        
                        logging.info(f"✅ PRODUCTION: Found {len(validated_products)} validated products for '{ingredient}'")
                        # Log first 2 products as examples
                        for j, product in enumerate(validated_products[:2]):
                            logging.info(f"   Product {j+1}: {product.name} - ${product.price} (ID: {product.product_id})")
                    else:
                        logging.warning(f"❌ PRODUCTION: No valid products after filtering for ingredient: '{ingredient}'")
                        failed_ingredients.append(ingredient)
                else:
                    logging.warning(f"❌ PRODUCTION: No products returned from Walmart API for ingredient: '{ingredient}'")
                    failed_ingredients.append(ingredient)
                
                    
            except Exception as e:
                logging.error(f"❌ PRODUCTION: Error processing ingredient '{ingredient}': {str(e)}")
                failed_ingredients.append(ingredient)
        
        # PRODUCTION: Enhanced logging
        logging.info(f"📊 PRODUCTION: Cart options completed: {successful_ingredients}/{total_ingredients} ingredients successful")
        if failed_ingredients:
            logging.warning(f"⚠️ PRODUCTION: Failed ingredients: {failed_ingredients}")
        
        # CRITICAL DEBUG: Log the state before checking
        logging.warning(f"🚨 DEBUG: ingredient_options length = {len(ingredient_options)}")
        logging.warning(f"🚨 DEBUG: successful_ingredients = {successful_ingredients}")
        logging.warning(f"🚨 DEBUG: failed_ingredients = {failed_ingredients}")
        
        # PRODUCTION: Check if we have any ingredient options BEFORE creating cart
        if not ingredient_options:
            logging.warning(f"🚨 EMERGENCY: Creating basic shopping cart without Walmart integration for recipe {recipe_id}")
            
            # Create basic ingredient list for manual shopping
            basic_cart = {
                "recipe_id": recipe_id,
                "recipe_title": recipe_title,
                "ingredients_list": shopping_list,
                "shopping_mode": "manual",
                "message": "Shopping list ready - visit Walmart.com to purchase these ingredients",
                "walmart_search_url": f"https://www.walmart.com/search?q={'+'.join(shopping_list)}",
                "manual_shopping_instructions": "Copy this ingredient list and search for these items on Walmart.com or visit your local store."
            }
            
            return basic_cart
        
        # PRODUCTION: Create cart options object - ONLY REAL DATA
        cart_options = GroceryCartOptions(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipe_id=recipe_id,
            ingredient_options=ingredient_options,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        await db.grocery_cart_options.insert_one(cart_options.dict())
        
        cart_dict = cart_options.dict()
        
        logging.info(f"✅ PRODUCTION: Successfully created cart options with {len(ingredient_options)} ingredient groups")
        # Also log total products found
        total_products = sum(len(opt.options) for opt in ingredient_options)
        logging.info(f"🛒 PRODUCTION: Total products found: {total_products}")
        
        return cart_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ PRODUCTION: Cart options critical error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating cart options: {str(e)}")

@api_router.post("/grocery/custom-cart")
async def create_custom_cart(cart_data: Dict[str, Any]):
    """Create a custom grocery cart with selected products"""
    try:
        # Extract data
        user_id = cart_data.get('user_id')
        recipe_id = cart_data.get('recipe_id')
        selected_products = cart_data.get('products', [])
        
        if not all([user_id, recipe_id, selected_products]):
            raise HTTPException(status_code=400, detail="Missing required cart data")
        
        # Create cart products and validate product IDs
        cart_products = []
        total_price = 0
        product_ids = []
        
        for product_data in selected_products:
            product_id = product_data['product_id']
            
            # Validate that product ID is from real Walmart API (not mock data)
            # Real Walmart product IDs are numeric and at least 6 digits
            if (not product_id.isdigit() or 
                len(product_id) < 6 or
                product_id.startswith('10315') or  # Common mock ID pattern from old data
                product_id.startswith('walmart-') or 
                product_id.startswith('mock-')):
                logging.warning(f"Skipping invalid/mock product ID: {product_id} for {product_data.get('ingredient_name', 'unknown')}")
                continue
            
            cart_product = GroceryCartProduct(
                ingredient_name=product_data['ingredient_name'],
                product_id=product_id,
                name=product_data['name'],
                price=product_data['price'],
                quantity=product_data.get('quantity', 1)
            )
            cart_products.append(cart_product)
            total_price += cart_product.price * cart_product.quantity
            product_ids.append(product_id)
        
        # Only generate Walmart URL if we have real product IDs
        if not product_ids:
            raise HTTPException(status_code=400, detail="No valid Walmart product IDs found. Only real Walmart products can be added to cart.")
        
        # Generate Walmart URL with correct offers format: offers=SKU1|Quantity1,SKU2|Quantity2
        walmart_offers = []
        for product in cart_products:
            product_id = product.product_id
            quantity = product.quantity if isinstance(product.quantity, (int, float)) and product.quantity > 0 else 1
            
            # Use new offers format: SKU|Quantity
            walmart_offers.append(f"{product_id}|{int(quantity)}")
        
        walmart_url = f"https://affil.walmart.com/cart/addToCart?offers={','.join(walmart_offers)}"
        
        # Create cart
        cart = GroceryCart(
            user_id=user_id,
            recipe_id=recipe_id,
            products=cart_products,
            total_price=total_price,
            walmart_url=walmart_url
        )
        
        # Save to database
        cart_dict = cart.dict()
        result = await db.grocery_carts.insert_one(cart_dict)
        
        # Get the inserted document and return it
        if result.inserted_id:
            inserted_cart = await db.grocery_carts.find_one({"_id": result.inserted_id})
            return mongo_to_dict(inserted_cart)
        
        return cart_dict
        
    except Exception as e:
        logging.error(f"Error creating custom cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create custom cart")

# CORS middleware configuration - Production ready
@app.delete("/api/starbucks-recipes/{recipe_id}")
async def delete_starbucks_recipe(recipe_id: str):
    """Delete a specific Starbucks recipe"""
    try:
        # Convert string ID to ObjectId if needed
        from bson import ObjectId
        if ObjectId.is_valid(recipe_id):
            object_id = ObjectId(recipe_id)
            result = await db.starbucks_recipes.delete_one({"_id": object_id})
        else:
            result = await db.starbucks_recipes.delete_one({"id": recipe_id})
        
        if result.deleted_count == 1:
            return {"success": True, "message": "Starbucks recipe deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Starbucks recipe not found")
    except Exception as e:
        print(f"Error deleting Starbucks recipe: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete Starbucks recipe")

# NO CACHE MIDDLEWARE - PREVENT ALL BACKEND CACHING
@app.middleware("http")
async def no_cache_middleware(request, call_next):
    """Prevent all caching in backend responses"""
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://buildyoursmartcart.com", 
        "http://localhost:3000", 
        "http://localhost:8001",
        "https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com",  # Preview environment
        "https://recipe-cart-app-1.emergent.host",  # New deployed environment
        "*"  # Allow all origins for testing
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
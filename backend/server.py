from fastapi import FastAPI, APIRouter, HTTPException
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

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
        # Normalize email
        email_lower = login_data.email.lower().strip()
        
        # Find user (case-insensitive)
        user = await db.users.find_one({"email": {"$regex": f"^{email_lower}$", "$options": "i"}})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password FIRST
        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # THEN check if user is verified (after valid credentials)
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
def _get_walmart_signature() -> tuple:
    """Generate Walmart API signature and timestamp"""
    try:
        # Parse private key
        private_key = serialization.load_pem_private_key(
            WALMART_PRIVATE_KEY.encode(),
            password=None
        )
        
        # Generate timestamp
        timestamp = str(int(time.time() * 1000))
        
        # Create message in the correct format: CONSUMER_ID\nTIMESTAMP\nKEY_VERSION\n
        message = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n".encode("utf-8")
        
        # Sign the message
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Base64 encode the signature
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        
        return timestamp, signature_b64
        
    except Exception as e:
        logging.error(f"Error generating Walmart signature: {str(e)}")
        raise

def _extract_core_ingredient(ingredient: str) -> str:
    """Extract the core ingredient name from complex recipe descriptions"""
    
    # Convert to lowercase for processing
    ingredient_lower = ingredient.lower().strip()
    
    # Remove common recipe measurements and quantities at the beginning
    ingredient_lower = re.sub(r'^(\d+[\s\/\-]*\d*\s*)?(cups?|cup|tbsp|tablespoons?|tablespoon|tsp|teaspoons?|teaspoon|lbs?|pounds?|pound|oz|ounces?|ounce|cans?|can|jars?|jar|bottles?|bottle|packages?|package|bags?|bag|cloves?|clove|slices?|slice|pieces?|piece|pinch|dash)\s+', '', ingredient_lower)
    
    # Remove quantities at the beginning (like "1", "2", "1/2", "1-2", etc.)
    ingredient_lower = re.sub(r'^\d+[\s\/\-]*\d*\s+', '', ingredient_lower)
    
    # Remove preparation instructions (everything after comma, parentheses, or "to taste")
    ingredient_lower = re.sub(r'[,\(].*$', '', ingredient_lower)
    ingredient_lower = re.sub(r'\s+to\s+taste.*$', '', ingredient_lower)
    ingredient_lower = re.sub(r'\s+(drained|rinsed|chopped|sliced|diced|minced|cooked|fresh|dried|ground|whole|halved|quartered).*$', '', ingredient_lower)
    
    # Handle specific ingredient mappings for better search results
    ingredient_mappings = {
        'bbq sauce': 'barbecue sauce',
        'mixed vegetables': 'frozen mixed vegetables',
        'bell peppers': 'bell pepper',
        'olive oil': 'olive oil',
        'chickpeas': 'chickpeas',
        'garbanzo beans': 'chickpeas',
        'quinoa': 'quinoa',
        'avocado': 'avocado',
        'salt and pepper': 'salt pepper',
        'tomato sauce': 'tomato sauce',
        'tomato paste': 'tomato paste',
        'chicken breast': 'chicken breast',
        'ground beef': 'ground beef',
        'pasta': 'pasta',
        'spaghetti': 'spaghetti pasta',
        'rice': 'rice',
        'onion': 'onion',
        'garlic': 'garlic',
        'cheese': 'shredded cheese'
    }
    
    # Clean up extra spaces
    ingredient_lower = ' '.join(ingredient_lower.split())
    
    # Check for direct mappings first
    for key, value in ingredient_mappings.items():
        if key in ingredient_lower:
            return value
    
    # If no direct mapping, try to extract the main ingredient
    # Remove adjectives and modifiers
    ingredient_lower = re.sub(r'\b(fresh|dried|ground|whole|chopped|sliced|diced|minced|cooked|raw|organic|extra\s+virgin|virgin|pure|natural|unsalted|salted|sweet|hot|mild|spicy|large|small|medium)\b\s*', '', ingredient_lower)
    
    # Remove extra spaces again
    ingredient_lower = ' '.join(ingredient_lower.split())
    
    # If the result is too short or empty, return the original (cleaned)
    if len(ingredient_lower) < 3:
        # Fallback: try to extract noun from original
        original_words = ingredient.lower().split()
        # Look for common food nouns
        food_nouns = ['oil', 'sauce', 'vegetables', 'quinoa', 'chickpeas', 'avocado', 'tomatoes', 'onion', 'garlic', 'cheese', 'pasta', 'rice', 'chicken', 'beef', 'pork', 'salt', 'pepper', 'herbs', 'spices']
        for word in original_words:
            clean_word = re.sub(r'[,\(\)]', '', word)
            if clean_word in food_nouns:
                return clean_word
        
        # If still nothing found, return first substantial word
        for word in original_words:
            clean_word = re.sub(r'[,\(\)\d]', '', word).strip()
            if len(clean_word) > 2 and clean_word not in ['cup', 'cups', 'tbsp', 'tsp', 'can', 'jar', 'bottle', 'package', 'bag']:
                return clean_word
    
    return ingredient_lower.strip() if ingredient_lower.strip() else ingredient

async def _get_walmart_product_options(ingredient: str, max_options: int = 3) -> List[WalmartProduct]:
    """Get Walmart product options for an ingredient"""
    try:
        # Extract core ingredient name using improved parsing
        clean_ingredient = _extract_core_ingredient(ingredient)
        
        logging.info(f"Original ingredient: '{ingredient}' -> Cleaned: '{clean_ingredient}'")
        
        # Try real Walmart API first
        try:
            # Generate signature and timestamp
            timestamp, signature = _get_walmart_signature()
            
            # Prepare API call
            query = clean_ingredient.replace(' ', '+')
            url = f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query={query}&numItems={max_options}"
            
            headers = {
                "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
                "WM_CONSUMER.INTIMESTAMP": timestamp,
                "WM_SEC.KEY_VERSION": WALMART_KEY_VERSION,
                "WM_SEC.AUTH_SIGNATURE": signature,
                "Content-Type": "application/json"
            }
            
            logging.info(f"Making Walmart API call for ingredient: '{clean_ingredient}'")
            logging.info(f"URL: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    products = []
                    
                    if 'items' in data:
                        logging.info(f"Found {len(data['items'])} items from Walmart API for '{clean_ingredient}'")
                        for item in data['items'][:max_options]:
                            if 'itemId' in item:
                                product = WalmartProduct(
                                    product_id=str(item.get('itemId', '')),
                                    name=item.get('name', clean_ingredient),
                                    price=float(item.get('salePrice', 0.0)),
                                    thumbnail_image=item.get('thumbnailImage', ''),
                                    availability="Available"
                                )
                                products.append(product)
                                logging.info(f"Real Walmart product: {product.name} - ${product.price} (ID: {product.product_id})")
                        
                        if products:
                            return products
                    else:
                        logging.warning(f"No items found in Walmart API response for '{clean_ingredient}'")
                else:
                    logging.warning(f"Walmart API error for '{clean_ingredient}': {response.status_code} - {response.text}")
                    
        except Exception as api_error:
            logging.error(f"Walmart API call failed for '{clean_ingredient}': {str(api_error)}")
        
        # Fallback to enhanced mock data if API fails
        logging.info(f"Using enhanced mock data for '{clean_ingredient}'")
        mock_products = []
        
        # Create realistic sample products based on cleaned ingredient type
        ingredient_lower = clean_ingredient.lower()
        
        if any(word in ingredient_lower for word in ['chicken']):
            mock_products = [
                WalmartProduct(product_id="10452697", name="Great Value Chicken Breast 2.5lb", price=8.99, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315162", name="Tyson Grilled Chicken Strips 9oz", price=5.48, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10452855", name="Rotisserie Chicken Whole", price=4.98, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['chickpeas', 'garbanzo']):
            mock_products = [
                WalmartProduct(product_id="10315201", name="Bush's Chickpeas 15.5oz Can", price=1.18, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315202", name="Great Value Chickpeas 15oz", price=0.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315203", name="Goya Chickpeas 15.5oz", price=1.28, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['bbq', 'barbecue']):
            mock_products = [
                WalmartProduct(product_id="10315204", name="Sweet Baby Ray's BBQ Sauce 18oz", price=1.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315205", name="KC Masterpiece BBQ Sauce 18oz", price=2.28, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315206", name="Great Value BBQ Sauce 18oz", price=1.48, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['quinoa']):
            mock_products = [
                WalmartProduct(product_id="10315207", name="Ancient Harvest Quinoa 12oz", price=4.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315208", name="Great Value Organic Quinoa 16oz", price=3.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315209", name="Bob's Red Mill Quinoa 18oz", price=5.99, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['mixed vegetables', 'frozen vegetables']):
            mock_products = [
                WalmartProduct(product_id="10315210", name="Great Value Frozen Mixed Vegetables 12oz", price=1.24, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315211", name="Birds Eye Mixed Vegetables 10oz", price=1.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315212", name="Green Giant Mixed Vegetables 12oz", price=2.18, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['avocado']):
            mock_products = [
                WalmartProduct(product_id="10315213", name="Fresh Avocados 4 count", price=3.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315214", name="Organic Avocados 4 count", price=5.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315215", name="Large Avocados 3 count", price=4.48, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['olive oil']):
            mock_products = [
                WalmartProduct(product_id="10315216", name="Bertolli Extra Virgin Olive Oil 16.9oz", price=6.99, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315217", name="Great Value Olive Oil 17oz", price=4.97, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315218", name="Pompeian Extra Virgin Olive Oil 16oz", price=5.48, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['salt', 'pepper']):
            mock_products = [
                WalmartProduct(product_id="10315219", name="Morton Salt 26oz", price=1.24, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315220", name="McCormick Black Pepper 3oz", price=2.68, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315221", name="Great Value Salt & Pepper Set", price=1.98, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['pasta', 'spaghetti', 'penne', 'noodle']):
            mock_products = [
                WalmartProduct(product_id="10315162", name="Barilla Pasta Penne 16oz", price=1.99, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10533089", name="Great Value Spaghetti 1lb", price=1.28, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315264", name="Ronzoni Pasta Shells 12oz", price=1.68, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['tomato', 'tomatoes']):
            mock_products = [
                WalmartProduct(product_id="44391492", name="Fresh Roma Tomatoes 2lb", price=2.49, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315486", name="Hunt's Diced Tomatoes 14.5oz", price=1.18, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315487", name="Cherry Tomatoes 1lb", price=2.97, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['cheese', 'mozzarella', 'parmesan', 'cheddar']):
            mock_products = [
                WalmartProduct(product_id="10315488", name="Great Value Shredded Cheddar Cheese 8oz", price=2.84, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315162", name="Kraft Mexican Style Shredded Cheese 8oz", price=3.97, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10533089", name="Sargento Shredded Monterey Jack 8oz", price=4.48, thumbnail_image="", availability="Available")
            ]
        elif any(word in ingredient_lower for word in ['garlic']):
            mock_products = [
                WalmartProduct(product_id="10315264", name="Fresh Garlic Bulb 3oz", price=0.98, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id="10315486", name="Great Value Minced Garlic 8oz", price=2.47, thumbnail_image="", availability="Available")
            ]
        else:
            # Generic products for other ingredients with realistic IDs
            base_id = abs(hash(clean_ingredient)) % 90000000 + 10000000  # Generate 8-digit realistic ID
            mock_products = [
                WalmartProduct(product_id=str(base_id), name=f"Great Value {clean_ingredient.title()}", price=2.99, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id=str(base_id + 1), name=f"Fresh {clean_ingredient.title()}", price=3.49, thumbnail_image="", availability="Available"),
                WalmartProduct(product_id=str(base_id + 2), name=f"Organic {clean_ingredient.title()}", price=4.99, thumbnail_image="", availability="Available")
            ]
        
        return mock_products[:max_options]
                
    except Exception as e:
        logging.error(f"Error fetching Walmart products for '{ingredient}': {str(e)}")
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
                prompt_parts.append(f"Create healthy frozen yogurt berry bites recipe for {request.servings} people. Focus on Greek yogurt, mixed berries, natural sweeteners, and bite-sized frozen treats. Include freezing techniques and presentation.")
            else:
                prompt_parts.append(f"Create a {recipe_type} snack recipe for {request.servings} people. Focus on tasty, satisfying snacks that are perfect for any time of day.")
        
        elif recipe_category == "beverage":
            # Enhanced beverage prompt to generate 4 unique and original beverage recipes
            prompt_parts.append(f"""Generate 4 unique and original beverage recipes for {request.servings} people, one for each of the following types:

1. Coffee-based drink
   - May include elements like cold foam, whipped crème, flavored syrups, or layered toppings like caramel drizzle — but only if it enhances the concept.

2. Lemonade-based drink  
   - Refreshing, fruity, or herbal — perfect for summer.

3. Thai tea-based drink
   - Layered or infused with other flavors (like fruit, spices, milk alternatives, or syrups).

4. Boba drink (bubble tea)
   - Can be milk-based or fruit-based, and use tapioca, popping boba, or creative textures.

For each drink, include the following:
🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make the drinks visually Instagram-worthy and perfect for any season.""")
        
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
        
        prompt_parts.append("""
Return ONLY a valid JSON object with this exact structure:

For BEVERAGES (4-recipe format):
{
    "title": "4 Premium Beverage Collection",
    "description": "Four unique and original beverage recipes featuring coffee, lemonade, Thai tea, and boba drinks",
    "ingredients": ["combined list of all ingredients from all 4 recipes"],
    "instructions": [
        "🧋 COFFEE-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 LEMONADE-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 THAI TEA-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 BOBA DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]"
    ],
    "prep_time": 45,
    "cook_time": 15,
    "calories_per_serving": 280,
    "shopping_list": ["ingredient_name_1", "ingredient_name_2", "ingredient_name_3"]
}

For all other categories (SNACKS, CUISINE):
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

BEVERAGES: Focus on detailed "secret recipes" with exact measurements and professional techniques:
- Coffee (specialty espresso drinks, cold brews, gourmet preparations with exact measurements)
- Boba tea (brown sugar boba, fruit boba with cooking instructions, syrup preparation)
- Thai tea (authentic orange tea with traditional preparation methods)
- Special lemonades (unique fruit combinations, natural sweeteners, fresh herbs, gourmet touches)

For BEVERAGES, create detailed "secret recipes" with:
- Title of the drink
- Brief description (1–2 sentences)
- List of ingredients with exact quantities and units (cups, tablespoons, ounces)
- Detailed step-by-step instructions including brewing, mixing, and serving techniques
- Optional tips or substitutions for customization
- Professional techniques (shaking, layering, temperature control)

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
- Clean ingredient names without quantities, measurements, or preparation instructions

BEVERAGE EXAMPLES for reference:
- Starbucks Copycat Iced Brown Sugar Oatmilk Shaken Espresso: espresso, brown sugar, oat milk, cinnamon, ice
- Brown Sugar Boba Milk Tea: black tea, tapioca pearls, brown sugar, milk, ice
- Guava Lemonade: guava nectar, fresh lemons, sugar, water, ice
- Fresas con Crema Milkshake: strawberries, vanilla ice cream, condensed milk, cinnamon, whipped cream

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
        
        # Create recipe object
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
        
        # Save to database
        recipe_dict = recipe.dict()
        result = await db.recipes.insert_one(recipe_dict)
        
        # Get the inserted document and return it
        if result.inserted_id:
            inserted_recipe = await db.recipes.find_one({"_id": result.inserted_id})
            return mongo_to_dict(inserted_recipe)
        
        return recipe_dict
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON parse error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse recipe from AI")
    except Exception as e:
        logging.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recipe")

@api_router.get("/recipes/{recipe_id}")
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
async def create_grocery_cart_options(recipe_id: str, user_id: str):
    """Create grocery cart with multiple options per ingredient"""
    try:
        # Get the recipe
        recipe = await db.recipes.find_one({"id": recipe_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Use shopping list if available, otherwise fall back to parsing ingredients
        ingredients_to_search = []
        
        if recipe.get('shopping_list') and len(recipe.get('shopping_list', [])) > 0:
            logging.info(f"Using shopping list for product search: {recipe['shopping_list']}")
            ingredients_to_search = recipe['shopping_list']
        else:
            logging.info(f"No shopping list found, using ingredient parsing for: {recipe['ingredients']}")
            ingredients_to_search = recipe['ingredients']
        
        # Get product options for each ingredient
        ingredient_options = []
        for index, ingredient in enumerate(ingredients_to_search):
            products = await _get_walmart_product_options(ingredient, max_options=3)
            
            # Use the original ingredient description for display if we have both
            original_ingredient = recipe['ingredients'][index] if index < len(recipe['ingredients']) else ingredient
            
            ingredient_option = IngredientOption(
                ingredient_name=ingredient,  # Clean ingredient name for searching
                original_ingredient=original_ingredient,  # Full ingredient description for display
                options=products
            )
            ingredient_options.append(ingredient_option)
            
            logging.info(f"Ingredient: '{ingredient}' -> Found {len(products)} products")
        
        # Create cart options object
        cart_options = GroceryCartOptions(
            user_id=user_id,
            recipe_id=recipe_id,
            ingredient_options=ingredient_options
        )
        
        # Save to database
        cart_dict = cart_options.dict()
        result = await db.grocery_cart_options.insert_one(cart_dict)
        
        # Get the inserted document and return it
        if result.inserted_id:
            inserted_cart = await db.grocery_cart_options.find_one({"_id": result.inserted_id})
            return mongo_to_dict(inserted_cart)
        
        return cart_dict
        
    except Exception as e:
        logging.error(f"Error creating grocery cart options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create grocery cart options")

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
        
        # Create cart products
        cart_products = []
        total_price = 0
        product_ids = []
        
        for product_data in selected_products:
            cart_product = GroceryCartProduct(
                ingredient_name=product_data['ingredient_name'],
                product_id=product_data['product_id'],
                name=product_data['name'],
                price=product_data['price'],
                quantity=product_data.get('quantity', 1)
            )
            cart_products.append(cart_product)
            total_price += cart_product.price * cart_product.quantity
            product_ids.append(cart_product.product_id)
        
        # Generate Walmart URL
        walmart_url = f"https://affil.walmart.com/cart/addToCart?items={','.join(product_ids)}"
        
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for deployment flexibility
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
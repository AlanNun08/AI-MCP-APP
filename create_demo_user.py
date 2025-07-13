#!/usr/bin/env python3
"""
Script to create a verified demo user for testing the Walmart integration
"""
import asyncio
import os
import sys
from datetime import datetime
import uuid
import bcrypt
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv('.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def create_demo_user():
    """Create a verified demo user for testing"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Check if demo user already exists
        existing_user = await db.users.find_one({"email": "demo@test.com"})
        if existing_user:
            print("Demo user already exists. Updating to verified status...")
            # Update existing user to be verified
            await db.users.update_one(
                {"email": "demo@test.com"},
                {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
            )
            print("✅ Demo user updated to verified status")
        else:
            print("Creating new demo user...")
            # Create new demo user
            demo_user = {
                "id": str(uuid.uuid4()),
                "first_name": "Demo",
                "last_name": "User", 
                "email": "demo@test.com",
                "password_hash": hash_password("password123"),
                "dietary_preferences": [],
                "allergies": [],
                "favorite_cuisines": ["Italian", "Mexican"],
                "is_verified": True,
                "created_at": datetime.utcnow(),
                "verified_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(demo_user)
            if result.inserted_id:
                print("✅ Demo user created successfully!")
                print(f"   Email: demo@test.com")
                print(f"   Password: password123")
                print(f"   User ID: {demo_user['id']}")
                print(f"   Verified: True")
            else:
                print("❌ Failed to create demo user")
                
        # Create a test user as well for additional testing
        existing_test_user = await db.users.find_one({"email": "test.user@example.com"})
        if not existing_test_user:
            print("Creating test.user@example.com...")
            test_user = {
                "id": str(uuid.uuid4()),
                "first_name": "Test",
                "last_name": "User",
                "email": "test.user@example.com", 
                "password_hash": hash_password("password123"),
                "dietary_preferences": [],
                "allergies": [],
                "favorite_cuisines": ["Italian"],
                "is_verified": True,
                "created_at": datetime.utcnow(),
                "verified_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(test_user)
            if result.inserted_id:
                print("✅ Test user created successfully!")
                print(f"   Email: test.user@example.com")
                print(f"   Password: password123")
                print(f"   User ID: {test_user['id']}")
            else:
                print("❌ Failed to create test user")
                
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_user())
#!/usr/bin/env python3
"""
Script to clean up and create a fresh verified demo user
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import uuid

# Load environment variables
load_dotenv('/app/backend/.env')

async def create_fresh_demo_user():
    """Delete old demo users and create a fresh verified one"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Delete all existing demo users
        delete_result = await db.users.delete_many({"email": "demo@test.com"})
        print(f"Deleted {delete_result.deleted_count} existing demo users")
        
        # Create a fresh demo user
        password = "password123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        demo_user = {
            "id": str(uuid.uuid4()),
            "first_name": "Demo",
            "last_name": "User",
            "email": "demo@test.com",
            "password_hash": password_hash,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": [],
            "is_verified": True,
            "verified_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        # Insert the new demo user
        result = await db.users.insert_one(demo_user)
        
        if result.inserted_id:
            print(f"✅ Created fresh verified demo user:")
            print(f"  ID: {demo_user['id']}")
            print(f"  Name: {demo_user['first_name']} {demo_user['last_name']}")
            print(f"  Email: {demo_user['email']}")
            print(f"  Verified: {demo_user['is_verified']}")
        else:
            print("❌ Failed to create demo user")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_fresh_demo_user())
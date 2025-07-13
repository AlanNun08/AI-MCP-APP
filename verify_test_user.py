#!/usr/bin/env python3
"""
Script to verify the test user
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def verify_test_user():
    """Verify the test user"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Verify the test user
        result = await db.users.update_one(
            {"email": "testuser123@example.com"},
            {
                "$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count > 0:
            print(f"✅ Test user verified successfully!")
            
            # Get the user to confirm
            user = await db.users.find_one({"email": "testuser123@example.com"})
            if user:
                print(f"User ID: {user.get('id')}")
                print(f"Name: {user.get('first_name')} {user.get('last_name')}")
                print(f"Email: {user.get('email')}")
                print(f"Verified: {user.get('is_verified')}")
        else:
            print("❌ Test user not found")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_test_user())
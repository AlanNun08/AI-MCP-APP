#!/usr/bin/env python3
"""
Script to manually verify the demo user for testing purposes
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def verify_demo_user():
    """Manually verify the demo user"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Update the demo user to be verified
        result = await db.users.update_one(
            {"email": "demo@test.com"},
            {
                "$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count > 0:
            print("✅ Demo user verified successfully!")
            
            # Get the user to confirm
            user = await db.users.find_one({"email": "demo@test.com"})
            if user:
                print(f"User ID: {user.get('id')}")
                print(f"Name: {user.get('first_name')} {user.get('last_name')}")
                print(f"Email: {user.get('email')}")
                print(f"Verified: {user.get('is_verified')}")
            else:
                print("❌ User not found after verification")
        else:
            print("❌ Demo user not found in database")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Error verifying demo user: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_demo_user())
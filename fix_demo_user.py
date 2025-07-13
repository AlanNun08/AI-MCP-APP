#!/usr/bin/env python3
"""
Script to find and verify the correct demo user
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def fix_demo_user():
    """Find and verify the correct demo user"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Find the user with the specific ID from login response
        target_user_id = "00cf1e50-4693-4beb-8eb6-da37dcc38cb6"
        
        user = await db.users.find_one({"id": target_user_id})
        
        if user:
            print(f"Found target user:")
            print(f"  ID: {user.get('id')}")
            print(f"  Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Verified: {user.get('is_verified')}")
            
            # Verify this specific user
            result = await db.users.update_one(
                {"id": target_user_id},
                {
                    "$set": {
                        "is_verified": True,
                        "verified_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                print(f"  ✅ Target user verified successfully!")
            else:
                print(f"  ❌ Failed to verify target user")
        else:
            print(f"❌ Target user {target_user_id} not found")
            
            # List all demo users
            print("\nAll demo@test.com users:")
            async for user in db.users.find({"email": "demo@test.com"}):
                print(f"  ID: {user.get('id')}, Verified: {user.get('is_verified')}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_demo_user())
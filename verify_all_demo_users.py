#!/usr/bin/env python3
"""
Script to verify all demo users and check their status
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def verify_all_demo_users():
    """Find and verify all demo users"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Find all demo users
        demo_users = []
        async for user in db.users.find({"email": "demo@test.com"}):
            demo_users.append(user)
        
        print(f"Found {len(demo_users)} demo users:")
        
        for i, user in enumerate(demo_users):
            print(f"\nDemo User {i+1}:")
            print(f"  ID: {user.get('id')}")
            print(f"  Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Verified: {user.get('is_verified')}")
            print(f"  MongoDB _id: {user.get('_id')}")
            
            # Verify this user
            result = await db.users.update_one(
                {"_id": user.get('_id')},
                {
                    "$set": {
                        "is_verified": True,
                        "verified_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count > 0:
                print(f"  ✅ Verified successfully!")
            else:
                print(f"  ❌ Failed to verify")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_all_demo_users())
#!/usr/bin/env python3
"""
Script to find all demo users and fix them
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
load_dotenv('./backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')

async def find_all_demo_users():
    """Find all demo users"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Find all users with demo email (case insensitive)
        demo_users = []
        async for user in db.users.find({"email": {"$regex": "^demo@test\\.com$", "$options": "i"}}):
            demo_users.append(user)
            
        print(f"Found {len(demo_users)} demo users:")
        for i, user in enumerate(demo_users):
            print(f"\nDemo User {i+1}:")
            print(f"  ID: {user.get('id')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"  Is Verified: {user.get('is_verified')}")
            print(f"  Created At: {user.get('created_at')}")
            print(f"  Verified At: {user.get('verified_at')}")
            
            # Update this user to verified
            result = await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Updated to verified")
            else:
                print(f"  ❌ Failed to update")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(find_all_demo_users())
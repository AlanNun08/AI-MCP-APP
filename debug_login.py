#!/usr/bin/env python3
"""
Script to debug the login issue by checking for the user ID returned by login
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

async def debug_login_issue():
    """Debug the login issue"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Look for the user ID that login is returning
        mysterious_user_id = "00cf1e50-4693-4beb-8eb6-da37dcc38cb6"
        mysterious_user = await db.users.find_one({"id": mysterious_user_id})
        
        if mysterious_user:
            print("Found the mysterious user:")
            print(f"  ID: {mysterious_user.get('id')}")
            print(f"  Email: {mysterious_user.get('email')}")
            print(f"  Name: {mysterious_user.get('first_name')} {mysterious_user.get('last_name')}")
            print(f"  Is Verified: {mysterious_user.get('is_verified')}")
            print(f"  Created At: {mysterious_user.get('created_at')}")
            
            # Update this user too
            result = await db.users.update_one(
                {"id": mysterious_user_id},
                {"$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print("  ✅ Updated mysterious user to verified")
            else:
                print("  ❌ Failed to update mysterious user")
        else:
            print("Mysterious user not found")
            
        # Also list all users with demo@test.com to see if there are others
        print("\nAll users with demo@test.com:")
        async for user in db.users.find({"email": {"$regex": "demo@test\\.com", "$options": "i"}}):
            print(f"  ID: {user.get('id')}, Email: {user.get('email')}, Verified: {user.get('is_verified')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_login_issue())
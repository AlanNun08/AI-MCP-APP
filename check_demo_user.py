#!/usr/bin/env python3
"""
Script to check and fix the demo user verification status
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

async def check_and_fix_demo_user():
    """Check and fix demo user verification status"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Find the demo user
        demo_user = await db.users.find_one({"email": "demo@test.com"})
        if demo_user:
            print("Demo user found:")
            print(f"  ID: {demo_user.get('id')}")
            print(f"  Email: {demo_user.get('email')}")
            print(f"  Name: {demo_user.get('first_name')} {demo_user.get('last_name')}")
            print(f"  Is Verified: {demo_user.get('is_verified')}")
            print(f"  Created At: {demo_user.get('created_at')}")
            print(f"  Verified At: {demo_user.get('verified_at')}")
            
            # Force update to verified status
            result = await db.users.update_one(
                {"email": "demo@test.com"},
                {"$set": {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print("✅ Demo user verification status updated successfully")
                
                # Verify the update
                updated_user = await db.users.find_one({"email": "demo@test.com"})
                print(f"✅ Verified status is now: {updated_user.get('is_verified')}")
            else:
                print("❌ Failed to update demo user")
                
        else:
            print("❌ Demo user not found")
            
        # Also check test.user@example.com
        test_user = await db.users.find_one({"email": "test.user@example.com"})
        if test_user:
            print("\nTest user found:")
            print(f"  Is Verified: {test_user.get('is_verified')}")
        else:
            print("\nTest user not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_and_fix_demo_user())
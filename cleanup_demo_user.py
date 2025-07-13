#!/usr/bin/env python3
"""
Script to clean up verification codes and ensure demo user is properly verified
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def cleanup_and_verify():
    """Clean up verification codes and ensure demo user is verified"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Delete all verification codes for demo user
        delete_result = await db.verification_codes.delete_many({"email": "demo@test.com"})
        print(f"Deleted {delete_result.deleted_count} verification codes for demo@test.com")
        
        # Find and verify the demo user
        user = await db.users.find_one({"email": "demo@test.com"})
        
        if user:
            print(f"Found demo user:")
            print(f"  ID: {user.get('id')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Verified: {user.get('is_verified')}")
            
            # Force verify the user
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
                print(f"✅ Demo user verified successfully!")
                
                # Verify the update
                updated_user = await db.users.find_one({"email": "demo@test.com"})
                print(f"Updated verification status: {updated_user.get('is_verified')}")
            else:
                print(f"❌ Failed to verify demo user")
        else:
            print("❌ Demo user not found")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(cleanup_and_verify())
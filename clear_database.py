#!/usr/bin/env python3
"""
Clear all users from database for fresh start
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def clear_database():
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'buildyoursmartcart_production')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Clear all collections
        collections_to_clear = [
            'users',
            'verification_codes',
            'password_reset_codes',
            'recipes',
            'snack_recipes',
            'beverage_recipes',
            'starbucks_recipes'
        ]
        
        results = {}
        for collection_name in collections_to_clear:
            result = await db[collection_name].delete_many({})
            results[collection_name] = result.deleted_count
            print(f"Cleared {result.deleted_count} documents from {collection_name}")
        
        print(f"\n✅ Database cleared successfully!")
        print(f"Total documents removed: {sum(results.values())}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return None
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(clear_database())
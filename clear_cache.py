#!/usr/bin/env python3
"""
Clear all backend cache and database cart options
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def clear_all_cache():
    """Clear all cached data"""
    try:
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Clear grocery cart options cache
        cart_result = await db.grocery_cart_options.delete_many({})
        print(f"✅ Cleared {cart_result.deleted_count} cached cart options")
        
        # Clear any other cache collections if they exist
        collections_to_clear = [
            'walmart_cache',
            'product_cache', 
            'api_cache',
            'grocery_cache'
        ]
        
        for collection_name in collections_to_clear:
            try:
                collection = getattr(db, collection_name)
                result = await collection.delete_many({})
                if result.deleted_count > 0:
                    print(f"✅ Cleared {result.deleted_count} items from {collection_name}")
            except:
                pass  # Collection might not exist
        
        client.close()
        print("🧹 All cache cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")

if __name__ == "__main__":
    asyncio.run(clear_all_cache())
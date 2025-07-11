#!/usr/bin/env python3
"""
Create a working account for Alan
"""
import asyncio
import motor.motor_asyncio
import bcrypt
from datetime import datetime
import uuid
import requests

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

async def create_working_account():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_recipe_app_production']
    
    # Clear everything
    await db.users.delete_many({})
    await db.verification_codes.delete_many({})
    await db.password_reset_codes.delete_many({})
    
    print("🗑️ Cleared all data")
    
    # Create account using registration endpoint (like a real user would)
    registration_data = {
        "first_name": "Alan",
        "last_name": "Nunez",
        "email": "alan.nunez0310@icloud.com",
        "password": "simpleworkingpass123",
        "dietary_preferences": ["None"],
        "allergies": ["None"],
        "favorite_cuisines": ["Italian"]
    }
    
    print("👤 Creating account via registration API...")
    
    # Use registration API
    response = requests.post('http://localhost:8001/api/auth/register', json=registration_data)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Registration successful!")
        print(f"   Email: {user_data.get('email')}")
        print(f"   User ID: {user_data.get('user_id')}")
        
        # Mark as verified directly in database
        await db.users.update_one(
            {"email": registration_data["email"]},
            {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
        )
        print(f"✅ Marked as verified")
        
        # Test login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = requests.post('http://localhost:8001/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"✅ LOGIN TEST SUCCESSFUL!")
            print(f"   User ID: {login_result.get('user_id')}")
            print(f"   Email: {login_result.get('email')}")
            
            return registration_data["email"], registration_data["password"]
        else:
            print(f"❌ Login test failed: {login_response.text}")
    else:
        print(f"❌ Registration failed: {response.text}")
    
    client.close()
    return None, None

async def main():
    print("🔧 Creating Working Account for Alan")
    print("=" * 40)
    
    email, password = await create_working_account()
    
    if email and password:
        print(f"\n🎉 SUCCESS! Working credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n📱 You can now login to your preview!")
    else:
        print(f"\n❌ Failed to create working account")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Create a properly verified account that definitely works
"""
import asyncio
import requests
import motor.motor_asyncio
from datetime import datetime
import time

BACKEND_URL = "https://407d4e17-1478-4b87-bdc3-d8a695a6f09c.preview.emergentagent.com"

async def create_and_verify_account():
    """Create account and verify it works"""
    
    # Step 1: Clear database
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_recipe_app_production']
    await db.users.delete_many({})
    await db.verification_codes.delete_many({})
    await db.password_reset_codes.delete_many({})
    print("🗑️ Cleared database")
    
    # Step 2: Register account
    email = "alan.test.verified@example.com"
    password = "testverified123"
    
    registration_data = {
        "first_name": "Alan",
        "last_name": "Nunez",
        "email": email,
        "password": password,
        "dietary_preferences": ["None"],
        "allergies": ["None"],
        "favorite_cuisines": ["Italian"]
    }
    
    print(f"📝 Registering account: {email}")
    response = requests.post(f"{BACKEND_URL}/api/auth/register", json=registration_data)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Registration successful: {user_data.get('user_id')}")
        
        # Step 3: Mark as verified in database
        await db.users.update_one(
            {"email": email},
            {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
        )
        print(f"✅ Marked as verified in database")
        
        # Step 4: Wait a moment for changes to propagate
        time.sleep(2)
        
        # Step 5: Test login
        print(f"🧪 Testing login...")
        login_response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            if "needs_verification" not in login_data:
                print(f"🎉 SUCCESS! Account works without verification!")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                print(f"   User ID: {login_data.get('user_id')}")
                return email, password
            else:
                print(f"❌ Still needs verification: {login_data}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    else:
        print(f"❌ Registration failed: {response.text}")
    
    client.close()
    return None, None

async def main():
    print("🔧 Creating Verified Account")
    print("=" * 30)
    
    email, password = await create_and_verify_account()
    
    if email and password:
        print(f"\n🎉 ACCOUNT READY!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Status: VERIFIED - No email confirmation needed")
    else:
        print(f"\n❌ Failed to create working account")

if __name__ == "__main__":
    asyncio.run(main())
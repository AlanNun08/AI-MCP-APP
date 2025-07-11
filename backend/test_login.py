#!/usr/bin/env python3
"""
Test Login API for Deployed Site
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_login_api():
    """Test the login API endpoint"""
    
    # Test both local and potential deployed URLs
    test_urls = [
        "http://localhost:8001/api/auth/login",
        "https://your-deployed-site.com/api/auth/login",  # Replace with actual deployed URL
        "http://localhost:8001/api/auth/login"
    ]
    
    credentials = {
        "email": "alannunezsilva0310@gmail.com",
        "password": "TempPassword123!"
    }
    
    print("🔍 Testing login API endpoints...")
    print(f"📧 Email: {credentials['email']}")
    print(f"🔑 Password: {credentials['password']}")
    print("-" * 50)
    
    for url in test_urls:
        try:
            print(f"\n🌐 Testing: {url}")
            
            response = requests.post(
                url,
                json=credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LOGIN SUCCESSFUL!")
                print(f"👤 User: {data.get('user', {}).get('first_name', 'Unknown')} {data.get('user', {}).get('last_name', 'Unknown')}")
                print(f"🆔 User ID: {data.get('user', {}).get('id', 'Unknown')}")
                print(f"✅ Verified: {data.get('user', {}).get('is_verified', False)}")
                return True
            else:
                print(f"❌ LOGIN FAILED")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return False

def create_new_test_password():
    """Create a new password for testing"""
    import asyncio
    import bcrypt
    from motor.motor_asyncio import AsyncIOMotorClient
    
    async def update_password():
        try:
            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
            db = client[os.environ.get('DB_NAME', 'ai_recipe_app_production')]
            
            email = 'alannunezsilva0310@gmail.com'
            new_password = 'DeployedSite123!'
            
            # Hash the new password
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update user's password
            result = await db.users.update_one(
                {'email': email.lower()},
                {'$set': {'password_hash': password_hash}}
            )
            
            if result.modified_count > 0:
                print(f"\n🔄 NEW PASSWORD CREATED!")
                print(f"📧 Email: {email}")
                print(f"🔑 Password: {new_password}")
                print("-" * 50)
                return new_password
            else:
                print(f"❌ Failed to update password")
                return None
                
        except Exception as e:
            print(f"❌ Error updating password: {str(e)}")
            return None
    
    return asyncio.run(update_password())

if __name__ == "__main__":
    print("🚀 AI Chef Login Test Tool")
    print("=" * 50)
    
    # First, test current credentials
    if not test_login_api():
        print("\n🔄 Current credentials failed. Creating new password...")
        new_password = create_new_test_password()
        
        if new_password:
            print(f"\n✅ Use these NEW credentials on your deployed site:")
            print(f"📧 Email: alannunezsilva0310@gmail.com")
            print(f"🔑 Password: {new_password}")
        else:
            print("\n❌ Failed to create new password")
    
    print("\n" + "=" * 50)
    print("🛠️  CACHE CLEARING INSTRUCTIONS:")
    print("1. Go to your deployed site")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Application tab")
    print("4. Click 'Clear storage' on the left")
    print("5. Click 'Clear site data' button")
    print("6. Hard refresh (Ctrl+F5 or Cmd+Shift+R)")
    print("7. Try logging in again")
    print("=" * 50)
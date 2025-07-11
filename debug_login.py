#!/usr/bin/env python3
"""
Debug login process for Alan's account
"""
import asyncio
import motor.motor_asyncio
import bcrypt
import requests
import json

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def debug_login():
    """Debug the login process"""
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ai_recipe_app_production']
    
    email = 'alan.nunez0310@icloud.com'
    password = 'newpassword123'
    
    print(f"🔍 Debugging login for: {email}")
    print(f"    Password: {password}")
    
    # Step 1: Check if user exists
    user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
    
    if user:
        print(f"✅ User found in database")
        print(f"   Email: {user.get('email')}")
        print(f"   ID: {user.get('id')}")
        print(f"   Verified: {user.get('is_verified')}")
        
        # Step 2: Check password
        stored_hash = user.get('password_hash', '')
        print(f"   Password hash length: {len(stored_hash)}")
        
        # Test password verification
        is_valid = verify_password(password, stored_hash)
        print(f"   Password verification: {is_valid}")
        
        if is_valid:
            print(f"✅ Password is correct!")
            
            # Step 3: Try API login
            print(f"\n🌐 Testing API login...")
            
            login_data = {
                'email': email,
                'password': password
            }
            
            try:
                response = requests.post('http://localhost:8001/api/auth/login', json=login_data)
                print(f"   API Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ API Login successful!")
                    print(f"   User ID: {result.get('user_id')}")
                else:
                    print(f"   ❌ API Login failed: {response.text}")
                    
                    # Check if it's a case sensitivity issue
                    print(f"\n🔍 Checking case sensitivity...")
                    
                    # Try with different case combinations
                    test_emails = [
                        'alan.nunez0310@icloud.com',
                        'Alan.nunez0310@icloud.com',
                        'ALAN.NUNEZ0310@ICLOUD.COM',
                        'alan.nunez0310@ICLOUD.COM'
                    ]
                    
                    for test_email in test_emails:
                        test_login = {
                            'email': test_email,
                            'password': password
                        }
                        
                        test_response = requests.post('http://localhost:8001/api/auth/login', json=test_login)
                        print(f"   Testing {test_email}: {test_response.status_code}")
                        
                        if test_response.status_code == 200:
                            result = test_response.json()
                            print(f"   ✅ SUCCESS with {test_email}!")
                            print(f"   User ID: {result.get('user_id')}")
                            break
                        
            except Exception as e:
                print(f"   ❌ API Error: {str(e)}")
        else:
            print(f"❌ Password verification failed!")
    else:
        print(f"❌ User not found!")
    
    client.close()

async def main():
    print("🔧 Debug Login Process")
    print("=" * 30)
    
    await debug_login()

if __name__ == "__main__":
    asyncio.run(main())
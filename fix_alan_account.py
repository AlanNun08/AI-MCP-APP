#!/usr/bin/env python3
"""
Check and fix user account for Alan.nunez0310@icloud.com
"""
import requests
import json
import os

BACKEND_URL = "http://localhost:8001"

def check_user_exists(email):
    """Check if user exists in database"""
    print(f"🔍 Checking if user exists: {email}")
    
    try:
        # Try to trigger forgot password to see if user exists
        response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json={"email": email})
        print(f"Forgot password response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ User exists: {email}")
            return True
        elif response.status_code == 404:
            print(f"❌ User not found: {email}")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user: {str(e)}")
        return False

def try_login(email, password):
    """Try to login with given credentials"""
    print(f"\n🔐 Attempting login for: {email}")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful!")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"   Email: {user_data.get('email')}")
            return user_data
        else:
            response_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Login failed: {response_data}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def create_user_account(email, password="password123"):
    """Create user account"""
    print(f"\n👤 Creating account for: {email}")
    
    registration_data = {
        "first_name": "Alan",
        "last_name": "Nunez",
        "email": email,
        "password": password,
        "dietary_preferences": ["None"],
        "allergies": ["None"],
        "favorite_cuisines": ["Italian", "Mexican"]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/register", json=registration_data)
        print(f"Registration response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Account created successfully!")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"   Email: {user_data.get('email')}")
            return user_data
        else:
            response_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Registration failed: {response_data}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None

def main():
    """Main function to fix user account"""
    print("🔧 Fixing Alan.nunez0310@icloud.com Account")
    print("=" * 50)
    
    email = "Alan.nunez0310@icloud.com"
    password = "password123"
    
    # Step 1: Check if user exists
    user_exists = check_user_exists(email)
    
    # Step 2: Try login with common passwords
    if user_exists:
        print(f"\n🔐 Trying to login with existing account...")
        
        # Try common passwords
        common_passwords = ["password123", "testpassword", "123456", "alan123", "password"]
        
        for pwd in common_passwords:
            print(f"   Trying password: {pwd}")
            login_result = try_login(email, pwd)
            if login_result:
                print(f"\n🎉 SUCCESS! Login works with password: {pwd}")
                print(f"   You can now login with:")
                print(f"   Email: {email}")
                print(f"   Password: {pwd}")
                return
        
        print(f"\n❌ None of the common passwords worked")
        print(f"🔄 Let's reset the password...")
        
        # Reset password
        reset_response = requests.post(f"{BACKEND_URL}/api/auth/forgot-password", json={"email": email})
        if reset_response.status_code == 200:
            print(f"✅ Password reset email sent!")
            print(f"   Check your email for the reset code")
            print(f"   Or I can help you reset it directly")
        else:
            print(f"❌ Password reset failed: {reset_response.text}")
    
    else:
        print(f"\n👤 User doesn't exist, creating new account...")
        user_data = create_user_account(email, password)
        
        if user_data:
            print(f"\n🎉 SUCCESS! Account created successfully!")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"\n📧 Note: You may need to verify your email address")
            print(f"   Check your email for verification code")
        else:
            print(f"\n❌ Failed to create account")

if __name__ == "__main__":
    main()
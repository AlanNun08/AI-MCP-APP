#!/usr/bin/env python3
"""
Reset password for Alan.nunez0310@icloud.com using reset code
"""
import requests
import json

BACKEND_URL = "http://localhost:8001"

def get_reset_code(email):
    """Get reset code for user (debug function)"""
    print(f"🔍 Getting reset code for: {email}")
    
    try:
        # Try to get reset code from debug endpoint
        response = requests.get(f"{BACKEND_URL}/api/debug/reset-code/{email}")
        print(f"Debug reset code response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            reset_code = data.get('reset_code')
            print(f"✅ Reset code found: {reset_code}")
            return reset_code
        else:
            print(f"❌ Debug endpoint failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting reset code: {str(e)}")
        return None

def reset_password(email, reset_code, new_password):
    """Reset password using reset code"""
    print(f"\n🔄 Resetting password for: {email}")
    
    reset_data = {
        "email": email,
        "reset_code": reset_code,
        "new_password": new_password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/reset-password", json=reset_data)
        print(f"Reset password response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Password reset successful!")
            return True
        else:
            response_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Password reset failed: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ Password reset error: {str(e)}")
        return False

def test_login(email, password):
    """Test login with new password"""
    print(f"\n🔐 Testing login with new password...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"Login test response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Login successful!")
            print(f"   User ID: {user_data.get('user_id')}")
            print(f"   Email: {user_data.get('email')}")
            return True
        else:
            response_data = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"❌ Login failed: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def main():
    """Main function to reset password"""
    print("🔄 Resetting Password for Alan.nunez0310@icloud.com")
    print("=" * 55)
    
    email = "Alan.nunez0310@icloud.com"
    new_password = "newpassword123"
    
    # Step 1: Get reset code
    reset_code = get_reset_code(email)
    
    if reset_code:
        # Step 2: Reset password
        if reset_password(email, reset_code, new_password):
            # Step 3: Test login
            if test_login(email, new_password):
                print(f"\n🎉 SUCCESS! Your account is now ready!")
                print(f"   Email: {email}")
                print(f"   Password: {new_password}")
                print(f"\n📱 You can now login to the app with these credentials!")
            else:
                print(f"\n❌ Password reset worked but login still failed")
        else:
            print(f"\n❌ Password reset failed")
    else:
        print(f"\n❌ Could not get reset code")
        print(f"📧 Please check your email for the reset code")
        print(f"   If you have the code, I can help you reset it manually")

if __name__ == "__main__":
    main()
import requests
import json
import time
import sys
import uuid
import logging
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_email_verification():
    """Test the email verification system with real email sending"""
    base_url = "https://390faeca-fe6c-42c5-afe1-d1d19d490134.preview.emergentagent.com/api"
    
    # Clean up test data
    print("\n" + "=" * 50)
    print("Cleaning up test data")
    print("=" * 50)
    
    response = requests.delete(f"{base_url}/debug/cleanup-test-data")
    print(f"Cleanup response: {response.status_code}")
    
    # Register a new user with a real email
    print("\n" + "=" * 50)
    print("Registering a new user with a real email")
    print("=" * 50)
    
    # Use a real email for testing with a unique identifier
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f"alan.nunez0310+{random_id}@icloud.com"
    test_password = "SecureP@ssw0rd123"
    
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": test_email,
        "password": test_password,
        "dietary_preferences": ["vegetarian"],
        "allergies": ["nuts"],
        "favorite_cuisines": ["italian", "mexican"]
    }
    
    response = requests.post(f"{base_url}/auth/register", json=user_data)
    print(f"Registration response: {response.status_code}")
    
    if response.status_code == 200:
        print("Registration successful!")
        print(response.json())
    else:
        print("Registration failed!")
        print(response.text)
        
    # Get the verification code from the debug endpoint
    print("\n" + "=" * 50)
    print("Getting verification code from debug endpoint")
    print("=" * 50)
    
    response = requests.get(f"{base_url}/debug/verification-codes/{test_email}")
    print(f"Get verification code response: {response.status_code}")
    
    if response.status_code == 200:
        print("Got verification code!")
        verification_data = response.json()
        print(verification_data)
        
        if 'codes' in verification_data and len(verification_data['codes']) > 0:
            verification_code = verification_data['codes'][0]['code']
            print(f"Verification code: {verification_code}")
            
            # Verify the email
            print("\n" + "=" * 50)
            print("Verifying email")
            print("=" * 50)
            
            verify_data = {
                "email": test_email,
                "code": verification_code
            }
            
            response = requests.post(f"{base_url}/auth/verify", json=verify_data)
            print(f"Verification response: {response.status_code}")
            
            if response.status_code == 200:
                print("Verification successful!")
                print(response.json())
                
                # Login with the verified user
                print("\n" + "=" * 50)
                print("Logging in with verified user")
                print("=" * 50)
                
                login_data = {
                    "email": test_email,
                    "password": test_password
                }
                
                response = requests.post(f"{base_url}/auth/login", json=login_data)
                print(f"Login response: {response.status_code}")
                
                if response.status_code == 200:
                    print("Login successful!")
                    print(response.json())
                else:
                    print("Login failed!")
                    print(response.text)
            else:
                print("Verification failed!")
                print(response.text)
        else:
            print("No verification code found!")
    else:
        print("Failed to get verification code!")
        print(response.text)

if __name__ == "__main__":
    test_email_verification()
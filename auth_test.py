import requests
import json
import time
import sys
import uuid
import logging
import re
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackendTester:
    def __init__(self, base_url="https://1896460c-1fcb-418f-bf8d-0da71d07a349.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, timeout=30):
        """Run a single API test with configurable timeout"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        logger.info(f"Testing {name} - {method} {url}")
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            logger.info(f"Request completed in {elapsed_time:.2f} seconds")
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Response: {error_data}")
                    return False, error_data
                except:
                    print(f"Response: {response.text}")
                    return False, {}

        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"❌ Failed - Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            logger.error(f"Request timed out after {elapsed_time:.2f} seconds (timeout set to {timeout}s)")
            return False, {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error: Could not connect to {url}")
            logger.error(f"Connection error: Could not connect to {url}")
            return False, {"error": "Connection error"}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            logger.error(f"Test failed with error: {str(e)}")
            return False, {}

    def test_unverified_user_login_flow(self):
        """Test login with unverified user"""
        # Register a new user but don't verify
        unverified_email = f"unverified_{uuid.uuid4()}@example.com"
        unverified_password = "SecureP@ssw0rd789"
        
        user_data = {
            "first_name": "Unverified",
            "last_name": "User",
            "email": unverified_email,
            "password": unverified_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        # Register the user
        success, _ = self.run_test(
            "Register Unverified User",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            print("❌ Failed to register unverified user")
            return False
        
        # Try to login with unverified user
        login_data = {
            "email": unverified_email,
            "password": unverified_password
        }
        
        # We expect a 200 status code with a special response indicating unverified status
        success, response = self.run_test(
            "Login with Unverified User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        # Check if the response indicates unverified status
        if success and 'status' in response:
            if response['status'] == 'unverified' and response.get('needs_verification', False):
                print("✅ Unverified user login correctly handled with unverified status")
                return True
            else:
                print(f"❌ Unexpected response for unverified user: {response}")
                return False
        
        return success
        
    def test_password_reset_flow(self):
        """Test the complete password reset flow"""
        print("\n" + "=" * 50)
        print("Testing Password Reset Flow")
        print("=" * 50)
        
        # Step 1: Request password reset
        reset_email = f"reset_{uuid.uuid4()}@example.com"
        reset_password = "SecureP@ssw0rd123"
        new_password = "NewSecureP@ssw0rd456"
        
        # First, create a user to reset password for
        user_data = {
            "first_name": "Reset",
            "last_name": "Test",
            "email": reset_email,
            "password": reset_password,
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        # Register the user
        success, _ = self.run_test(
            "Register User for Password Reset",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if not success:
            print("❌ Failed to register user for password reset test")
            return False
        
        # Verify the user (get verification code and verify)
        code_success, code_response = self.run_test(
            "Get Verification Code for Reset Test",
            "GET",
            f"debug/verification-codes/{reset_email}",
            200
        )
        
        if not code_success or 'codes' not in code_response or len(code_response['codes']) == 0:
            print("❌ Failed to get verification code for reset test")
            return False
            
        verification_code = code_response['codes'][0]['code']
        
        # Verify the user
        verify_data = {
            "email": reset_email,
            "code": verification_code
        }
        
        verify_success, _ = self.run_test(
            "Verify User for Reset Test",
            "POST",
            "auth/verify",
            200,
            data=verify_data
        )
        
        if not verify_success:
            print("❌ Failed to verify user for reset test")
            return False
        
        # Step 2: Request password reset
        reset_request = {
            "email": reset_email
        }
        
        reset_success, reset_response = self.run_test(
            "Request Password Reset",
            "POST",
            "auth/forgot-password",
            200,
            data=reset_request
        )
        
        if not reset_success:
            print("❌ Failed to request password reset")
            return False
            
        # Step 3: Get reset code from debug endpoint
        reset_code_success, reset_code_response = self.run_test(
            "Get Password Reset Code",
            "GET",
            f"debug/verification-codes/{reset_email}",
            200
        )
        
        if not reset_code_success:
            print("❌ Failed to get password reset code")
            return False
            
        # Try to get the reset code from the response
        reset_code = None
        if 'last_test_code' in reset_code_response and reset_code_response['last_test_code']:
            reset_code = reset_code_response['last_test_code']
            print(f"✅ Retrieved reset code from last_test_code: {reset_code}")
        elif 'codes' in reset_code_response and len(reset_code_response['codes']) > 0:
            # The verification codes endpoint might return the reset code
            reset_code = reset_code_response['codes'][0]['code']
            print(f"✅ Retrieved reset code from codes: {reset_code}")
        
        if not reset_code:
            print("❌ No reset code found")
            return False
        
        # Step 4: Reset password with code
        reset_verify_data = {
            "email": reset_email,
            "reset_code": reset_code,
            "new_password": new_password
        }
        
        reset_verify_success, reset_verify_response = self.run_test(
            "Reset Password with Code",
            "POST",
            "auth/reset-password",
            200,
            data=reset_verify_data
        )
        
        if not reset_verify_success:
            print("❌ Failed to reset password with code")
            return False
            
        # Step 5: Try to login with new password
        login_data = {
            "email": reset_email,
            "password": new_password
        }
        
        login_success, login_response = self.run_test(
            "Login with New Password",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if login_success and 'status' in login_response and login_response['status'] == 'success':
            print("✅ Successfully logged in with new password")
            return True
        else:
            print("❌ Failed to login with new password")
            return False

def main():
    print("=" * 50)
    print("Backend API Test - Focused on Authentication Features")
    print("=" * 50)
    
    tester = BackendTester()
    
    # Test unverified user login flow
    print("\n" + "=" * 50)
    print("Testing Unverified User Login Flow")
    print("=" * 50)
    unverified_result = tester.test_unverified_user_login_flow()
    
    # Test password reset flow
    print("\n" + "=" * 50)
    print("Testing Password Reset Flow")
    print("=" * 50)
    reset_result = tester.test_password_reset_flow()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"✅ Unverified User Login Flow: {'Passed' if unverified_result else 'Failed'}")
    print(f"✅ Password Reset Flow: {'Passed' if reset_result else 'Failed'}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
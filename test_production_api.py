#!/usr/bin/env python3
"""
Test script to verify backend API is accessible
"""

import requests
import json

def test_backend_api():
    """Test various backend endpoints"""
    
    # Test URLs
    base_urls = [
        "http://localhost:8001",
        "https://buildyoursmartcart.com"
    ]
    
    credentials = {
        "email": "alannunezsilva0310@gmail.com",
        "password": "password123"
    }
    
    print("🔍 Testing Backend API Accessibility")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n🌐 Testing: {base_url}")
        
        try:
            # Test 1: Health check
            print("  📊 Testing health endpoint...")
            response = requests.get(f"{base_url}/api/", timeout=10)
            if response.status_code == 200:
                print("  ✅ Health check: PASSED")
            else:
                print(f"  ❌ Health check: FAILED ({response.status_code})")
            
            # Test 2: Login endpoint
            print("  🔐 Testing login endpoint...")
            response = requests.post(
                f"{base_url}/api/auth/login",
                json=credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("  ✅ Login: PASSED")
                print(f"  👤 User: {data.get('user', {}).get('first_name', 'Unknown')}")
            else:
                print(f"  ❌ Login: FAILED ({response.status_code}) - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Connection Error: {str(e)}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🚀 PRODUCTION DEPLOYMENT INSTRUCTIONS:")
    print("1. Deploy backend to: https://buildyoursmartcart.com/api")
    print("2. Deploy frontend to: https://buildyoursmartcart.com")
    print("3. Set environment variables as per PRODUCTION_DEPLOYMENT_CONFIG.md")
    print("4. Test login with credentials:")
    print(f"   📧 Email: {credentials['email']}")
    print(f"   🔑 Password: {credentials['password']}")
    print("=" * 50)

if __name__ == "__main__":
    test_backend_api()
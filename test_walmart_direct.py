#!/usr/bin/env python3
"""
Direct Walmart API Test for Production Server
Tests if production can reach Walmart API endpoints
"""

import requests
import hashlib
import hmac
import base64
import time
from datetime import datetime

def test_walmart_api_connectivity():
    """Test if production server can reach Walmart API"""
    print("🌐 TESTING WALMART API CONNECTIVITY FROM PRODUCTION")
    print("=" * 60)
    
    # Test basic connectivity to Walmart domain
    print("1️⃣ Testing basic connectivity to Walmart API...")
    try:
        response = requests.get("https://developer.api.walmart.com", timeout=10)
        print(f"✅ Can reach Walmart domain (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Cannot reach Walmart domain: {str(e)}")
        return False
    
    # Test API endpoint specifically
    print("\n2️⃣ Testing Walmart API endpoint...")
    try:
        # This will fail with auth error, but proves network connectivity
        response = requests.get(
            "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query=test",
            timeout=10
        )
        print(f"✅ Can reach API endpoint (Status: {response.status_code})")
        if response.status_code == 401 or response.status_code == 403:
            print("   (Expected auth error - this means endpoint is reachable)")
        return True
    except Exception as e:
        print(f"❌ Cannot reach API endpoint: {str(e)}")
        return False

def generate_walmart_signature_test():
    """Test Walmart signature generation"""
    print("\n3️⃣ TESTING WALMART SIGNATURE GENERATION")
    print("-" * 40)
    
    # These should match your actual production values
    consumer_id = "eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62"
    key_version = "1"
    
    # Test private key (you'll need to verify this matches production)
    private_key = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQChD5cdZ5YhVzu9
4eMXMqPaoHndt8lM8cgdFi3zLxc2CfPr4Ga8TBnz8JmT+dnjXYvz47jeNnLRF95b
udPTwm822W8s+LVIb4mvnD71sSa0eVMoe0r91xtb0viEt0AW2mTkCdK6R8TdQLvz
kcN2z/iHo7u/dEQI3LJUA6tbza7sENpz1TZC9pGtpokpTaC3nrlqFvsXlmTxcDZX
Bvys6JBeyJe7gY//NgaSiHog37MqXHV99VRCjRBOUmp5NcIPi0narqaZo60KRLEC
AGlqZIdPWaMlmMkO+sEeFOCzvqUP5N0UR/EYUqtNZoMrMCzCPowC13FjUCn47k5U
/bea4xjpAgMBAAECggEAAjt9dleAF9Z2EiXSQFkv9vjsM3/ngwDja47KBIHBtjqp
VjrCJcg+wFg0gr3u8JU0ekUM5AyYZxBIAVi4KEpcwQN+xF5uodJE8+mMIFrsHMqF
Ne2Ojqnne8x27Bz/nwl4JkaCFJmnz4LFECVUMp6DlPq2oJrXkhFgCeTSoFc/nk9A
XF+DpAgN1ww/sm/s8TXM4+8TAr+fShkv89qp8LYvK4J6KIdqO+ayidklNXS4/zjL
Gt0yV2OUYoHZYXchjeyAxkE3CCzijI8GddV+vuYE6crPVPvMfSJvDNyCeN9LbWpR
Yxmqg5Oh6GIbQxCgxa6489O6QEJ0Lyj1eF1LgGYiwQKBgQDQd2K/qCLjMiz2TeMg
feFU1DGJ0JPADEXUzGljNnyNmJc4G8saO8HkW8JYqkmsQxm+O3wCCXCF1WnDuMZe
GTDDdzeh6coMmbTCI6CG9S6soyZhObTT5Mm0U0kX/cwXR2rHq7puzvwYFl4a9aEd
7Cy5qRjuQAW5b84bxG8kxgQ9QQKBgQDFyQzBxJZZ3y3585U7Gw78vRRYofdTR+FW
7R1kp/PG1RaEk3fSScLZdLAP5CnkHS7TZcHwKP/b2/BBxVQVWo9znCY7EwEfzcoE
rdfiEKqL2dPlb7YHSmlcvxVi75NItnoRoHq8TwD53Tu6auy0NqFfNlwrbKXNC/3i
XZ0E/DdpqQKBgEa0d1Wx3UNZvU481JAsocR3w+WOTM6SWwz117jCvjP4UTHCm3xm
UDj3tk8EUsCOcajH3COEuBlsbNbpUL6RpKxnPwM3nEPxzhEarFOZzR7YpyfKvr4v
lwoGRYBRoGs02c6nPDBhG7e/vmM+dEsF05WU+NO1+zsN5MYeNeQvFTkBAoGAKF1a
tCTpxles62kR2KkyCtSP1XLgpedyjqn/qK46KycL3Gy4NHuHP5f34pZfEkX+a3hF
9zx20yj0xIeAHIeJ5T9F8iJzxUjbZM8R0voxxC7ldtqwnJZMIHiC5dkdBubuzLAi
vFGnUlcbPHVb73+CuYq/jsEyqUE8RDl0tTLAIFkCgYB8qgvZNpCWUL1Fe9hFXz9D
N/Aor9OBxVySMsceg9ejW7/iUcRsqy4KEQPwMD5dQVbEsjCWFzPZrh53llyi0q6n
w/n0UuoRcmZ7kLrFIOf6ZStmHnZ1BX/6VKD4m9k6O9LSCGxPWhU+k7uqaFnH720g
0Sj9Z58+3ELzkinERznDcg==
-----END PRIVATE KEY-----"""
    
    try:
        print(f"Consumer ID: {consumer_id}")
        print(f"Key Version: {key_version}")
        print(f"Private Key: {'✅ Present' if private_key else '❌ Missing'}")
        
        # Generate signature
        timestamp = str(int(time.time() * 1000))
        string_to_sign = f"{consumer_id}\n{timestamp}\n{key_version}\n"
        
        # Sign the string
        signature = base64.b64encode(
            hmac.new(
                private_key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        print(f"✅ Signature generated successfully")
        print(f"   Timestamp: {timestamp}")
        print(f"   Signature: {signature[:20]}...")
        
        return timestamp, signature
        
    except Exception as e:
        print(f"❌ Signature generation failed: {str(e)}")
        return None, None

def test_walmart_api_call():
    """Test actual Walmart API call"""
    print("\n4️⃣ TESTING ACTUAL WALMART API CALL")
    print("-" * 40)
    
    timestamp, signature = generate_walmart_signature_test()
    
    if not timestamp or not signature:
        print("❌ Cannot test API call - signature generation failed")
        return False
    
    # Test API call
    url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query=milk&numItems=1"
    
    headers = {
        "WM_CONSUMER.ID": "eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62",
        "WM_CONSUMER.INTIMESTAMP": timestamp,
        "WM_SEC.KEY_VERSION": "1",
        "WM_SEC.AUTH_SIGNATURE": signature,
        "Content-Type": "application/json",
        "User-Agent": "BuildYourSmartCart/1.0"
    }
    
    try:
        print(f"🔄 Making API call to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ SUCCESS! Found {len(items)} products")
            
            if items:
                item = items[0]
                print(f"   Sample Product: {item.get('name', 'Unknown')}")
                print(f"   Price: ${item.get('salePrice', 0)}")
                print(f"   Product ID: {item.get('itemId', 'Unknown')}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Authentication failed - check credentials")
            print(f"   Response: {response.text}")
            return False
            
        elif response.status_code == 403:
            print("❌ Forbidden - check API permissions")
            print(f"   Response: {response.text}")
            return False
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API call error: {str(e)}")
        return False

def main():
    """Run complete Walmart API test"""
    print("🚀 WALMART API PRODUCTION TEST")
    print("Testing from buildyoursmartcart.com server")
    print("=" * 60)
    
    results = []
    
    # Test connectivity
    results.append(test_walmart_api_connectivity())
    
    # Test API call
    results.append(test_walmart_api_call())
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if all(results):
        print("🎉 SUCCESS: Walmart API fully functional!")
        print("   The issue may be in the backend code or environment setup")
    else:
        print("❌ ISSUES DETECTED:")
        if not results[0]:
            print("   - Network connectivity to Walmart API failed")
            print("   - Production server cannot reach developer.api.walmart.com")
        if not results[1]:
            print("   - Walmart API authentication failed")
            print("   - Check production environment variables")
    
    print("\n📋 NEXT STEPS:")
    if all(results):
        print("   1. Check backend logs during cart-options calls")
        print("   2. Verify environment variables are loaded correctly")
        print("   3. Test ingredient processing pipeline")
    else:
        print("   1. Fix network/authentication issues first")
        print("   2. Verify production environment variables")
        print("   3. Check server firewall settings")

if __name__ == "__main__":
    main()
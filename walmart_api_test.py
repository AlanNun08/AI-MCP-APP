import requests
import json
import time
import logging
import uuid
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Walmart API credentials
WALMART_CONSUMER_ID = "eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62"
WALMART_KEY_VERSION = "1"
WALMART_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
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

# Backend API URL
BASE_URL = "http://localhost:8001/api"

def get_walmart_signature():
    """Generate Walmart API signature and timestamp"""
    try:
        # Parse private key
        private_key = serialization.load_pem_private_key(
            WALMART_PRIVATE_KEY.encode(),
            password=None
        )
        
        # Generate timestamp
        timestamp = str(int(time.time() * 1000))
        
        # Create message in the correct format: CONSUMER_ID\nTIMESTAMP\nKEY_VERSION\n
        message = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n".encode("utf-8")
        
        # Sign the message
        signature = private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Base64 encode the signature
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        
        return timestamp, signature_b64
        
    except Exception as e:
        logger.error(f"Error generating Walmart signature: {str(e)}")
        raise

def test_direct_walmart_api():
    """Test direct Walmart API call with new credentials and signature method"""
    try:
        # Generate signature and timestamp
        timestamp, signature = get_walmart_signature()
        
        # Prepare API call for a test query
        query = "pasta"
        url = f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query={query}&numItems=3"
        
        headers = {
            "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
            "WM_CONSUMER.INTIMESTAMP": timestamp,
            "WM_SEC.KEY_VERSION": WALMART_KEY_VERSION,
            "WM_SEC.AUTH_SIGNATURE": signature,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Making direct Walmart API call for query: {query}")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Walmart API response status: {response.status_code}")
            
            if 'items' in data:
                items_count = len(data['items'])
                logger.info(f"Found {items_count} items from Walmart API for '{query}'")
                
                # Print the first few items
                for i, item in enumerate(data['items'][:3]):
                    if 'itemId' in item:
                        logger.info(f"Item {i+1}: {item.get('name', 'Unknown')} - ${item.get('salePrice', 0.0)} (ID: {item.get('itemId', 'Unknown')})")
                
                return True, data
            else:
                logger.warning(f"No items found in Walmart API response for '{query}'")
                return False, {"error": "No items found in response"}
        else:
            logger.error(f"Walmart API error: {response.status_code} - {response.text}")
            return False, {"error": f"API error: {response.status_code}", "details": response.text}
            
    except Exception as e:
        logger.error(f"Direct Walmart API test failed: {str(e)}")
        return False, {"error": str(e)}

def test_backend_cart_options():
    """Test the backend cart-options endpoint with a test recipe"""
    try:
        # First, create a test user
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "SecureP@ssw0rd123",
            "dietary_preferences": ["vegetarian"],
            "allergies": [],
            "favorite_cuisines": ["italian"]
        }
        
        logger.info("Creating test user...")
        user_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if user_response.status_code != 200:
            logger.error(f"Failed to create test user: {user_response.status_code} - {user_response.text}")
            return False, {"error": "Failed to create test user"}
        
        user_data = user_response.json()
        user_id = user_data.get('user_id')
        logger.info(f"Created test user with ID: {user_id}")
        
        # Now, create a test recipe with common ingredients
        recipe_request = {
            "user_id": user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        logger.info("Creating test recipe...")
        recipe_response = requests.post(f"{BASE_URL}/recipes/generate", json=recipe_request, timeout=60)
        
        if recipe_response.status_code != 200:
            logger.error(f"Failed to create test recipe: {recipe_response.status_code} - {recipe_response.text}")
            return False, {"error": "Failed to create test recipe"}
        
        recipe_data = recipe_response.json()
        recipe_id = recipe_data.get('id')
        logger.info(f"Created test recipe with ID: {recipe_id}")
        logger.info(f"Recipe ingredients: {recipe_data.get('ingredients', [])}")
        
        # Now test the cart-options endpoint
        logger.info("Testing cart-options endpoint...")
        cart_options_response = requests.post(
            f"{BASE_URL}/grocery/cart-options",
            params={"recipe_id": recipe_id, "user_id": user_id}
        )
        
        if cart_options_response.status_code != 200:
            logger.error(f"Cart options endpoint failed: {cart_options_response.status_code} - {cart_options_response.text}")
            return False, {"error": "Cart options endpoint failed"}
        
        cart_options_data = cart_options_response.json()
        logger.info(f"Cart options response: {json.dumps(cart_options_data, indent=2)}")
        
        # Check if we're getting real Walmart product IDs
        if 'ingredient_options' in cart_options_data:
            real_product_count = 0
            mock_product_count = 0
            
            for ingredient_option in cart_options_data['ingredient_options']:
                if 'options' in ingredient_option:
                    for product in ingredient_option['options']:
                        # Check if this is a real Walmart product ID (typically 8-9 digits)
                        product_id = product.get('product_id', '')
                        if product_id and len(product_id) >= 8 and product_id.isdigit():
                            real_product_count += 1
                        else:
                            mock_product_count += 1
            
            logger.info(f"Found {real_product_count} real product IDs and {mock_product_count} mock product IDs")
            
            if real_product_count > 0:
                logger.info("✅ Successfully retrieved real Walmart product IDs")
            else:
                logger.warning("⚠️ No real Walmart product IDs found - still using mock data")
        
        # Now test the custom-cart endpoint
        logger.info("Testing custom-cart endpoint...")
        
        # Extract some products from the cart options
        products = []
        if 'ingredient_options' in cart_options_data:
            for ingredient_option in cart_options_data['ingredient_options']:
                if 'options' in ingredient_option and len(ingredient_option['options']) > 0:
                    product = ingredient_option['options'][0]
                    products.append({
                        "ingredient_name": ingredient_option.get('ingredient_name', 'Unknown'),
                        "product_id": product.get('product_id', ''),
                        "name": product.get('name', 'Unknown'),
                        "price": product.get('price', 0.0),
                        "quantity": 1
                    })
        
        custom_cart_data = {
            "user_id": user_id,
            "recipe_id": recipe_id,
            "products": products
        }
        
        custom_cart_response = requests.post(
            f"{BASE_URL}/grocery/custom-cart",
            json=custom_cart_data
        )
        
        if custom_cart_response.status_code != 200:
            logger.error(f"Custom cart endpoint failed: {custom_cart_response.status_code} - {custom_cart_response.text}")
            return False, {"error": "Custom cart endpoint failed"}
        
        custom_cart_data = custom_cart_response.json()
        logger.info(f"Custom cart response: {json.dumps(custom_cart_data, indent=2)}")
        
        # Check if the Walmart URL is correctly generated
        if 'walmart_url' in custom_cart_data:
            walmart_url = custom_cart_data['walmart_url']
            logger.info(f"Walmart URL: {walmart_url}")
            
            if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                logger.info("✅ Walmart URL correctly formatted")
                
                # Check if all product IDs are in the URL
                product_ids = [p['product_id'] for p in products]
                all_ids_in_url = all(pid in walmart_url for pid in product_ids)
                if all_ids_in_url:
                    logger.info("✅ All product IDs included in Walmart URL")
                else:
                    logger.warning("⚠️ Not all product IDs found in Walmart URL")
            else:
                logger.warning("⚠️ Walmart URL format may be incorrect")
        
        return True, {
            "cart_options": cart_options_data,
            "custom_cart": custom_cart_data
        }
        
    except Exception as e:
        logger.error(f"Backend cart options test failed: {str(e)}")
        return False, {"error": str(e)}

if __name__ == "__main__":
    print("=" * 80)
    print("WALMART API INTEGRATION TEST")
    print("=" * 80)
    
    # Test direct Walmart API call
    print("\n1. Testing direct Walmart API call with new credentials and signature method...")
    direct_success, direct_result = test_direct_walmart_api()
    
    if direct_success:
        print("✅ Direct Walmart API call successful!")
        if 'items' in direct_result:
            print(f"   Found {len(direct_result['items'])} products")
            for i, item in enumerate(direct_result['items'][:3]):
                print(f"   Product {i+1}: {item.get('name', 'Unknown')} - ${item.get('salePrice', 0.0)} (ID: {item.get('itemId', 'Unknown')})")
    else:
        print("❌ Direct Walmart API call failed!")
        print(f"   Error: {direct_result.get('error', 'Unknown error')}")
        if 'details' in direct_result:
            print(f"   Details: {direct_result['details']}")
    
    # Test backend cart-options endpoint
    print("\n2. Testing backend cart-options endpoint with test recipe...")
    backend_success, backend_result = test_backend_cart_options()
    
    if backend_success:
        print("✅ Backend cart-options endpoint test successful!")
        
        # Check if we're getting real Walmart product IDs
        real_product_count = 0
        mock_product_count = 0
        
        if 'cart_options' in backend_result and 'ingredient_options' in backend_result['cart_options']:
            for ingredient_option in backend_result['cart_options']['ingredient_options']:
                if 'options' in ingredient_option:
                    for product in ingredient_option['options']:
                        # Check if this is a real Walmart product ID (typically 8-9 digits)
                        product_id = product.get('product_id', '')
                        if product_id and len(product_id) >= 8 and product_id.isdigit():
                            real_product_count += 1
                        else:
                            mock_product_count += 1
            
            print(f"   Found {real_product_count} real product IDs and {mock_product_count} mock product IDs")
            
            if real_product_count > 0:
                print("✅ Successfully retrieved real Walmart product IDs")
            else:
                print("⚠️ No real Walmart product IDs found - still using mock data")
        
        # Check if the Walmart URL is correctly generated
        if 'custom_cart' in backend_result and 'walmart_url' in backend_result['custom_cart']:
            walmart_url = backend_result['custom_cart']['walmart_url']
            print(f"   Walmart URL: {walmart_url}")
            
            if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
                print("✅ Walmart URL correctly formatted")
            else:
                print("⚠️ Walmart URL format may be incorrect")
    else:
        print("❌ Backend cart-options endpoint test failed!")
        print(f"   Error: {backend_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Direct Walmart API: {'✅ PASSED' if direct_success else '❌ FAILED'}")
    print(f"Backend Integration: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    
    if direct_success and backend_success:
        print("\n✅ OVERALL: WALMART API INTEGRATION IS WORKING CORRECTLY")
    elif direct_success and not backend_success:
        print("\n⚠️ OVERALL: DIRECT API WORKS BUT BACKEND INTEGRATION HAS ISSUES")
    elif not direct_success and backend_success:
        print("\n⚠️ OVERALL: BACKEND INTEGRATION WORKS BUT DIRECT API HAS ISSUES")
    else:
        print("\n❌ OVERALL: WALMART API INTEGRATION IS NOT WORKING")
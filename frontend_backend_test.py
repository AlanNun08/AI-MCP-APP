import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_frontend_backend_integration():
    """Test if the frontend is correctly configured to call the backend API"""
    
    # Get the backend URL from the frontend .env file
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            
        # Extract REACT_APP_BACKEND_URL
        import re
        match = re.search(r'REACT_APP_BACKEND_URL=(.+)', env_content)
        if match:
            backend_url = match.group(1).strip()
            logger.info(f"Found backend URL in frontend .env: {backend_url}")
        else:
            logger.error("Could not find REACT_APP_BACKEND_URL in frontend .env")
            return False
    except Exception as e:
        logger.error(f"Error reading frontend .env file: {str(e)}")
        return False
    
    # Test if the backend URL is accessible
    try:
        response = requests.get(f"{backend_url}/api", timeout=5)
        if response.status_code == 200:
            logger.info(f"Backend API is accessible at {backend_url}/api")
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"Backend API returned status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error connecting to backend API: {str(e)}")
        return False
    
    # Test the grocery cart options endpoint with sample data
    try:
        # Create a test user
        user_data = {
            "name": "Test User",
            "email": "test_user@example.com",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": []
        }
        
        user_response = requests.post(f"{backend_url}/api/users", json=user_data, timeout=5)
        if user_response.status_code != 200:
            logger.error(f"Failed to create test user: {user_response.status_code}")
            logger.error(f"Response: {user_response.text}")
            return False
        
        user_id = user_response.json().get('id')
        if not user_id:
            logger.error("No user ID returned from user creation")
            return False
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # Create a test recipe
        recipe_request = {
            "user_id": user_id,
            "cuisine_type": "mexican",
            "dietary_preferences": [],
            "ingredients_on_hand": [
                "bell pepper",
                "cumin",
                "chili powder",
                "tortillas",
                "avocado",
                "cheese",
                "cilantro",
                "lime",
                "salt",
                "pepper",
                "chicken"
            ],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "medium"
        }
        
        recipe_response = requests.post(f"{backend_url}/api/recipes/generate", json=recipe_request, timeout=60)
        if recipe_response.status_code != 200:
            logger.error(f"Failed to generate recipe: {recipe_response.status_code}")
            logger.error(f"Response: {recipe_response.text}")
            return False
        
        recipe_id = recipe_response.json().get('id')
        if not recipe_id:
            logger.error("No recipe ID returned from recipe generation")
            return False
        
        logger.info(f"Generated recipe with ID: {recipe_id}")
        
        # Test the grocery cart options endpoint
        cart_options_url = f"{backend_url}/api/grocery/cart-options?recipe_id={recipe_id}&user_id={user_id}"
        logger.info(f"Testing grocery cart options endpoint: {cart_options_url}")
        
        cart_options_response = requests.post(cart_options_url, timeout=10)
        if cart_options_response.status_code != 200:
            logger.error(f"Failed to get grocery cart options: {cart_options_response.status_code}")
            logger.error(f"Response: {cart_options_response.text}")
            return False
        
        cart_options = cart_options_response.json()
        if 'ingredient_options' not in cart_options:
            logger.error("No ingredient_options in cart options response")
            logger.error(f"Response: {cart_options}")
            return False
        
        logger.info(f"Successfully retrieved grocery cart options with {len(cart_options['ingredient_options'])} ingredients")
        
        # Test the custom cart endpoint
        products = []
        for ingredient_option in cart_options['ingredient_options']:
            if 'options' in ingredient_option and len(ingredient_option['options']) > 0:
                product = ingredient_option['options'][0]
                products.append({
                    "ingredient_name": ingredient_option.get('ingredient_name', 'Unknown'),
                    "product_id": product.get('product_id', ''),
                    "name": product.get('name', ''),
                    "price": product.get('price', 0),
                    "quantity": 1
                })
        
        custom_cart_data = {
            "user_id": user_id,
            "recipe_id": recipe_id,
            "products": products
        }
        
        custom_cart_response = requests.post(f"{backend_url}/api/grocery/custom-cart", json=custom_cart_data, timeout=10)
        if custom_cart_response.status_code != 200:
            logger.error(f"Failed to create custom cart: {custom_cart_response.status_code}")
            logger.error(f"Response: {custom_cart_response.text}")
            return False
        
        custom_cart = custom_cart_response.json()
        if 'walmart_url' not in custom_cart:
            logger.error("No walmart_url in custom cart response")
            logger.error(f"Response: {custom_cart}")
            return False
        
        logger.info(f"Successfully created custom cart with Walmart URL: {custom_cart['walmart_url']}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing grocery cart functionality: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("Testing Frontend-Backend Integration for Grocery Cart Functionality")
    print("=" * 80)
    
    success = test_frontend_backend_integration()
    
    if success:
        print("\n✅ Frontend-Backend integration is working correctly for grocery cart functionality")
        print("The issue may be with the frontend UI or event handling")
    else:
        print("\n❌ There are issues with the Frontend-Backend integration for grocery cart functionality")
        print("Check the logs above for details on what's failing")
    
    sys.exit(0 if success else 1)
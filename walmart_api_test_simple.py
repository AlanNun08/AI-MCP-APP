import requests
import json
import time
import logging
import uuid
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backend API URL
BASE_URL = "http://localhost:8001/api"

def test_walmart_api_integration():
    """Test the Walmart API integration with the new credentials and signature method"""
    print("=" * 80)
    print("WALMART API INTEGRATION TEST")
    print("=" * 80)
    
    # Step 1: Create a test user
    print("\n1. Creating test user...")
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "SecureP@ssw0rd123",
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["italian"]
    }
    
    try:
        user_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if user_response.status_code != 200:
            print(f"❌ Failed to create test user: {user_response.status_code} - {user_response.text}")
            return False
        
        user_data = user_response.json()
        user_id = user_data.get('user_id')
        print(f"✅ Created test user with ID: {user_id}")
        
        # Step 2: Create a test recipe with common ingredients
        print("\n2. Creating test recipe with common ingredients: pasta, tomatoes, garlic...")
        recipe_request = {
            "user_id": user_id,
            "cuisine_type": "italian",
            "dietary_preferences": ["vegetarian"],
            "ingredients_on_hand": ["pasta", "tomatoes", "garlic"],
            "prep_time_max": 30,
            "servings": 2,
            "difficulty": "easy"
        }
        
        recipe_response = requests.post(f"{BASE_URL}/recipes/generate", json=recipe_request, timeout=60)
        if recipe_response.status_code != 200:
            print(f"❌ Failed to create test recipe: {recipe_response.status_code} - {recipe_response.text}")
            return False
        
        recipe_data = recipe_response.json()
        recipe_id = recipe_data.get('id')
        print(f"✅ Created test recipe with ID: {recipe_id}")
        print(f"Recipe title: {recipe_data.get('title', 'Untitled')}")
        print(f"Recipe ingredients: {recipe_data.get('ingredients', [])}")
        
        # Step 3: Test the cart-options endpoint
        print("\n3. Testing cart-options endpoint...")
        cart_options_response = requests.post(
            f"{BASE_URL}/grocery/cart-options",
            params={"recipe_id": recipe_id, "user_id": user_id}
        )
        
        if cart_options_response.status_code != 200:
            print(f"❌ Cart options endpoint failed: {cart_options_response.status_code} - {cart_options_response.text}")
            return False
        
        cart_options_data = cart_options_response.json()
        
        # Check if we're getting real Walmart product IDs
        real_product_ids = []
        mock_product_ids = []
        
        if 'ingredient_options' in cart_options_data:
            for ingredient_option in cart_options_data['ingredient_options']:
                ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
                
                print(f"Ingredient: {original_ingredient} ({ingredient_name})")
                
                if 'options' in ingredient_option:
                    for product in ingredient_option['options']:
                        product_id = product.get('product_id', '')
                        product_name = product.get('name', 'Unknown')
                        product_price = product.get('price', 0.0)
                        
                        print(f"  - Product: {product_name} - ${product_price} (ID: {product_id})")
                        
                        # Check if this is a real Walmart product ID (typically 8-9 digits)
                        if product_id and len(product_id) >= 8 and product_id.isdigit():
                            real_product_ids.append(product_id)
                        else:
                            mock_product_ids.append(product_id)
        
        print(f"\nFound {len(real_product_ids)} real product IDs and {len(mock_product_ids)} mock product IDs")
        
        if len(real_product_ids) > 0:
            print("✅ Successfully retrieved real Walmart product IDs")
        else:
            print("⚠️ No real Walmart product IDs found - still using mock data")
        
        # Step 4: Test the custom-cart endpoint
        print("\n4. Testing custom-cart endpoint...")
        
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
            print(f"❌ Custom cart endpoint failed: {custom_cart_response.status_code} - {custom_cart_response.text}")
            return False
        
        custom_cart_data = custom_cart_response.json()
        
        # Check if the Walmart URL is correctly generated
        walmart_url = custom_cart_data.get('walmart_url', '')
        total_price = custom_cart_data.get('total_price', 0.0)
        
        print(f"Total price: ${total_price}")
        print(f"Walmart URL: {walmart_url}")
        
        # Check if all product IDs are in the URL
        product_ids_in_url = []
        if 'items=' in walmart_url:
            items_part = walmart_url.split('items=')[1]
            product_ids_in_url = items_part.split(',')
        
        print(f"Product IDs in URL: {product_ids_in_url}")
        
        if 'affil.walmart.com' in walmart_url and 'items=' in walmart_url:
            print("✅ Walmart URL correctly formatted")
            
            # Check if all product IDs are in the URL
            product_ids = [p['product_id'] for p in products]
            all_ids_in_url = all(pid in walmart_url for pid in product_ids)
            if all_ids_in_url:
                print("✅ All product IDs included in Walmart URL")
            else:
                print("❌ Not all product IDs found in Walmart URL")
        else:
            print("❌ Walmart URL format may be incorrect")
        
        # Final summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Real Walmart Product IDs: {'✅ FOUND' if len(real_product_ids) > 0 else '❌ NOT FOUND'}")
        print(f"Walmart URL Generation: {'✅ CORRECT' if 'affil.walmart.com' in walmart_url else '❌ INCORRECT'}")
        print(f"Product IDs in URL: {'✅ ALL INCLUDED' if all_ids_in_url else '❌ SOME MISSING'}")
        
        if len(real_product_ids) > 0 and 'affil.walmart.com' in walmart_url and all_ids_in_url:
            print("\n✅ OVERALL: WALMART API INTEGRATION IS WORKING CORRECTLY WITH REAL PRODUCT IDs")
            return True
        elif 'affil.walmart.com' in walmart_url and all_ids_in_url:
            print("\n⚠️ OVERALL: WALMART API INTEGRATION IS WORKING BUT STILL USING MOCK PRODUCT IDs")
            return False
        else:
            print("\n❌ OVERALL: WALMART API INTEGRATION HAS ISSUES")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_walmart_api_integration()
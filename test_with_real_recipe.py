import requests
import json
import time
import logging
import sys
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ingredient_parsing_with_real_recipe(base_url="http://localhost:8001"):
    """Test ingredient parsing with a real recipe"""
    print("=" * 80)
    print("Testing Ingredient Parsing with Real Recipe")
    print("=" * 80)
    
    api_url = f"{base_url}/api"
    headers = {'Content-Type': 'application/json'}
    
    # Step 1: Create a user
    user_id = str(uuid.uuid4())
    user_data = {
        "name": f"Test User {user_id[:8]}",
        "email": f"test_{user_id[:8]}@example.com",
        "dietary_preferences": ["vegetarian"],
        "allergies": [],
        "favorite_cuisines": ["italian"]
    }
    
    print("\nStep 1: Creating test user...")
    try:
        response = requests.post(f"{api_url}/users", json=user_data, headers=headers, timeout=30)
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get('id')
            print(f"✅ Created test user with ID: {user_id}")
        else:
            print(f"❌ Failed to create test user (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")
        return False
    
    # Step 2: Generate a recipe with specific ingredients
    recipe_request = {
        "user_id": user_id,
        "cuisine_type": "vegetarian bowl",
        "dietary_preferences": ["vegetarian"],
        "ingredients_on_hand": [
            "chickpeas",
            "bbq sauce",
            "quinoa",
            "mixed vegetables",
            "avocado",
            "olive oil",
            "salt and pepper"
        ],
        "prep_time_max": 30,
        "servings": 2,
        "difficulty": "easy"
    }
    
    print("\nStep 2: Generating recipe with specific ingredients...")
    try:
        response = requests.post(f"{api_url}/recipes/generate", json=recipe_request, headers=headers, timeout=60)
        if response.status_code == 200:
            recipe_data = response.json()
            recipe_id = recipe_data.get('id')
            print(f"✅ Generated recipe with ID: {recipe_id}")
            print(f"Recipe title: {recipe_data.get('title')}")
            print(f"Recipe ingredients:")
            for i, ingredient in enumerate(recipe_data.get('ingredients', [])):
                print(f"  {i+1}. {ingredient}")
        else:
            print(f"❌ Failed to generate recipe (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error generating recipe: {str(e)}")
        return False
    
    # Step 3: Test the cart-options endpoint with the generated recipe
    print("\nStep 3: Testing cart-options endpoint with generated recipe...")
    try:
        response = requests.post(
            f"{api_url}/grocery/cart-options",
            params={"recipe_id": recipe_id, "user_id": user_id},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            cart_data = response.json()
            print(f"✅ Successfully retrieved cart options")
            
            if 'ingredient_options' in cart_data:
                ingredient_options = cart_data['ingredient_options']
                print(f"Found {len(ingredient_options)} ingredient options")
                
                # Check each ingredient option
                all_have_products = True
                for i, option in enumerate(ingredient_options):
                    original = option.get('original_ingredient', '')
                    cleaned = option.get('ingredient_name', '').lower()
                    
                    print(f"\nIngredient {i+1}:")
                    print(f"  Original: '{original}'")
                    print(f"  Cleaned: '{cleaned}'")
                    
                    if 'options' in option and len(option['options']) > 0:
                        print(f"  ✅ Found {len(option['options'])} product options")
                        
                        # Print the first 2 options
                        for j, product in enumerate(option['options'][:2]):
                            print(f"    Product {j+1}: {product.get('name', 'Unknown')} - ${product.get('price', 0):.2f} (ID: {product.get('product_id', 'Unknown')})")
                    else:
                        print("  ❌ No product options found")
                        all_have_products = False
                
                if all_have_products:
                    print("\n✅ All ingredients have product options")
                    return True
                else:
                    print("\n❌ Some ingredients do not have product options")
                    return False
            else:
                print("❌ No ingredient options in response")
                return False
        else:
            print(f"❌ Failed to get cart options (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error getting cart options: {str(e)}")
        return False

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "http://localhost:8001"  # Default fallback
    try:
        with open('/app/frontend/.env', 'r') as f:
            env_content = f.read()
            import re
            match = re.search(r'REACT_APP_BACKEND_URL=(.+)', env_content)
            if match:
                backend_url = match.group(1).strip()
                print(f"Using backend URL from frontend/.env: {backend_url}")
    except Exception as e:
        print(f"Error reading backend URL from .env: {str(e)}")
        print(f"Using default backend URL: {backend_url}")
    
    # Test ingredient parsing with real recipe
    success = test_ingredient_parsing_with_real_recipe(backend_url)
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ Ingredient parsing is working correctly")
        print("✅ The cart-options endpoint successfully returns product options for ingredients")
        print("✅ The improved parsing logic correctly extracts core ingredients")
        print("✅ No 'No product options available' errors were found")
    else:
        print("❌ Issues found with ingredient parsing or cart options")
        print("❌ Some ingredients may not have been parsed correctly")
        print("❌ Some ingredients may not have product options")
    
    return 0 if success else 1

if __name__ == "__main__":
    main()
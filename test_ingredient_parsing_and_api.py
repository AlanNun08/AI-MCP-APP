import sys
import os
import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to the path so we can import the server module
sys.path.append('/app/backend')

# Import the _extract_core_ingredient function from server.py
try:
    from server import _extract_core_ingredient
    print("Successfully imported _extract_core_ingredient function")
except ImportError as e:
    print(f"Error importing _extract_core_ingredient: {e}")
    sys.exit(1)

def test_ingredient_parsing():
    """Test the _extract_core_ingredient function with specific ingredients"""
    print("=" * 80)
    print("Testing Ingredient Parsing Function")
    print("=" * 80)
    
    # Test ingredients from the user's request
    test_ingredients = [
        "1 can chickpeas, drained and rinsed",
        "1/2 cup BBQ sauce",
        "1 cup cooked quinoa",
        "1 cup mixed vegetables (bell peppers, zucchini, onions)",
        "1 avocado, sliced",
        "2 tbsp olive oil",
        "Salt and pepper to taste"
    ]
    
    # Expected core ingredients
    expected_results = [
        "chickpeas",
        "barbecue sauce",  # or "bbq sauce"
        "quinoa",
        "mixed vegetables",  # or "frozen mixed vegetables"
        "avocado",
        "olive oil",
        "salt pepper"
    ]
    
    # Test each ingredient
    all_passed = True
    parsed_ingredients = []
    
    for i, ingredient in enumerate(test_ingredients):
        print(f"\nTesting ingredient {i+1}: '{ingredient}'")
        
        # Call the function
        result = _extract_core_ingredient(ingredient)
        parsed_ingredients.append(result)
        print(f"  Result: '{result}'")
        
        # Check if the result matches the expected value
        expected = expected_results[i]
        if expected in result or result in expected:
            print(f"  ✅ PASS: Found expected core ingredient '{expected}'")
        else:
            print(f"  ❌ FAIL: Expected '{expected}', got '{result}'")
            all_passed = False
    
    # Print summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All ingredient parsing tests PASSED")
    else:
        print("❌ Some ingredient parsing tests FAILED")
    print("=" * 50)
    
    return all_passed, parsed_ingredients

def test_walmart_api_for_parsed_ingredients(parsed_ingredients, base_url="http://localhost:8001"):
    """Test if the Walmart API can find products for the parsed ingredients"""
    print("\n" + "=" * 80)
    print("Testing Walmart API for Parsed Ingredients")
    print("=" * 80)
    
    api_url = f"{base_url}/api/grocery/cart-options"
    headers = {'Content-Type': 'application/json'}
    
    # Create a test recipe with the parsed ingredients
    recipe = {
        "id": "test_recipe_id",
        "title": "Test Recipe",
        "ingredients": parsed_ingredients,
        "user_id": "test_user_id"
    }
    
    # Test each ingredient individually
    all_have_products = True
    
    for i, ingredient in enumerate(parsed_ingredients):
        print(f"\nTesting Walmart API for ingredient {i+1}: '{ingredient}'")
        
        # Create a recipe with just this ingredient
        single_ingredient_recipe = {
            "id": f"test_recipe_{i}",
            "title": f"Test Recipe {i}",
            "ingredients": [ingredient],
            "user_id": "test_user_id"
        }
        
        # Call the cart-options endpoint
        try:
            start_time = time.time()
            response = requests.post(
                api_url,
                json=single_ingredient_recipe,
                headers=headers,
                params={"recipe_id": single_ingredient_recipe["id"], "user_id": "test_user_id"},
                timeout=30
            )
            elapsed_time = time.time() - start_time
            
            print(f"  API call completed in {elapsed_time:.2f} seconds")
            
            if response.status_code == 200:
                print(f"  ✅ API call successful (Status: {response.status_code})")
                
                # Parse the response
                try:
                    data = response.json()
                    
                    if 'ingredient_options' in data and len(data['ingredient_options']) > 0:
                        for option in data['ingredient_options']:
                            if 'options' in option and len(option['options']) > 0:
                                print(f"  ✅ Found {len(option['options'])} product options")
                                
                                # Print the first 2 options
                                for j, product in enumerate(option['options'][:2]):
                                    print(f"    Product {j+1}: {product.get('name', 'Unknown')} - ${product.get('price', 0):.2f} (ID: {product.get('product_id', 'Unknown')})")
                            else:
                                print("  ❌ No product options found")
                                all_have_products = False
                    else:
                        print("  ❌ No ingredient options found")
                        all_have_products = False
                        
                except json.JSONDecodeError:
                    print("  ❌ Failed to parse response JSON")
                    all_have_products = False
            else:
                print(f"  ❌ API call failed (Status: {response.status_code})")
                all_have_products = False
                
        except requests.exceptions.Timeout:
            print("  ❌ API call timed out")
            all_have_products = False
        except requests.exceptions.ConnectionError:
            print("  ❌ Connection error")
            all_have_products = False
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            all_have_products = False
    
    # Print summary
    print("\n" + "=" * 50)
    if all_have_products:
        print("✅ All parsed ingredients have product options")
    else:
        print("❌ Some parsed ingredients do not have product options")
    print("=" * 50)
    
    return all_have_products

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
    
    # Test ingredient parsing
    parsing_success, parsed_ingredients = test_ingredient_parsing()
    
    # Test Walmart API for parsed ingredients
    if parsing_success:
        api_success = test_walmart_api_for_parsed_ingredients(parsed_ingredients, backend_url)
    else:
        api_success = False
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    if parsing_success:
        print("✅ Ingredient parsing function is working correctly")
    else:
        print("❌ Issues found with ingredient parsing function")
    
    if api_success:
        print("✅ Walmart API integration is working correctly")
        print("✅ Product options are found for all parsed ingredients")
    else:
        print("❌ Issues found with Walmart API integration")
        print("❌ Some parsed ingredients do not have product options")
    
    if parsing_success and api_success:
        print("\n✅ OVERALL: The improved ingredient parsing logic is working correctly")
    else:
        print("\n❌ OVERALL: Issues found with the improved ingredient parsing logic")
    
    return 0 if parsing_success and api_success else 1

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
🧪 TESTING THE CLEAN V2 WALMART INTEGRATION
Following MCP App Development Blueprint

This tests the new systematic approach vs old complex system
"""

import requests
import json

def test_v2_health():
    """Test V2 health endpoint"""
    print("🧪 Testing V2 Health Check...")
    try:
        response = requests.get("https://recipe-cart-app-1.emergent.host/api/v2/walmart/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ V2 Health OK - Version: {data.get('version')}, Integration: {data.get('integration')}")
            return True
        else:
            print(f"❌ V2 Health failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ V2 Health error: {str(e)}")
        return False

def test_v2_cart_options():
    """Test V2 cart options with clean implementation"""
    print("\n🧪 Testing V2 Cart Options...")
    
    # Use existing demo user and generate fresh recipe
    user_id = 'b53d3389-cfa2-4201-9689-9eb7b877a7af'
    
    # First generate a recipe
    recipe_data = {
        'user_id': user_id,
        'recipe_category': 'cuisine',
        'cuisine_type': 'Mexican',
        'dietary_preferences': [],
        'ingredients_on_hand': [],
        'prep_time_max': 20,
        'servings': 2,
        'difficulty': 'easy'
    }
    
    try:
        # Generate recipe
        recipe_response = requests.post('https://recipe-cart-app-1.emergent.host/api/recipes/generate', 
                                      json=recipe_data, timeout=30)
        
        if recipe_response.status_code != 200:
            print(f"❌ Recipe generation failed: {recipe_response.status_code}")
            return False
        
        recipe = recipe_response.json()
        recipe_id = recipe.get('id')
        print(f"✅ Recipe generated: {recipe.get('title')} (ID: {recipe_id})")
        
        # Test V2 cart options
        params = {'recipe_id': recipe_id, 'user_id': user_id}
        v2_response = requests.post('https://recipe-cart-app-1.emergent.host/api/v2/walmart/cart-options', 
                                   params=params, timeout=20)
        
        print(f"V2 Cart Options Status: {v2_response.status_code}")
        
        if v2_response.status_code == 200:
            data = v2_response.json()
            version = data.get('version', 'unknown')
            ingredient_matches = data.get('ingredient_matches', [])
            total_products = data.get('total_products', 0)
            
            print(f"✅ V2 Cart Options SUCCESS!")
            print(f"   Version: {version}")
            print(f"   Ingredients processed: {len(ingredient_matches)}")
            print(f"   Total products: {total_products}")
            
            # Show sample data
            if ingredient_matches:
                sample = ingredient_matches[0]
                print(f"   Sample ingredient: {sample.get('ingredient')}")
                products = sample.get('products', [])
                if products:
                    sample_product = products[0]
                    print(f"   Sample product: {sample_product.get('name')} - ${sample_product.get('price')} (ID: {sample_product.get('id')})")
            
            return data
        else:
            print(f"❌ V2 Cart Options failed: {v2_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ V2 Cart Options error: {str(e)}")
        return False

def test_v2_cart_url_generation(cart_data):
    """Test V2 cart URL generation"""
    print("\n🧪 Testing V2 Cart URL Generation...")
    
    if not cart_data or not cart_data.get('ingredient_matches'):
        print("⚠️ No cart data available for URL generation")
        return False
    
    try:
        # Select first product from first 2 ingredients
        selected_products = []
        for match in cart_data.get('ingredient_matches', [])[:2]:
            products = match.get('products', [])
            if products:
                selected_products.append(products[0])
        
        if not selected_products:
            print("⚠️ No products available for URL generation")
            return False
        
        url_request = {
            'selected_products': selected_products
        }
        
        response = requests.post('https://recipe-cart-app-1.emergent.host/api/v2/walmart/generate-cart-url',
                               json=url_request, timeout=10)
        
        print(f"V2 Cart URL Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ V2 Cart URL SUCCESS!")
            print(f"   URL: {data.get('cart_url')}")
            print(f"   Total Price: ${data.get('total_price')}")
            print(f"   Product Count: {data.get('product_count')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ V2 Cart URL failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ V2 Cart URL error: {str(e)}")
        return False

def main():
    """Test complete V2 integration following blueprint"""
    print("🚀 TESTING CLEAN V2 WALMART INTEGRATION")
    print("Following MCP App Development Blueprint")
    print("=" * 60)
    
    # Test Phase 2: Health & Cache
    if not test_v2_health():
        print("❌ V2 Integration not available")
        return False
    
    # Test Phase 3-5: API Integration & State Management
    cart_data = test_v2_cart_options()
    if not cart_data:
        print("❌ V2 Cart Options failed")
        return False
    
    # Test Phase 6: Export & UX
    if not test_v2_cart_url_generation(cart_data):
        print("⚠️ V2 Cart URL generation failed (optional)")
    
    print("\n🎉 V2 INTEGRATION TESTING COMPLETE!")
    print("✅ Clean blueprint-based implementation working!")
    print("🔄 This should show DIFFERENT behavior from old system")
    
    return True

if __name__ == "__main__":
    main()
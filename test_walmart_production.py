#!/usr/bin/env python3
"""
Comprehensive Walmart Integration Test for buildyoursmartcart.com
Tests recipes for cuisine, beverage, and snacks for user Alan.nunez0310@icloud.com
"""

import requests
import json
import time
import sys

class ProductionWalmartTester:
    def __init__(self):
        self.local_url = "http://localhost:8001/api"
        self.production_url = "https://buildyoursmartcart.com/api"
        self.test_user_email = "Alan.nunez0310@icloud.com"
        self.test_user_id = None
        
    def test_environment(self, base_url):
        """Test Walmart integration in specific environment"""
        print(f"\n🌐 Testing environment: {base_url}")
        print("=" * 60)
        
        # Test recipe categories
        categories_to_test = [
            {
                "category": "cuisine",
                "cuisine_type": "italian",
                "name": "Italian Cuisine"
            },
            {
                "category": "beverage", 
                "cuisine_type": "refreshing drinks",
                "name": "Beverage"
            },
            {
                "category": "snack",
                "cuisine_type": "energy snacks", 
                "name": "Snack"
            }
        ]
        
        test_results = []
        
        for category_test in categories_to_test:
            print(f"\n🧪 Testing {category_test['name']} Recipe Generation...")
            
            # Generate recipe
            recipe_data = {
                "user_id": "test-production-user",
                "recipe_category": category_test["category"],
                "cuisine_type": category_test["cuisine_type"],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "easy"
            }
            
            try:
                response = requests.post(
                    f"{base_url}/recipes/generate",
                    json=recipe_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    recipe = response.json()
                    recipe_id = recipe['id']
                    recipe_title = recipe['title']
                    shopping_list = recipe.get('shopping_list', [])
                    
                    print(f"✅ Recipe Generated: {recipe_title}")
                    print(f"   Shopping List: {shopping_list}")
                    
                    # Test Walmart integration
                    print(f"🛒 Testing Walmart Product Search...")
                    
                    cart_response = requests.post(
                        f"{base_url}/grocery/cart-options",
                        params={
                            "recipe_id": recipe_id,
                            "user_id": "test-production-user"
                        },
                        timeout=60
                    )
                    
                    if cart_response.status_code == 200:
                        cart_data = cart_response.json()
                        
                        if 'error' in cart_data:
                            print(f"❌ Walmart Error: {cart_data['error']}")
                            if 'debug_info' in cart_data:
                                debug = cart_data['debug_info']
                                print(f"   Failed ingredients: {debug.get('failed_ingredients', [])}")
                            test_results.append({
                                "category": category_test['name'],
                                "status": "failed",
                                "error": cart_data['error']
                            })
                        else:
                            ingredient_options = cart_data.get('ingredient_options', [])
                            total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                            
                            print(f"✅ Walmart Integration Working!")
                            print(f"   Ingredients with products: {len(ingredient_options)}")
                            print(f"   Total products found: {total_products}")
                            
                            # Show sample products
                            for i, ingredient_opt in enumerate(ingredient_options[:2]):
                                ingredient_name = ingredient_opt.get('ingredient_name', 'Unknown')
                                options = ingredient_opt.get('options', [])
                                print(f"   {ingredient_name}: {len(options)} products")
                                for j, product in enumerate(options[:2]):
                                    name = product.get('name', 'Unknown')
                                    price = product.get('price', 0)
                                    product_id = product.get('product_id', 'Unknown')
                                    print(f"     Product {j+1}: {name} - ${price} (ID: {product_id})")
                            
                            test_results.append({
                                "category": category_test['name'],
                                "status": "success",
                                "ingredients": len(ingredient_options),
                                "products": total_products
                            })
                    else:
                        print(f"❌ Cart Options Failed: {cart_response.status_code}")
                        print(f"   Response: {cart_response.text}")
                        test_results.append({
                            "category": category_test['name'],
                            "status": "cart_failed",
                            "error": f"HTTP {cart_response.status_code}"
                        })
                else:
                    print(f"❌ Recipe Generation Failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    test_results.append({
                        "category": category_test['name'],
                        "status": "recipe_failed",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ Test Error: {str(e)}")
                test_results.append({
                    "category": category_test['name'],
                    "status": "error",
                    "error": str(e)
                })
        
        return test_results
    
    def run_comprehensive_test(self):
        """Run comprehensive tests on both local and production"""
        print("🚀 COMPREHENSIVE WALMART INTEGRATION TEST")
        print("Testing Cuisine, Beverage, and Snacks categories")
        print("For user: Alan.nunez0310@icloud.com")
        print("=" * 80)
        
        # Test local environment
        print("\n📍 LOCAL ENVIRONMENT TEST")
        local_results = self.test_environment(self.local_url)
        
        # Test production environment  
        print("\n📍 PRODUCTION ENVIRONMENT TEST")
        production_results = self.test_environment(self.production_url)
        
        # Compare results
        print("\n📊 COMPARISON RESULTS")
        print("=" * 60)
        
        for i, category in enumerate(['Italian Cuisine', 'Beverage', 'Snack']):
            local_result = local_results[i] if i < len(local_results) else {"status": "not_tested"}
            prod_result = production_results[i] if i < len(production_results) else {"status": "not_tested"}
            
            print(f"\n🍽️ {category}:")
            print(f"   Local:      {local_result.get('status', 'unknown')}")
            print(f"   Production: {prod_result.get('status', 'unknown')}")
            
            if local_result.get('status') == 'success' and prod_result.get('status') != 'success':
                print(f"   ⚠️ Production issue detected!")
                if 'error' in prod_result:
                    print(f"   Error: {prod_result['error']}")
            elif local_result.get('status') == 'success' and prod_result.get('status') == 'success':
                local_products = local_result.get('products', 0)
                prod_products = prod_result.get('products', 0)
                print(f"   ✅ Both working! Local: {local_products} products, Production: {prod_products} products")
        
        # Final recommendations
        print("\n🎯 RECOMMENDATIONS")
        print("=" * 60)
        
        all_prod_working = all(r.get('status') == 'success' for r in production_results)
        
        if all_prod_working:
            print("✅ All categories working in production!")
            print("   Walmart integration is functioning correctly")
        else:
            print("❌ Production issues detected:")
            for result in production_results:
                if result.get('status') != 'success':
                    print(f"   - {result['category']}: {result.get('error', 'Unknown error')}")
            
            print("\n🔧 Suggested fixes:")
            print("   1. Check production environment variables")
            print("   2. Verify Walmart API credentials in production")
            print("   3. Check production database connectivity")
            print("   4. Monitor production logs for API errors")

if __name__ == "__main__":
    tester = ProductionWalmartTester()
    tester.run_comprehensive_test()
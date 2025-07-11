#!/usr/bin/env python3
"""
Production Environment Diagnostic Tool for buildyoursmartcart.com
Tests Walmart API connectivity, environment variables, and user account setup
"""

import requests
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime
import uuid

class ProductionDiagnostic:
    def __init__(self):
        self.production_url = "https://buildyoursmartcart.com/api"
        self.user_email = "Alan.nunez0310@icloud.com"
        self.user_id = None
        
        print("🔍 PRODUCTION ENVIRONMENT DIAGNOSTIC")
        print("🌐 Target: buildyoursmartcart.com")
        print("👤 User: Alan.nunez0310@icloud.com")
        print("=" * 60)

    def test_backend_health(self):
        """Test if production backend is accessible"""
        print("\n1️⃣ BACKEND HEALTH CHECK")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.production_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend accessible")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                return True
            else:
                print(f"❌ Backend error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False

    def test_environment_variables(self):
        """Test production environment variables by creating a debug endpoint call"""
        print("\n2️⃣ ENVIRONMENT VARIABLES CHECK")
        print("-" * 30)
        
        try:
            # Try to access a debug endpoint or make a call that would reveal env issues
            response = requests.get(f"{self.production_url}/debug/env-status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Environment variables accessible")
                for key, value in data.items():
                    if 'API_KEY' in key or 'SECRET' in key:
                        # Mask sensitive data
                        masked = value[:8] + "..." if value else "NOT SET"
                        print(f"   {key}: {masked}")
                    else:
                        print(f"   {key}: {value}")
                return True
            else:
                print("⚠️ Debug endpoint not available (normal for production)")
                print("   Will test environment through API functionality")
                return self.test_walmart_api_directly()
                
        except Exception as e:
            print("⚠️ Direct env check failed, testing through API calls")
            return self.test_walmart_api_directly()

    def test_walmart_api_directly(self):
        """Test Walmart API connectivity from production"""
        print("\n3️⃣ WALMART API CONNECTIVITY TEST")
        print("-" * 30)
        
        # Test by making a recipe and checking cart options
        try:
            print("🔄 Generating test recipe...")
            recipe_data = {
                "user_id": "diagnostic-test-user",
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "easy"
            }
            
            response = requests.post(
                f"{self.production_url}/recipes/generate",
                json=recipe_data,
                timeout=60
            )
            
            if response.status_code == 200:
                recipe = response.json()
                recipe_id = recipe['id']
                shopping_list = recipe.get('shopping_list', [])
                
                print(f"✅ Recipe generated: {recipe['title']}")
                print(f"   Shopping list: {shopping_list}")
                
                if shopping_list:
                    print("\n🛒 Testing Walmart API through cart options...")
                    cart_response = requests.post(
                        f"{self.production_url}/grocery/cart-options",
                        params={
                            "recipe_id": recipe_id,
                            "user_id": "diagnostic-test-user"
                        },
                        timeout=90  # Longer timeout for Walmart API
                    )
                    
                    if cart_response.status_code == 200:
                        cart_data = cart_response.json()
                        
                        if 'error' in cart_data:
                            print(f"❌ Walmart API Error: {cart_data['error']}")
                            if 'debug_info' in cart_data:
                                debug = cart_data['debug_info']
                                print(f"   Failed ingredients: {debug.get('failed_ingredients', [])}")
                            return False
                        else:
                            ingredient_options = cart_data.get('ingredient_options', [])
                            total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                            
                            if total_products > 0:
                                print(f"✅ Walmart API working!")
                                print(f"   Found products for {len(ingredient_options)} ingredients")
                                print(f"   Total products: {total_products}")
                                
                                # Show sample products
                                for opt in ingredient_options[:2]:
                                    ingredient = opt.get('ingredient_name', 'Unknown')
                                    options = opt.get('options', [])
                                    print(f"   {ingredient}: {len(options)} products")
                                    for product in options[:1]:
                                        print(f"     - {product.get('name', 'Unknown')} (${product.get('price', 0)})")
                                
                                return True
                            else:
                                print("❌ Walmart API returning 0 products")
                                print("   This indicates environment variable or network issues")
                                return False
                    else:
                        print(f"❌ Cart options failed: {cart_response.status_code}")
                        print(f"   Response: {cart_response.text}")
                        return False
                else:
                    print("❌ Recipe has no shopping list")
                    return False
            else:
                print(f"❌ Recipe generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Walmart API test failed: {str(e)}")
            return False

    def create_user_account(self):
        """Create user account on production"""
        print("\n4️⃣ USER ACCOUNT SETUP")
        print("-" * 30)
        
        user_data = {
            "first_name": "Alan",
            "last_name": "Nunez",
            "email": self.user_email,
            "password": "TempPassword123!",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["Italian"]
        }
        
        try:
            response = requests.post(
                f"{self.production_url}/auth/register",
                json=user_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('user_id')
                print(f"✅ User account created successfully")
                print(f"   User ID: {self.user_id}")
                print(f"   Email: {self.user_email}")
                print(f"   Password: TempPassword123!")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                print(f"✅ User account already exists")
                print(f"   Email: {self.user_email}")
                print(f"   Try logging in with existing password")
                return True
            else:
                print(f"❌ User creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ User creation error: {str(e)}")
            return False

    def test_user_workflow(self):
        """Test complete user workflow with real account"""
        print("\n5️⃣ COMPLETE USER WORKFLOW TEST")
        print("-" * 30)
        
        if not self.user_id:
            print("⚠️ No user ID available, using test user")
            test_user_id = "alan-test-user"
        else:
            test_user_id = self.user_id
        
        # Test each recipe category
        categories = [
            {"category": "cuisine", "type": "italian", "name": "Italian Cuisine"},
            {"category": "beverage", "type": "refreshing drinks", "name": "Beverage"},
            {"category": "snack", "type": "energy snacks", "name": "Snack"}
        ]
        
        success_count = 0
        
        for cat in categories:
            print(f"\n📋 Testing {cat['name']}...")
            
            recipe_data = {
                "user_id": test_user_id,
                "recipe_category": cat["category"],
                "cuisine_type": cat["type"],
                "dietary_preferences": [],
                "ingredients_on_hand": [],
                "prep_time_max": 30,
                "servings": 4,
                "difficulty": "easy"
            }
            
            try:
                # Generate recipe
                response = requests.post(
                    f"{self.production_url}/recipes/generate",
                    json=recipe_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    recipe = response.json()
                    recipe_id = recipe['id']
                    shopping_list = recipe.get('shopping_list', [])
                    
                    print(f"   ✅ Recipe: {recipe['title']}")
                    print(f"   📦 Ingredients: {len(shopping_list)}")
                    
                    # Test Walmart integration
                    cart_response = requests.post(
                        f"{self.production_url}/grocery/cart-options",
                        params={"recipe_id": recipe_id, "user_id": test_user_id},
                        timeout=90
                    )
                    
                    if cart_response.status_code == 200:
                        cart_data = cart_response.json()
                        
                        if 'error' not in cart_data:
                            ingredient_options = cart_data.get('ingredient_options', [])
                            total_products = sum(len(opt.get('options', [])) for opt in ingredient_options)
                            
                            print(f"   🛒 Walmart: {total_products} products found")
                            
                            if total_products > 0:
                                success_count += 1
                                print(f"   ✅ {cat['name']} WORKING")
                            else:
                                print(f"   ❌ {cat['name']} - No products")
                        else:
                            print(f"   ❌ {cat['name']} - Walmart error: {cart_data['error']}")
                    else:
                        print(f"   ❌ {cat['name']} - Cart failed: {cart_response.status_code}")
                else:
                    print(f"   ❌ {cat['name']} - Recipe failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {cat['name']} - Error: {str(e)}")
        
        return success_count

    def generate_recommendations(self, test_results):
        """Generate specific recommendations based on test results"""
        print("\n🎯 DIAGNOSTIC RECOMMENDATIONS")
        print("=" * 60)
        
        backend_ok = test_results.get('backend', False)
        walmart_ok = test_results.get('walmart', False)
        user_ok = test_results.get('user', False)
        workflow_success = test_results.get('workflow_success', 0)
        
        if not backend_ok:
            print("🚨 CRITICAL: Backend not accessible")
            print("   - Check deployment status")
            print("   - Verify domain configuration")
            print("   - Check server logs")
            
        elif not walmart_ok:
            print("🚨 CRITICAL: Walmart API not working")
            print("   - Check production environment variables:")
            print("     WALMART_CONSUMER_ID=eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62")
            print("     WALMART_KEY_VERSION=1")
            print("     WALMART_PRIVATE_KEY=[your private key]")
            print("   - Check network connectivity to developer.api.walmart.com")
            print("   - Verify production server can make external HTTPS requests")
            
        elif workflow_success == 0:
            print("🚨 CRITICAL: No recipe categories working")
            print("   - All Walmart API calls returning 0 products")
            print("   - Check production environment variables")
            print("   - Monitor backend logs during API calls")
            
        elif workflow_success < 3:
            print("⚠️ PARTIAL: Some categories not working")
            print(f"   - {workflow_success}/3 categories successful")
            print("   - Check specific ingredient processing")
            print("   - May be intermittent API issues")
            
        else:
            print("✅ SUCCESS: All systems working!")
            print("   - Walmart API integration functional")
            print("   - All recipe categories working")
            print("   - Production deployment successful")
        
        print(f"\n📧 User Account Status:")
        if user_ok:
            print(f"   ✅ User: {self.user_email}")
            print(f"   🔑 Password: TempPassword123!")
            print(f"   🌐 Ready to test on: buildyoursmartcart.com")
        else:
            print(f"   ❌ User setup incomplete")
            print(f"   📝 Manual registration may be needed")

    def run_complete_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🚀 Starting Production Diagnostic...")
        
        results = {}
        
        # Test backend
        results['backend'] = self.test_backend_health()
        
        if results['backend']:
            # Test environment/Walmart API
            results['walmart'] = self.test_environment_variables()
            
            # Create user account
            results['user'] = self.create_user_account()
            
            # Test complete workflow
            results['workflow_success'] = self.test_user_workflow()
        else:
            results['walmart'] = False
            results['user'] = False
            results['workflow_success'] = 0
        
        # Generate recommendations
        self.generate_recommendations(results)
        
        return results

if __name__ == "__main__":
    diagnostic = ProductionDiagnostic()
    results = diagnostic.run_complete_diagnostic()
    
    print(f"\n" + "=" * 60)
    print("🏁 DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
    if results['workflow_success'] == 3:
        print("🎉 SUCCESS: Production environment fully functional!")
    else:
        print("🔧 ACTION REQUIRED: Issues detected in production")
        print("   Review recommendations above for next steps")
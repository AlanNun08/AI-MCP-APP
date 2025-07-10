#!/usr/bin/env python3
"""
Focused Beverage Recipe Testing Script
Tests beverage recipe generation and shopping list functionality
"""

import requests
import json
import uuid
import time
from datetime import datetime

class BeverageRecipeTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = f"{base_url}/api"
        self.user_id = None
        self.recipe_id = None
        
    def create_test_user(self):
        """Create a test user for recipe generation"""
        print("🔧 Creating test user...")
        
        # Create legacy user (simpler for testing)
        user_data = {
            "name": f"Beverage Test User {uuid.uuid4()}",
            "email": f"beverage_test_{uuid.uuid4()}@example.com",
            "dietary_preferences": [],
            "allergies": [],
            "favorite_cuisines": ["american"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/users", json=user_data, timeout=10)
            if response.status_code == 200:
                user_response = response.json()
                self.user_id = user_response.get('id')
                print(f"✅ Created test user with ID: {self.user_id}")
                return True
            else:
                print(f"❌ Failed to create user: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return False
    
    def test_beverage_recipe_generation(self):
        """Test beverage recipe generation and examine the response"""
        print("\n" + "=" * 80)
        print("🧋 TESTING BEVERAGE RECIPE GENERATION")
        print("=" * 80)
        
        if not self.user_id:
            print("❌ No user ID available")
            return False
        
        # Create beverage recipe request
        recipe_request = {
            "user_id": self.user_id,
            "recipe_category": "beverage",  # This is the key parameter
            "cuisine_type": "mixed",
            "dietary_preferences": [],
            "ingredients_on_hand": [],
            "prep_time_max": 30,
            "servings": 4,
            "difficulty": "medium"
        }
        
        print("📝 Recipe Request:")
        print(json.dumps(recipe_request, indent=2))
        print("\n🔄 Calling /api/recipes/generate...")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/recipes/generate", 
                json=recipe_request, 
                timeout=60
            )
            elapsed_time = time.time() - start_time
            
            print(f"⏱️ Request completed in {elapsed_time:.2f} seconds")
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                recipe_data = response.json()
                self.recipe_id = recipe_data.get('id')
                
                print("\n" + "=" * 60)
                print("✅ COMPLETE API RESPONSE:")
                print("=" * 60)
                print(json.dumps(recipe_data, indent=2))
                
                print("\n" + "=" * 60)
                print("🔍 DETAILED ANALYSIS:")
                print("=" * 60)
                
                # Analyze the response structure
                print(f"📋 Recipe Title: {recipe_data.get('title', 'N/A')}")
                print(f"📝 Description: {recipe_data.get('description', 'N/A')}")
                print(f"🍽️ Servings: {recipe_data.get('servings', 'N/A')}")
                print(f"⏰ Prep Time: {recipe_data.get('prep_time', 'N/A')} minutes")
                print(f"🔥 Cook Time: {recipe_data.get('cook_time', 'N/A')} minutes")
                print(f"🔥 Calories per Serving: {recipe_data.get('calories_per_serving', 'N/A')}")
                
                # Examine ingredients
                ingredients = recipe_data.get('ingredients', [])
                print(f"\n🧾 INGREDIENTS ({len(ingredients)} items):")
                for i, ingredient in enumerate(ingredients, 1):
                    print(f"  {i}. {ingredient}")
                
                # Examine shopping list
                shopping_list = recipe_data.get('shopping_list', [])
                print(f"\n🛒 SHOPPING LIST ({len(shopping_list)} items):")
                for i, item in enumerate(shopping_list, 1):
                    print(f"  {i}. {item}")
                
                # Compare ingredients vs shopping list
                print(f"\n" + "=" * 60)
                print("📊 INGREDIENTS vs SHOPPING LIST COMPARISON:")
                print("=" * 60)
                
                print("🧾 INGREDIENTS (with quantities and measurements):")
                for i, ingredient in enumerate(ingredients, 1):
                    print(f"  {i}. '{ingredient}'")
                
                print("\n🛒 SHOPPING LIST (clean ingredient names):")
                for i, item in enumerate(shopping_list, 1):
                    print(f"  {i}. '{item}'")
                
                # Analyze cleanliness of shopping list
                print(f"\n🔍 SHOPPING LIST CLEANLINESS ANALYSIS:")
                issues = []
                clean_items = 0
                
                for item in shopping_list:
                    item_issues = []
                    
                    # Check for quantities (numbers at start)
                    if any(char.isdigit() for char in item.split()[0] if item.split()):
                        item_issues.append("contains quantities")
                    
                    # Check for measurements
                    measurements = ['cup', 'cups', 'tbsp', 'tsp', 'oz', 'lb', 'can', 'jar', 'bottle', 'package', 'bag']
                    if any(measure in item.lower() for measure in measurements):
                        item_issues.append("contains measurements")
                    
                    # Check for preparation words
                    prep_words = ['fresh', 'chopped', 'diced', 'sliced', 'minced', 'cooked', 'frozen', 'dried']
                    if any(prep in item.lower() for prep in prep_words):
                        item_issues.append("contains preparation words")
                    
                    if item_issues:
                        issues.append(f"'{item}': {', '.join(item_issues)}")
                    else:
                        clean_items += 1
                        print(f"  ✅ '{item}' - CLEAN")
                
                if issues:
                    print(f"\n  ⚠️ ISSUES FOUND:")
                    for issue in issues:
                        print(f"    - {issue}")
                
                cleanliness_score = (clean_items / len(shopping_list)) * 100 if shopping_list else 0
                print(f"\n📊 CLEANLINESS SCORE: {cleanliness_score:.1f}% ({clean_items}/{len(shopping_list)} items clean)")
                
                if cleanliness_score >= 90:
                    print("🎉 EXCELLENT - Shopping list is very clean!")
                elif cleanliness_score >= 75:
                    print("✅ GOOD - Shopping list is mostly clean")
                elif cleanliness_score >= 50:
                    print("⚠️ FAIR - Shopping list needs improvement")
                else:
                    print("❌ POOR - Shopping list has many issues")
                
                return True
                
            else:
                print(f"❌ Recipe generation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during recipe generation: {str(e)}")
            return False
    
    def test_cart_options(self):
        """Test the grocery cart options endpoint to see ingredient names used for Walmart search"""
        print("\n" + "=" * 80)
        print("🛒 TESTING GROCERY CART OPTIONS")
        print("=" * 80)
        
        if not self.recipe_id or not self.user_id:
            print("❌ No recipe ID or user ID available")
            return False
        
        print(f"🔄 Calling /api/grocery/cart-options with recipe_id={self.recipe_id}, user_id={self.user_id}")
        
        try:
            response = requests.post(
                f"{self.base_url}/grocery/cart-options",
                params={"recipe_id": self.recipe_id, "user_id": self.user_id},
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                cart_data = response.json()
                
                print("\n" + "=" * 60)
                print("✅ CART OPTIONS RESPONSE:")
                print("=" * 60)
                print(json.dumps(cart_data, indent=2))
                
                print("\n" + "=" * 60)
                print("🔍 WALMART SEARCH ANALYSIS:")
                print("=" * 60)
                
                ingredient_options = cart_data.get('ingredient_options', [])
                print(f"📊 Found {len(ingredient_options)} ingredients with Walmart options")
                
                real_product_count = 0
                mock_product_count = 0
                
                for i, ingredient_option in enumerate(ingredient_options, 1):
                    ingredient_name = ingredient_option.get('ingredient_name', 'Unknown')
                    original_ingredient = ingredient_option.get('original_ingredient', 'Unknown')
                    options = ingredient_option.get('options', [])
                    
                    print(f"\n🧾 Ingredient {i}: '{ingredient_name}'")
                    print(f"   Original: '{original_ingredient}'")
                    print(f"   Walmart Options ({len(options)} found):")
                    
                    for j, option in enumerate(options, 1):
                        product_id = option.get('product_id', 'N/A')
                        name = option.get('name', 'N/A')
                        price = option.get('price', 0)
                        
                        # Determine if this is a real or mock product
                        if len(product_id) >= 8 and product_id.isdigit():
                            product_type = "🟢 REAL"
                            real_product_count += 1
                        else:
                            product_type = "🔵 MOCK"
                            mock_product_count += 1
                        
                        print(f"     {j}. {product_type} - {name} - ${price:.2f} (ID: {product_id})")
                
                print(f"\n📊 WALMART API RESULTS:")
                print(f"   🟢 Real Walmart Products: {real_product_count}")
                print(f"   🔵 Mock Products: {mock_product_count}")
                print(f"   📈 Real Product Rate: {(real_product_count / (real_product_count + mock_product_count) * 100):.1f}%")
                
                if real_product_count > mock_product_count:
                    print("✅ EXCELLENT - Mostly real Walmart products found!")
                elif real_product_count > 0:
                    print("✅ GOOD - Some real Walmart products found")
                else:
                    print("⚠️ WARNING - No real Walmart products found (using mock data)")
                
                return True
                
            else:
                print(f"❌ Cart options failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during cart options test: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Run the complete beverage testing suite"""
        print("🧋 BEVERAGE RECIPE TESTING SUITE")
        print("=" * 80)
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Create test user
        if not self.create_test_user():
            print("❌ Failed to create test user - cannot continue")
            return False
        
        # Step 2: Test beverage recipe generation
        recipe_success = self.test_beverage_recipe_generation()
        
        # Step 3: Test cart options (only if recipe generation succeeded)
        cart_success = False
        if recipe_success and self.recipe_id:
            cart_success = self.test_cart_options()
        else:
            print("\n⚠️ Skipping cart options test - no recipe ID available")
        
        # Final summary
        print("\n" + "=" * 80)
        print("📋 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"✅ User Creation: {'PASSED' if self.user_id else 'FAILED'}")
        print(f"✅ Beverage Recipe Generation: {'PASSED' if recipe_success else 'FAILED'}")
        print(f"✅ Cart Options Test: {'PASSED' if cart_success else 'FAILED' if recipe_success else 'SKIPPED'}")
        
        overall_success = recipe_success and (cart_success or not recipe_success)
        print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        return overall_success

if __name__ == "__main__":
    tester = BeverageRecipeTester()
    success = tester.run_complete_test()
    exit(0 if success else 1)
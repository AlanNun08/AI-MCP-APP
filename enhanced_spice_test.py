#!/usr/bin/env python3
"""
Enhanced Spice Naming Test Script
Focus: Test the improved spice naming in recipes and Walmart integration
"""

import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
BACKEND_URL = "https://7231aef0-71b1-4397-ae8c-9cb5a059a118.preview.emergentagent.com/api"
DEMO_USER_EMAIL = "demo@test.com"
DEMO_USER_PASSWORD = "password123"

class EnhancedSpiceTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.user_id = None
        
    async def cleanup(self):
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_demo_authentication(self):
        """Test 1: Verify demo@test.com/password123 login works"""
        self.log("=== Testing Demo Authentication ===")
        
        try:
            login_data = {
                "email": DEMO_USER_EMAIL,
                "password": DEMO_USER_PASSWORD
            }
            
            response = await self.client.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    self.user_id = result.get("user_id") or result.get("user", {}).get("id")
                    user_email = result.get("user", {}).get("email", "Unknown")
                    is_verified = result.get("user", {}).get("is_verified", False)
                    
                    self.log(f"✅ Demo authentication successful")
                    self.log(f"User ID: {self.user_id}")
                    self.log(f"Email: {user_email}")
                    self.log(f"Verified: {is_verified}")
                    
                    return True
                else:
                    self.log(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error during authentication: {str(e)}", "ERROR")
            return False
    
    async def test_spice_heavy_recipe_generation(self):
        """Test 2: Generate spice-heavy recipes and verify individual spice names"""
        self.log("=== Testing Spice-Heavy Recipe Generation ===")
        
        if not self.user_id:
            self.log("❌ No user_id available for recipe generation")
            return False
        
        # Test different spice-heavy cuisines
        test_recipes = [
            {
                "name": "Indian Chicken Curry",
                "cuisine_type": "Indian",
                "expected_spices": ["turmeric", "cumin", "coriander", "garam masala", "cardamom", "cinnamon", "cloves"]
            },
            {
                "name": "Italian Pasta Arrabbiata", 
                "cuisine_type": "Italian",
                "expected_spices": ["oregano", "basil", "red pepper flakes", "black pepper", "garlic powder"]
            },
            {
                "name": "Indian Biryani",
                "cuisine_type": "Indian", 
                "expected_spices": ["saffron", "bay leaves", "star anise", "cinnamon", "cardamom", "cloves", "cumin"]
            }
        ]
        
        results = {}
        
        for recipe_test in test_recipes:
            self.log(f"--- Testing {recipe_test['name']} ---")
            
            try:
                recipe_data = {
                    "user_id": self.user_id,
                    "recipe_category": "cuisine",
                    "cuisine_type": recipe_test["cuisine_type"],
                    "dietary_preferences": [],
                    "ingredients_on_hand": [],
                    "prep_time_max": 60,
                    "servings": 4,
                    "difficulty": "medium"
                }
                
                response = await self.client.post(f"{BACKEND_URL}/recipes/generate", json=recipe_data)
                
                if response.status_code == 200:
                    result = response.json()
                    recipe_title = result.get("title", "Unknown")
                    shopping_list = result.get("shopping_list", [])
                    instructions = result.get("instructions", [])
                    
                    self.log(f"✅ Recipe generated: {recipe_title}")
                    self.log(f"Shopping list ({len(shopping_list)} items): {shopping_list}")
                    
                    # Analyze spice naming
                    spice_analysis = self.analyze_spice_naming(shopping_list, recipe_test["expected_spices"])
                    results[recipe_test["name"]] = {
                        "recipe": result,
                        "spice_analysis": spice_analysis
                    }
                    
                    # Log spice analysis
                    self.log(f"Spice Analysis:")
                    self.log(f"  Individual spices found: {spice_analysis['individual_spices']}")
                    self.log(f"  Generic terms found: {spice_analysis['generic_terms']}")
                    self.log(f"  Specific spices detected: {spice_analysis['specific_spices_count']}")
                    self.log(f"  Generic spice terms: {spice_analysis['generic_spice_count']}")
                    
                    # Check if instructions are generated
                    if instructions:
                        self.log(f"✅ Recipe instructions generated ({len(instructions)} steps)")
                    else:
                        self.log(f"❌ No recipe instructions generated")
                    
                else:
                    self.log(f"❌ Recipe generation failed: {response.status_code} - {response.text}")
                    results[recipe_test["name"]] = {"error": response.text}
                    
            except Exception as e:
                self.log(f"❌ Error generating {recipe_test['name']}: {str(e)}", "ERROR")
                results[recipe_test["name"]] = {"error": str(e)}
        
        return results
    
    def analyze_spice_naming(self, shopping_list: List[str], expected_spices: List[str]) -> Dict[str, Any]:
        """Analyze the shopping list for specific vs generic spice naming"""
        
        # Common individual spices to look for
        individual_spices = [
            "turmeric", "cumin", "coriander", "paprika", "garam masala", "oregano", 
            "basil", "thyme", "rosemary", "sage", "cardamom", "cinnamon", "cloves",
            "bay leaves", "saffron", "star anise", "fennel", "mustard seeds",
            "red pepper flakes", "black pepper", "white pepper", "garlic powder",
            "onion powder", "chili powder", "cayenne", "nutmeg", "allspice"
        ]
        
        # Generic terms that should be avoided
        generic_terms = [
            "spices", "mixed spices", "seasoning", "seasoning blend", "italian seasoning",
            "curry powder", "spice mix", "herbs", "mixed herbs", "herb blend"
        ]
        
        # Convert shopping list to lowercase for analysis
        shopping_list_lower = [item.lower() for item in shopping_list]
        
        # Find individual spices
        found_individual_spices = []
        for spice in individual_spices:
            for item in shopping_list_lower:
                if spice in item:
                    found_individual_spices.append(spice)
                    break
        
        # Find generic terms
        found_generic_terms = []
        for term in generic_terms:
            for item in shopping_list_lower:
                if term in item:
                    found_generic_terms.append(term)
                    break
        
        # Check for expected spices
        found_expected_spices = []
        for expected in expected_spices:
            for item in shopping_list_lower:
                if expected.lower() in item:
                    found_expected_spices.append(expected)
                    break
        
        return {
            "individual_spices": found_individual_spices,
            "generic_terms": found_generic_terms,
            "expected_spices_found": found_expected_spices,
            "specific_spices_count": len(found_individual_spices),
            "generic_spice_count": len(found_generic_terms),
            "expected_spices_ratio": len(found_expected_spices) / len(expected_spices) if expected_spices else 0,
            "shopping_list": shopping_list
        }
    
    async def test_walmart_integration_with_spices(self, recipe_results: Dict[str, Any]):
        """Test 3: Test Walmart integration with specific spice names"""
        self.log("=== Testing Walmart Integration with Specific Spices ===")
        
        if not recipe_results:
            self.log("❌ No recipe results available for Walmart testing")
            return False
        
        # Test specific spices directly with Walmart API
        test_spices = [
            "turmeric powder", "ground cumin", "ground coriander", "paprika",
            "garam masala", "dried oregano", "dried basil", "dried thyme"
        ]
        
        walmart_results = {}
        
        for spice in test_spices:
            self.log(f"--- Testing Walmart search for: {spice} ---")
            
            try:
                # Test the backend search function directly
                sys.path.append('/app/backend')
                from server import search_walmart_products
                
                products = await search_walmart_products(spice)
                
                if products:
                    self.log(f"✅ Found {len(products)} products for '{spice}'")
                    walmart_results[spice] = {
                        "success": True,
                        "product_count": len(products),
                        "products": [{"name": p.name, "price": p.price} for p in products]
                    }
                    
                    # Show first 2 products
                    for i, product in enumerate(products[:2]):
                        self.log(f"  Product {i+1}: {product.name} - ${product.price}")
                else:
                    self.log(f"❌ No products found for '{spice}'")
                    walmart_results[spice] = {"success": False, "product_count": 0}
                    
            except Exception as e:
                self.log(f"❌ Error testing '{spice}': {str(e)}")
                walmart_results[spice] = {"success": False, "error": str(e)}
        
        return walmart_results
    
    async def test_cart_options_with_spices(self, recipe_results: Dict[str, Any]):
        """Test 4: Test cart options endpoint with spice-heavy recipes"""
        self.log("=== Testing Cart Options with Spice-Heavy Recipes ===")
        
        if not recipe_results or not self.user_id:
            self.log("❌ Missing recipe results or user_id for cart options test")
            return False
        
        cart_results = {}
        
        for recipe_name, recipe_data in recipe_results.items():
            if "error" in recipe_data:
                continue
                
            recipe = recipe_data.get("recipe", {})
            recipe_id = recipe.get("id")
            
            if not recipe_id:
                continue
                
            self.log(f"--- Testing cart options for: {recipe_name} ---")
            
            try:
                params = {
                    "recipe_id": recipe_id,
                    "user_id": self.user_id
                }
                
                response = await self.client.post(f"{BACKEND_URL}/grocery/cart-options", params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    ingredient_options = result.get("ingredient_options", [])
                    total_products = result.get("total_products", 0)
                    
                    self.log(f"✅ Cart options generated: {total_products} total products")
                    self.log(f"Ingredient options: {len(ingredient_options)} ingredients")
                    
                    # Analyze spice products in cart options
                    spice_products = self.analyze_cart_spice_products(ingredient_options)
                    cart_results[recipe_name] = {
                        "success": True,
                        "total_products": total_products,
                        "ingredient_count": len(ingredient_options),
                        "spice_analysis": spice_products
                    }
                    
                    self.log(f"Spice products found: {spice_products['spice_ingredient_count']}")
                    for spice_ingredient in spice_products["spice_ingredients"]:
                        self.log(f"  {spice_ingredient['name']}: {spice_ingredient['product_count']} products")
                    
                else:
                    self.log(f"❌ Cart options failed: {response.status_code} - {response.text}")
                    cart_results[recipe_name] = {"success": False, "error": response.text}
                    
            except Exception as e:
                self.log(f"❌ Error testing cart options for {recipe_name}: {str(e)}")
                cart_results[recipe_name] = {"success": False, "error": str(e)}
        
        return cart_results
    
    def analyze_cart_spice_products(self, ingredient_options: List[Dict]) -> Dict[str, Any]:
        """Analyze cart options for spice-related products"""
        
        spice_keywords = [
            "spice", "seasoning", "turmeric", "cumin", "coriander", "paprika", 
            "oregano", "basil", "thyme", "rosemary", "sage", "cardamom", 
            "cinnamon", "cloves", "bay", "saffron", "garam masala"
        ]
        
        spice_ingredients = []
        
        for ingredient_option in ingredient_options:
            ingredient_name = ingredient_option.get("ingredient_name", "").lower()
            products = ingredient_option.get("options", [])
            
            # Check if this ingredient is spice-related
            is_spice = any(keyword in ingredient_name for keyword in spice_keywords)
            
            if is_spice:
                spice_ingredients.append({
                    "name": ingredient_option.get("ingredient_name"),
                    "product_count": len(products),
                    "products": products
                })
        
        return {
            "spice_ingredient_count": len(spice_ingredients),
            "spice_ingredients": spice_ingredients,
            "total_spice_products": sum(len(ing["products"]) for ing in spice_ingredients)
        }
    
    async def run_comprehensive_spice_test(self):
        """Run all spice-focused tests in sequence"""
        self.log("🌶️ Starting Enhanced Spice Naming Tests")
        self.log("=" * 60)
        
        test_results = {}
        
        # Test 1: Demo Authentication
        test_results["authentication"] = await self.test_demo_authentication()
        
        if not test_results["authentication"]:
            self.log("❌ Authentication failed - cannot proceed with other tests")
            return test_results
        
        # Test 2: Spice-Heavy Recipe Generation
        test_results["recipe_generation"] = await self.test_spice_heavy_recipe_generation()
        
        # Test 3: Walmart Integration with Spices
        test_results["walmart_integration"] = await self.test_walmart_integration_with_spices(
            test_results.get("recipe_generation", {})
        )
        
        # Test 4: Cart Options with Spices
        test_results["cart_options"] = await self.test_cart_options_with_spices(
            test_results.get("recipe_generation", {})
        )
        
        # Summary
        self.log("=" * 60)
        self.log("🔍 ENHANCED SPICE NAMING TEST RESULTS")
        self.log("=" * 60)
        
        # Authentication Summary
        auth_status = "✅ PASS" if test_results["authentication"] else "❌ FAIL"
        self.log(f"AUTHENTICATION: {auth_status}")
        
        # Recipe Generation Summary
        recipe_results = test_results.get("recipe_generation", {})
        if recipe_results:
            successful_recipes = sum(1 for r in recipe_results.values() if "error" not in r)
            total_recipes = len(recipe_results)
            self.log(f"RECIPE GENERATION: {successful_recipes}/{total_recipes} recipes generated successfully")
            
            # Spice analysis summary
            total_individual_spices = 0
            total_generic_terms = 0
            
            for recipe_name, recipe_data in recipe_results.items():
                if "spice_analysis" in recipe_data:
                    analysis = recipe_data["spice_analysis"]
                    total_individual_spices += analysis["specific_spices_count"]
                    total_generic_terms += analysis["generic_spice_count"]
                    
                    self.log(f"  {recipe_name}:")
                    self.log(f"    Individual spices: {analysis['specific_spices_count']}")
                    self.log(f"    Generic terms: {analysis['generic_spice_count']}")
                    self.log(f"    Expected spices found: {len(analysis['expected_spices_found'])}")
            
            self.log(f"OVERALL SPICE NAMING:")
            self.log(f"  Total individual spices: {total_individual_spices}")
            self.log(f"  Total generic terms: {total_generic_terms}")
            
            if total_individual_spices > total_generic_terms:
                self.log("  ✅ GOOD: More individual spices than generic terms")
            else:
                self.log("  ⚠️ CONCERN: More generic terms than individual spices")
        
        # Walmart Integration Summary
        walmart_results = test_results.get("walmart_integration", {})
        if walmart_results:
            successful_searches = sum(1 for r in walmart_results.values() if r.get("success", False))
            total_searches = len(walmart_results)
            self.log(f"WALMART INTEGRATION: {successful_searches}/{total_searches} spice searches successful")
        
        # Cart Options Summary
        cart_results = test_results.get("cart_options", {})
        if cart_results:
            successful_carts = sum(1 for r in cart_results.values() if r.get("success", False))
            total_carts = len(cart_results)
            self.log(f"CART OPTIONS: {successful_carts}/{total_carts} cart generations successful")
        
        # Overall Assessment
        self.log("=" * 60)
        critical_passed = (
            test_results["authentication"] and
            bool(recipe_results) and
            bool(walmart_results) and
            bool(cart_results)
        )
        
        if critical_passed:
            self.log("🎉 ENHANCED SPICE NAMING TESTS COMPLETED")
            if total_individual_spices > total_generic_terms:
                self.log("✅ SPICE NAMING ENHANCEMENT: WORKING CORRECTLY")
            else:
                self.log("⚠️ SPICE NAMING ENHANCEMENT: NEEDS IMPROVEMENT")
        else:
            self.log("❌ SOME CRITICAL TESTS FAILED")
        
        return test_results

async def main():
    """Main test execution"""
    tester = EnhancedSpiceTester()
    
    try:
        results = await tester.run_comprehensive_spice_test()
        return results
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    results = asyncio.run(main())
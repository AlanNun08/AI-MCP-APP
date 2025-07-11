#!/usr/bin/env python3
"""
Additional Comprehensive Testing for Specific Review Requirements
Testing cross-category Walmart integration and email service validation
"""

import asyncio
import httpx
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpecificFeatureTester:
    def __init__(self):
        self.backend_url = "https://recipe-cart-app.preview.emergentagent.com/api"
        self.test_results = []
        self.test_user_data = {
            "email": "specific_test_2024@example.com",
            "password": "SpecificTest123!",
            "first_name": "Specific",
            "last_name": "Tester"
        }
        self.user_id = None
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
    
    async def setup_test_user(self) -> bool:
        """Setup test user for specific tests"""
        try:
            # Clean up first
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.delete(f"{self.backend_url}/debug/cleanup-test-data")
            
            # Register user
            registration_data = {
                "first_name": self.test_user_data["first_name"],
                "last_name": self.test_user_data["last_name"],
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"],
                "dietary_preferences": [],
                "allergies": [],
                "favorite_cuisines": []
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.backend_url}/auth/register", json=registration_data)
                if response.status_code != 200:
                    return False
                
                data = response.json()
                self.user_id = data.get("user_id")
                
                # Get verification code
                code_response = await client.get(f"{self.backend_url}/debug/verification-codes/{self.test_user_data['email']}")
                if code_response.status_code != 200:
                    return False
                
                code_data = code_response.json()
                codes = code_data.get("codes", [])
                if not codes:
                    return False
                
                verification_code = codes[0]["code"]
                
                # Verify email
                verify_data = {
                    "email": self.test_user_data["email"],
                    "code": verification_code
                }
                verify_response = await client.post(f"{self.backend_url}/auth/verify", json=verify_data)
                
                return verify_response.status_code == 200
                
        except Exception as e:
            logger.error(f"Setup error: {str(e)}")
            return False
    
    async def test_cross_category_walmart_integration(self) -> bool:
        """Test Walmart integration across all recipe categories"""
        try:
            if not self.user_id:
                self.log_test_result("Cross-Category Walmart Integration", False, "No user ID available")
                return False
            
            categories_to_test = [
                ("cuisine", "mexican", "Mexican Cuisine"),
                ("beverage", "coffee", "Coffee Beverage"),
                ("snack", "acai bowls", "Acai Bowl Snack")
            ]
            
            total_ingredients = 0
            total_products = 0
            successful_categories = 0
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                for category, cuisine_type, description in categories_to_test:
                    try:
                        # Generate recipe
                        recipe_request = {
                            "user_id": self.user_id,
                            "recipe_category": category,
                            "cuisine_type": cuisine_type,
                            "servings": 4,
                            "difficulty": "medium"
                        }
                        
                        recipe_response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                        
                        if recipe_response.status_code == 200:
                            recipe_data = recipe_response.json()
                            recipe_id = recipe_data.get("id")
                            recipe_title = recipe_data.get("title", "Unknown")
                            
                            if recipe_id:
                                # Test Walmart integration
                                cart_response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.user_id}")
                                
                                if cart_response.status_code == 200:
                                    cart_data = cart_response.json()
                                    ingredient_options = cart_data.get("ingredient_options", [])
                                    category_products = sum(len(ing.get("options", [])) for ing in ingredient_options)
                                    
                                    total_ingredients += len(ingredient_options)
                                    total_products += category_products
                                    successful_categories += 1
                                    
                                    logger.info(f"✅ {description}: '{recipe_title}' - {len(ingredient_options)} ingredients, {category_products} products")
                                else:
                                    logger.warning(f"❌ {description}: Walmart integration failed - HTTP {cart_response.status_code}")
                            else:
                                logger.warning(f"❌ {description}: No recipe ID returned")
                        else:
                            logger.warning(f"❌ {description}: Recipe generation failed - HTTP {recipe_response.status_code}")
                    
                    except Exception as e:
                        logger.error(f"❌ {description}: Error - {str(e)}")
            
            if successful_categories == len(categories_to_test):
                self.log_test_result(
                    "Cross-Category Walmart Integration", 
                    True, 
                    f"All {len(categories_to_test)} categories successful - {total_ingredients} ingredients, {total_products} products"
                )
                return True
            else:
                self.log_test_result(
                    "Cross-Category Walmart Integration", 
                    False, 
                    f"Only {successful_categories}/{len(categories_to_test)} categories successful"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Cross-Category Walmart Integration", False, f"Test error: {str(e)}")
            return False
    
    async def test_starbucks_drink_types(self) -> bool:
        """Test different Starbucks drink types"""
        try:
            if not self.user_id:
                self.log_test_result("Starbucks Drink Types", False, "No user ID available")
                return False
            
            drink_types = ["frappuccino", "refresher", "lemonade", "iced_matcha_latte", "random"]
            successful_drinks = 0
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                for drink_type in drink_types:
                    try:
                        starbucks_request = {
                            "user_id": self.user_id,
                            "drink_type": drink_type,
                            "flavor_inspiration": "tropical"
                        }
                        
                        response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=starbucks_request)
                        
                        if response.status_code == 200:
                            data = response.json()
                            drink_name = data.get("drink_name", "Unknown")
                            category = data.get("category", "Unknown")
                            successful_drinks += 1
                            logger.info(f"✅ {drink_type}: '{drink_name}' ({category})")
                        else:
                            logger.warning(f"❌ {drink_type}: HTTP {response.status_code}")
                    
                    except Exception as e:
                        logger.error(f"❌ {drink_type}: Error - {str(e)}")
            
            if successful_drinks == len(drink_types):
                self.log_test_result(
                    "Starbucks Drink Types", 
                    True, 
                    f"All {len(drink_types)} drink types generated successfully"
                )
                return True
            else:
                self.log_test_result(
                    "Starbucks Drink Types", 
                    False, 
                    f"Only {successful_drinks}/{len(drink_types)} drink types successful"
                )
                return False
                
        except Exception as e:
            self.log_test_result("Starbucks Drink Types", False, f"Test error: {str(e)}")
            return False
    
    async def test_email_service_validation(self) -> bool:
        """Test email service functionality"""
        try:
            # Test with a new user for email validation
            test_email = "email_validation_test@example.com"
            
            registration_data = {
                "first_name": "Email",
                "last_name": "Test",
                "email": test_email,
                "password": "EmailTest123!",
                "dietary_preferences": [],
                "allergies": [],
                "favorite_cuisines": []
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Register user (should send verification email)
                response = await client.post(f"{self.backend_url}/auth/register", json=registration_data)
                
                if response.status_code != 200:
                    self.log_test_result("Email Service Validation", False, f"Registration failed: HTTP {response.status_code}")
                    return False
                
                # Check if verification code was generated
                code_response = await client.get(f"{self.backend_url}/debug/verification-codes/{test_email}")
                
                if code_response.status_code == 200:
                    code_data = code_response.json()
                    codes = code_data.get("codes", [])
                    
                    if codes:
                        # Test resend functionality
                        resend_response = await client.post(f"{self.backend_url}/auth/resend-code", json={"email": test_email})
                        
                        if resend_response.status_code == 200:
                            self.log_test_result(
                                "Email Service Validation", 
                                True, 
                                "Email verification and resend functionality working"
                            )
                            return True
                        else:
                            self.log_test_result("Email Service Validation", False, f"Resend failed: HTTP {resend_response.status_code}")
                            return False
                    else:
                        self.log_test_result("Email Service Validation", False, "No verification codes generated")
                        return False
                else:
                    self.log_test_result("Email Service Validation", False, f"Code retrieval failed: HTTP {code_response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test_result("Email Service Validation", False, f"Email service error: {str(e)}")
            return False
    
    async def test_shopping_list_generation(self) -> bool:
        """Test shopping list generation quality across categories"""
        try:
            if not self.user_id:
                self.log_test_result("Shopping List Generation", False, "No user ID available")
                return False
            
            categories = [
                ("cuisine", "italian", "Italian"),
                ("beverage", "thai tea", "Thai Tea"),
                ("snack", "frozen yogurt berry bites", "Frozen Yogurt")
            ]
            
            total_clean_items = 0
            total_items = 0
            successful_recipes = 0
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                for category, cuisine_type, description in categories:
                    try:
                        recipe_request = {
                            "user_id": self.user_id,
                            "recipe_category": category,
                            "cuisine_type": cuisine_type,
                            "servings": 4,
                            "difficulty": "medium"
                        }
                        
                        response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                        
                        if response.status_code == 200:
                            data = response.json()
                            shopping_list = data.get("shopping_list", [])
                            recipe_title = data.get("title", "Unknown")
                            
                            # Analyze shopping list quality
                            clean_items = 0
                            for item in shopping_list:
                                # Check if item is clean (no quantities, measurements, etc.)
                                if not any(char.isdigit() for char in item) and not any(word in item.lower() for word in ['cup', 'tbsp', 'tsp', 'oz', 'lb', 'can', 'jar']):
                                    clean_items += 1
                            
                            total_clean_items += clean_items
                            total_items += len(shopping_list)
                            successful_recipes += 1
                            
                            cleanliness_rate = (clean_items / len(shopping_list) * 100) if shopping_list else 0
                            logger.info(f"✅ {description}: '{recipe_title}' - {len(shopping_list)} items, {cleanliness_rate:.1f}% clean")
                        else:
                            logger.warning(f"❌ {description}: Recipe generation failed - HTTP {response.status_code}")
                    
                    except Exception as e:
                        logger.error(f"❌ {description}: Error - {str(e)}")
            
            if successful_recipes > 0:
                overall_cleanliness = (total_clean_items / total_items * 100) if total_items > 0 else 0
                
                if overall_cleanliness >= 80:  # 80% cleanliness threshold
                    self.log_test_result(
                        "Shopping List Generation", 
                        True, 
                        f"{successful_recipes} recipes generated, {overall_cleanliness:.1f}% shopping list cleanliness"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Shopping List Generation", 
                        False, 
                        f"Shopping list cleanliness too low: {overall_cleanliness:.1f}%"
                    )
                    return False
            else:
                self.log_test_result("Shopping List Generation", False, "No recipes generated successfully")
                return False
                
        except Exception as e:
            self.log_test_result("Shopping List Generation", False, f"Test error: {str(e)}")
            return False
    
    async def run_specific_tests(self):
        """Run specific feature tests"""
        logger.info("🎯 Starting Specific Feature Testing")
        
        # Setup test user
        if not await self.setup_test_user():
            logger.error("Failed to setup test user")
            return
        
        # Run specific tests
        tests = [
            ("Cross-Category Walmart Integration", self.test_cross_category_walmart_integration),
            ("Starbucks Drink Types", self.test_starbucks_drink_types),
            ("Email Service Validation", self.test_email_service_validation),
            ("Shopping List Generation", self.test_shopping_list_generation)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test execution error: {str(e)}")
            
            await asyncio.sleep(2)  # Longer delay for complex tests
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🔍 SPECIFIC FEATURE TESTING SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"{status_icon} {result['test']}: {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main execution"""
    tester = SpecificFeatureTester()
    await tester.run_specific_tests()

if __name__ == "__main__":
    asyncio.run(main())
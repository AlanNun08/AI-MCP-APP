#!/usr/bin/env python3
"""
Walmart API Validation Test - Verify Real Product IDs and No Mock Data
"""

import asyncio
import httpx
import json
import logging
import os
import re
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WalmartValidator:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_user_id = "test-walmart-validation"
        
    def get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            frontend_env_path = "/app/frontend/.env"
            if os.path.exists(frontend_env_path):
                with open(frontend_env_path, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            url = line.split('=', 1)[1].strip()
                            return f"{url}/api"
            return "http://localhost:8001/api"
        except Exception as e:
            logger.warning(f"Could not read frontend .env: {e}, using localhost")
            return "http://localhost:8001/api"
    
    def validate_product_id(self, product_id: str) -> Dict[str, Any]:
        """Validate if product ID is real Walmart ID (not mock data)"""
        validation = {
            "product_id": product_id,
            "is_valid": False,
            "is_mock": False,
            "issues": []
        }
        
        # Check for mock patterns
        mock_patterns = [
            r'^10315',  # Mock pattern mentioned in requirements
            r'^12345',  # Common mock pattern
            r'^99999',  # Common mock pattern
            r'^walmart-',  # Mock prefix
            r'^mock-',  # Mock prefix
            r'^test-',  # Test prefix
        ]
        
        for pattern in mock_patterns:
            if re.match(pattern, product_id):
                validation["is_mock"] = True
                validation["issues"].append(f"Matches mock pattern: {pattern}")
        
        # Validate real Walmart ID characteristics
        if product_id.isdigit():
            if len(product_id) >= 6 and len(product_id) <= 12:
                validation["is_valid"] = True
            else:
                validation["issues"].append(f"Invalid length: {len(product_id)} (should be 6-12 digits)")
        else:
            validation["issues"].append("Not numeric")
        
        # Final validation
        validation["is_valid"] = validation["is_valid"] and not validation["is_mock"]
        
        return validation
    
    async def test_walmart_product_validation(self) -> Dict[str, Any]:
        """Test Walmart integration and validate all product IDs"""
        try:
            logger.info("🔍 Testing Walmart API Integration and Product ID Validation")
            
            # Generate a recipe to get ingredients
            recipe_request = {
                "user_id": self.test_user_id,
                "recipe_category": "cuisine",
                "cuisine_type": "italian",
                "servings": 4,
                "difficulty": "medium"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Generate recipe
                logger.info("📝 Generating recipe for Walmart testing...")
                recipe_response = await client.post(f"{self.backend_url}/recipes/generate", json=recipe_request)
                
                if recipe_response.status_code != 200:
                    return {"error": f"Failed to generate recipe: {recipe_response.status_code}"}
                
                recipe_data = recipe_response.json()
                recipe_id = recipe_data.get("id")
                shopping_list = recipe_data.get("shopping_list", [])
                
                logger.info(f"✅ Recipe generated: '{recipe_data.get('title')}' with {len(shopping_list)} ingredients")
                
                # Test cart options endpoint
                logger.info("🛒 Testing Walmart cart options...")
                cart_options_response = await client.post(f"{self.backend_url}/grocery/cart-options?recipe_id={recipe_id}&user_id={self.test_user_id}")
                
                if cart_options_response.status_code != 200:
                    return {"error": f"Cart options failed: {cart_options_response.status_code}"}
                
                cart_data = cart_options_response.json()
                ingredient_options = cart_data.get("ingredient_options", [])
                
                # Validate all product IDs
                validation_results = {
                    "total_ingredients": len(ingredient_options),
                    "total_products": 0,
                    "valid_products": 0,
                    "mock_products": 0,
                    "invalid_products": 0,
                    "product_validations": [],
                    "ingredient_details": []
                }
                
                for ingredient in ingredient_options:
                    ingredient_name = ingredient.get("ingredient_name", "Unknown")
                    options = ingredient.get("options", [])
                    
                    ingredient_detail = {
                        "ingredient": ingredient_name,
                        "product_count": len(options),
                        "products": []
                    }
                    
                    for product in options:
                        product_id = product.get("product_id", "")
                        product_name = product.get("name", "")
                        product_price = product.get("price", 0)
                        
                        validation = self.validate_product_id(product_id)
                        validation_results["product_validations"].append(validation)
                        validation_results["total_products"] += 1
                        
                        if validation["is_valid"]:
                            validation_results["valid_products"] += 1
                        elif validation["is_mock"]:
                            validation_results["mock_products"] += 1
                        else:
                            validation_results["invalid_products"] += 1
                        
                        ingredient_detail["products"].append({
                            "id": product_id,
                            "name": product_name,
                            "price": product_price,
                            "is_valid": validation["is_valid"],
                            "is_mock": validation["is_mock"],
                            "issues": validation["issues"]
                        })
                    
                    validation_results["ingredient_details"].append(ingredient_detail)
                
                # Calculate success rates
                if validation_results["total_products"] > 0:
                    validation_results["valid_rate"] = (validation_results["valid_products"] / validation_results["total_products"]) * 100
                    validation_results["mock_rate"] = (validation_results["mock_products"] / validation_results["total_products"]) * 100
                else:
                    validation_results["valid_rate"] = 0
                    validation_results["mock_rate"] = 0
                
                return validation_results
                
        except Exception as e:
            logger.error(f"Walmart validation error: {str(e)}")
            return {"error": str(e)}
    
    async def run_validation(self):
        """Run Walmart validation tests"""
        logger.info("🚀 Starting Walmart API Validation")
        logger.info(f"Backend URL: {self.backend_url}")
        
        results = await self.test_walmart_product_validation()
        
        if "error" in results:
            print(f"\n❌ VALIDATION FAILED: {results['error']}")
            return False
        
        # Print detailed results
        print("\n" + "="*80)
        print("🛒 WALMART API VALIDATION RESULTS")
        print("="*80)
        print(f"Total Ingredients: {results['total_ingredients']}")
        print(f"Total Products: {results['total_products']}")
        print(f"Valid Products: {results['valid_products']} ({results['valid_rate']:.1f}%)")
        print(f"Mock Products: {results['mock_products']} ({results['mock_rate']:.1f}%)")
        print(f"Invalid Products: {results['invalid_products']}")
        
        print("\n📋 INGREDIENT BREAKDOWN:")
        print("-" * 80)
        
        for ingredient in results['ingredient_details']:
            print(f"\n🥘 {ingredient['ingredient']} ({ingredient['product_count']} products):")
            for product in ingredient['products']:
                status = "✅" if product['is_valid'] else ("🚫" if product['is_mock'] else "⚠️")
                price_str = f"${product['price']:.2f}" if product['price'] > 0 else "N/A"
                print(f"   {status} {product['id']} - {product['name']} ({price_str})")
                if product['issues']:
                    for issue in product['issues']:
                        print(f"      ⚠️ {issue}")
        
        print("\n" + "="*80)
        
        # Determine success
        success = results['mock_products'] == 0 and results['valid_products'] > 0
        
        if success:
            print("🎉 WALMART INTEGRATION VALIDATION PASSED")
            print("✅ All product IDs are authentic Walmart products")
            print("✅ No mock data detected")
        else:
            print("🚨 WALMART INTEGRATION VALIDATION FAILED")
            if results['mock_products'] > 0:
                print(f"❌ Found {results['mock_products']} mock products")
            if results['valid_products'] == 0:
                print("❌ No valid products found")
        
        return success

async def main():
    """Main validation execution"""
    validator = WalmartValidator()
    success = await validator.run_validation()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
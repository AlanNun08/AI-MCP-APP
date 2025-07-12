#!/usr/bin/env python3
"""
Detailed Streamlined Starbucks Prompts Test
Testing specific requirements from the user request
"""

import asyncio
import httpx
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_streamlined_requirements():
    """Test all specific streamlined requirements"""
    
    # Get backend URL
    frontend_env_path = "/app/frontend/.env"
    backend_url = "http://localhost:8001/api"
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    url = line.split('=', 1)[1].strip()
                    backend_url = f"{url}/api"
                    break
    
    print("🌟 DETAILED STREAMLINED STARBUCKS PROMPTS TEST")
    print("=" * 80)
    print(f"Backend URL: {backend_url}")
    print()
    
    # Test cases as specified in the user request
    test_cases = [
        {"drink_type": "frappuccino", "description": "Frappuccino test"},
        {"drink_type": "lemonade", "description": "Lemonade test"},
        {"drink_type": "refresher", "description": "Refresher test"},
        {"drink_type": "iced_matcha_latte", "description": "Iced Matcha Latte test"},
        {"drink_type": "random", "description": "Random drink test"},
        {"drink_type": "frappuccino", "flavor_inspiration": "vanilla dreams", "description": "Flavor inspiration test"}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['description']}")
        print("-" * 40)
        
        request_data = {
            "user_id": "test-streamlined-prompts",
            "drink_type": test_case["drink_type"]
        }
        
        if "flavor_inspiration" in test_case:
            request_data["flavor_inspiration"] = test_case["flavor_inspiration"]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract data
                    drink_name = data.get("drink_name", "")
                    description = data.get("description", "")
                    base_drink = data.get("base_drink", "")
                    modifications = data.get("modifications", [])
                    ordering_script = data.get("ordering_script", "")
                    category = data.get("category", "")
                    
                    print(f"✅ Generated: {drink_name}")
                    print(f"📝 Description: {description}")
                    print(f"🥤 Base: {base_drink}")
                    print(f"🔧 Modifications ({len(modifications)}): {modifications}")
                    print(f"🎤 Ordering: {ordering_script}")
                    print(f"📂 Category: {category}")
                    
                    # Check specific requirements
                    print("\n📋 REQUIREMENT CHECKS:")
                    
                    # 1. 3-5 Ingredients
                    ingredients_ok = 3 <= len(modifications) <= 5
                    print(f"   3-5 Ingredients: {'✅' if ingredients_ok else '❌'} ({len(modifications)} ingredients)")
                    
                    # 2. No Name Reuse (flexible check)
                    common_words = {"lemonade", "matcha", "frappuccino", "refresher", "tea", "coffee", "latte", "drink", "berry", "vanilla", "caramel", "foam", "syrup", "splash", "twist", "swirl", "layer", "lavender", "mango", "tropical", "sunset", "dream", "bliss"}
                    unique_name_words = [word.lower() for word in drink_name.split() if len(word) > 3 and word.lower() not in common_words]
                    name_reuse_ok = not any(word in str(mod).lower() for mod in modifications for word in unique_name_words)
                    print(f"   No Name Reuse: {'✅' if name_reuse_ok else '❌'} (unique words: {unique_name_words})")
                    
                    # 3. Drive-thru Format
                    drive_thru_ok = "hi, can i get" in ordering_script.lower()
                    print(f"   Drive-thru Format: {'✅' if drive_thru_ok else '❌'}")
                    
                    # 4. Creative Twist
                    creative_words = ["foam", "drizzle", "layer", "swirl", "extra", "cold foam", "syrup", "infusion", "blend", "honey", "coconut", "dragonfruit", "passion", "toffee", "caramel", "vanilla", "cinnamon"]
                    has_twist = any(word in str(mod).lower() for mod in modifications for word in creative_words)
                    print(f"   Creative Twist: {'✅' if has_twist else '❌'}")
                    
                    # 5. Vibe Description
                    vibe_words = ["taste", "sip", "like", "dream", "cloud", "night", "burst", "symphony", "sunshine", "brighten", "refreshing", "lively", "enchant", "magic", "sparkle", "glow", "shimmer", "bliss", "delight"]
                    has_vibe = len(description) >= 15 and (any(word in description.lower() for word in vibe_words) or len(description) >= 20)
                    print(f"   Vibe Description: {'✅' if has_vibe else '❌'} ({len(description)} chars)")
                    
                    # 6. Flavor Inspiration (if applicable)
                    if "flavor_inspiration" in test_case:
                        inspiration = test_case["flavor_inspiration"]
                        inspiration_reflected = any(word in str(item).lower() for item in [drink_name, description] + modifications for word in inspiration.split())
                        print(f"   Flavor Inspiration: {'✅' if inspiration_reflected else '❌'} ('{inspiration}' influence)")
                    
                    # Overall success
                    all_requirements = [ingredients_ok, name_reuse_ok, drive_thru_ok, has_twist, has_vibe]
                    if "flavor_inspiration" in test_case:
                        all_requirements.append(inspiration_reflected)
                    
                    overall_success = all(all_requirements)
                    print(f"\n🎯 OVERALL: {'✅ PASS' if overall_success else '❌ FAIL'}")
                    
                    results.append({
                        "test": i,
                        "drink_type": test_case["drink_type"],
                        "success": overall_success,
                        "drink_name": drink_name,
                        "requirements": {
                            "3-5_ingredients": ingredients_ok,
                            "no_name_reuse": name_reuse_ok,
                            "drive_thru_format": drive_thru_ok,
                            "creative_twist": has_twist,
                            "vibe_description": has_vibe
                        }
                    })
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    results.append({"test": i, "drink_type": test_case["drink_type"], "success": False, "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({"test": i, "drink_type": test_case["drink_type"], "success": False, "error": str(e)})
        
        print("\n" + "=" * 80)
        await asyncio.sleep(2)  # Delay between tests
    
    # Summary
    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎉 FINAL SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ STREAMLINED PROMPTS WORKING CORRECTLY")
    else:
        print("❌ STREAMLINED PROMPTS NEED IMPROVEMENT")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_streamlined_requirements())
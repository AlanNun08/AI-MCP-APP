#!/usr/bin/env python3
"""
Enhanced Creativity Features Testing for Starbucks API
Specifically testing the new advanced creativity features requested in the review
"""

import asyncio
import httpx
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedCreativityTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.backend_url = self.get_backend_url()
        self.test_results = []
        self.test_user_id = "test-enhanced-creativity"
        
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
    
    def analyze_creativity_features(self, data: dict, drink_type: str) -> Dict[str, Any]:
        """Analyze the enhanced creativity features in the response"""
        analysis = {
            "unique_naming": False,
            "theme_integration": False,
            "surprise_ingredients": False,
            "enhanced_creativity": False,
            "drive_thru_format": False,
            "details": {}
        }
        
        drink_name = data.get("drink_name", "")
        description = data.get("description", "")
        modifications = data.get("modifications", [])
        ordering_script = data.get("ordering_script", "")
        vibe = data.get("vibe", data.get("why_amazing", ""))
        
        # 1. Check for unique, original naming patterns
        creative_name_indicators = [
            "celestial", "stellar", "cosmic", "aurora", "luminous", "ethereal", "mystic", 
            "enchanted", "twilight", "stardust", "moonbeam", "crystal", "velvet", "silk",
            "whisper", "serenade", "symphony", "mirage", "reverie", "drift", "bloom",
            "prism", "ember", "frost", "shimmer", "glow", "radiance"
        ]
        
        name_lower = drink_name.lower()
        unique_words_found = [word for word in creative_name_indicators if word in name_lower]
        analysis["unique_naming"] = len(unique_words_found) > 0
        analysis["details"]["unique_words"] = unique_words_found
        analysis["details"]["drink_name"] = drink_name
        
        # 2. Check for theme integration (fantasy, color, mood, seasonal, nostalgic)
        theme_indicators = {
            "fantasy": ["fairy", "magic", "enchant", "mystic", "spell", "potion", "crystal", "ethereal"],
            "color": ["golden", "crimson", "azure", "violet", "emerald", "coral", "amber", "pearl"],
            "mood": ["serene", "cozy", "energetic", "dreamy", "peaceful", "vibrant", "calm"],
            "seasonal": ["autumn", "spring", "winter", "summer", "harvest", "bloom", "frost"],
            "nostalgic": ["vintage", "classic", "retro", "childhood", "memory", "timeless"]
        }
        
        detected_themes = []
        full_text = f"{drink_name} {description} {vibe}".lower()
        for theme, keywords in theme_indicators.items():
            if any(keyword in full_text for keyword in keywords):
                detected_themes.append(theme)
        
        analysis["theme_integration"] = len(detected_themes) > 0
        analysis["details"]["themes_detected"] = detected_themes
        
        # 3. Check for surprise ingredients/twists
        surprise_indicators = [
            "espresso", "shot", "foam", "cold foam", "tea", "matcha", "passion",
            "brown sugar", "drizzle", "layer", "twist", "hint", "touch", "splash"
        ]
        
        modifications_text = " ".join(modifications).lower()
        surprise_elements = [elem for elem in surprise_indicators if elem in modifications_text]
        analysis["surprise_ingredients"] = len(surprise_elements) > 0
        analysis["details"]["surprise_elements"] = surprise_elements
        analysis["details"]["modifications"] = modifications
        
        # 4. Check for enhanced creativity (bold, strange, playful combinations)
        creativity_indicators = [
            "unexpected", "unique", "bold", "creative", "innovative", "artisanal",
            "gourmet", "signature", "special", "exclusive", "limited", "rare"
        ]
        
        creativity_found = [word for word in creativity_indicators if word in full_text]
        unusual_combinations = []
        
        # Check for unusual ingredient combinations
        if any(combo in modifications_text for combo in ["matcha + ", "espresso + lemonade", "foam + frappuccino", "tea + "]):
            unusual_combinations.append("unusual_ingredient_mix")
        
        analysis["enhanced_creativity"] = len(creativity_found) > 0 or len(unusual_combinations) > 0
        analysis["details"]["creativity_indicators"] = creativity_found
        analysis["details"]["unusual_combinations"] = unusual_combinations
        
        # 5. Check drive-thru ordering format
        ordering_lower = ordering_script.lower()
        has_greeting = "hi" in ordering_lower or "hello" in ordering_lower
        has_request = "can i get" in ordering_lower or "i'd like" in ordering_lower
        analysis["drive_thru_format"] = has_greeting and has_request
        analysis["details"]["ordering_script"] = ordering_script
        
        return analysis
    
    async def test_enhanced_drink_type(self, drink_type: str, flavor_inspiration: str = None) -> Dict[str, Any]:
        """Test a specific drink type for enhanced creativity features"""
        try:
            request_data = {
                "user_id": self.test_user_id,
                "drink_type": drink_type
            }
            
            if flavor_inspiration:
                request_data["flavor_inspiration"] = flavor_inspiration
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(f"{self.backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = self.analyze_creativity_features(data, drink_type)
                    
                    # Calculate overall creativity score
                    features_passed = sum([
                        analysis["unique_naming"],
                        analysis["theme_integration"], 
                        analysis["surprise_ingredients"],
                        analysis["enhanced_creativity"],
                        analysis["drive_thru_format"]
                    ])
                    
                    creativity_score = (features_passed / 5) * 100
                    
                    result = {
                        "success": True,
                        "drink_type": drink_type,
                        "flavor_inspiration": flavor_inspiration,
                        "creativity_score": creativity_score,
                        "features_analysis": analysis,
                        "response_data": data
                    }
                    
                    logger.info(f"✅ {drink_type.upper()}: '{data.get('drink_name', '')}' - Creativity Score: {creativity_score:.1f}%")
                    return result
                    
                else:
                    logger.error(f"❌ {drink_type.upper()}: HTTP {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                    
        except Exception as e:
            logger.error(f"❌ {drink_type.upper()}: Error - {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_enhanced_creativity_tests(self) -> Dict[str, Any]:
        """Run comprehensive enhanced creativity tests"""
        logger.info("🌟 Starting Enhanced Creativity Features Testing")
        logger.info(f"Backend URL: {self.backend_url}")
        
        # Test all drink types as requested
        test_cases = [
            ("frappuccino", None),
            ("lemonade", None),
            ("refresher", None),
            ("iced_matcha_latte", None),
            ("random", None),
            ("frappuccino", "birthday cake nostalgia")  # Test with flavor inspiration
        ]
        
        results = []
        total_creativity_score = 0
        successful_tests = 0
        
        for drink_type, flavor_inspiration in test_cases:
            test_name = f"{drink_type}" + (f" with {flavor_inspiration}" if flavor_inspiration else "")
            logger.info(f"Testing: {test_name}")
            
            result = await self.test_enhanced_drink_type(drink_type, flavor_inspiration)
            results.append(result)
            
            if result.get("success"):
                total_creativity_score += result.get("creativity_score", 0)
                successful_tests += 1
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        # Calculate overall metrics
        average_creativity_score = (total_creativity_score / successful_tests) if successful_tests > 0 else 0
        
        summary = {
            "total_tests": len(test_cases),
            "successful_tests": successful_tests,
            "failed_tests": len(test_cases) - successful_tests,
            "average_creativity_score": average_creativity_score,
            "backend_url": self.backend_url,
            "test_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary

async def main():
    """Main test execution"""
    tester = EnhancedCreativityTester()
    
    try:
        summary = await tester.run_enhanced_creativity_tests()
        
        # Print detailed summary
        print("\n" + "="*100)
        print("🌟 ENHANCED CREATIVITY FEATURES TESTING SUMMARY")
        print("="*100)
        print(f"Backend URL: {summary['backend_url']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Average Creativity Score: {summary['average_creativity_score']:.1f}%")
        print(f"Test Completed: {summary['timestamp']}")
        
        print("\n📋 DETAILED CREATIVITY ANALYSIS:")
        print("-" * 100)
        
        for result in summary['test_results']:
            if result.get("success"):
                drink_type = result['drink_type']
                flavor = result.get('flavor_inspiration', 'None')
                score = result['creativity_score']
                analysis = result['features_analysis']
                data = result['response_data']
                
                print(f"\n🍹 {drink_type.upper()} (Flavor: {flavor}) - Score: {score:.1f}%")
                print(f"   Name: '{data.get('drink_name', '')}' ")
                print(f"   ✅ Unique Naming: {analysis['unique_naming']} {analysis['details'].get('unique_words', [])}")
                print(f"   ✅ Theme Integration: {analysis['theme_integration']} {analysis['details'].get('themes_detected', [])}")
                print(f"   ✅ Surprise Ingredients: {analysis['surprise_ingredients']} {analysis['details'].get('surprise_elements', [])}")
                print(f"   ✅ Enhanced Creativity: {analysis['enhanced_creativity']}")
                print(f"   ✅ Drive-thru Format: {analysis['drive_thru_format']}")
                print(f"   📝 Vibe: {data.get('vibe', data.get('why_amazing', ''))[:80]}...")
                print(f"   🛒 Ordering: {data.get('ordering_script', '')[:60]}...")
            else:
                print(f"\n❌ {result.get('drink_type', 'Unknown')}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*100)
        
        # Final assessment
        if summary['average_creativity_score'] >= 80:
            print("🎉 EXCELLENT: Enhanced creativity features are working exceptionally well!")
        elif summary['average_creativity_score'] >= 60:
            print("✅ GOOD: Enhanced creativity features are working well with room for improvement")
        else:
            print("⚠️ NEEDS IMPROVEMENT: Enhanced creativity features need attention")
        
        # Feature-specific assessment
        feature_scores = {}
        for result in summary['test_results']:
            if result.get("success"):
                analysis = result['features_analysis']
                for feature in ['unique_naming', 'theme_integration', 'surprise_ingredients', 'enhanced_creativity', 'drive_thru_format']:
                    if feature not in feature_scores:
                        feature_scores[feature] = []
                    feature_scores[feature].append(analysis[feature])
        
        print("\n📊 FEATURE SUCCESS RATES:")
        for feature, scores in feature_scores.items():
            success_rate = (sum(scores) / len(scores)) * 100 if scores else 0
            print(f"   {feature.replace('_', ' ').title()}: {success_rate:.1f}%")
        
        return summary
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
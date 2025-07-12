#!/usr/bin/env python3
"""
Sample Response Analysis for Enhanced Creativity Features
"""

import asyncio
import httpx
import json
import os

async def get_sample_responses():
    """Get sample responses to analyze content quality"""
    
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
    
    test_cases = [
        {"user_id": "test-enhanced-creativity", "drink_type": "frappuccino"},
        {"user_id": "test-enhanced-creativity", "drink_type": "lemonade"},
        {"user_id": "test-enhanced-creativity", "drink_type": "refresher"},
        {"user_id": "test-enhanced-creativity", "drink_type": "iced_matcha_latte"},
        {"user_id": "test-enhanced-creativity", "drink_type": "random"},
        {"user_id": "test-enhanced-creativity", "drink_type": "frappuccino", "flavor_inspiration": "birthday cake nostalgia"}
    ]
    
    print("🌟 SAMPLE RESPONSES FOR ENHANCED CREATIVITY ANALYSIS")
    print("="*80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, request_data in enumerate(test_cases, 1):
            try:
                response = await client.post(f"{backend_url}/generate-starbucks-drink", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    drink_type = request_data['drink_type']
                    flavor = request_data.get('flavor_inspiration', 'None')
                    
                    print(f"\n📋 SAMPLE {i}: {drink_type.upper()} (Flavor: {flavor})")
                    print("-" * 60)
                    print(f"🍹 Name: {data.get('drink_name', '')}")
                    print(f"📝 Description: {data.get('description', '')}")
                    print(f"🥤 Base: {data.get('base_drink', '')}")
                    print(f"🔧 Modifications: {', '.join(data.get('modifications', []))}")
                    print(f"🛒 Ordering: {data.get('ordering_script', '')}")
                    print(f"✨ Vibe: {data.get('vibe', data.get('why_amazing', ''))}")
                    print(f"🏷️ Category: {data.get('category', '')}")
                    
                    # Analysis
                    print(f"\n🔍 CREATIVITY ANALYSIS:")
                    
                    # Check unique naming
                    name = data.get('drink_name', '').lower()
                    creative_words = ['stardust', 'celestial', 'twilight', 'aurora', 'mystic', 'enchanted', 'luminous', 'ethereal', 'cosmic', 'stellar']
                    found_creative = [word for word in creative_words if word in name]
                    print(f"   • Unique Naming: {'✅' if found_creative else '❌'} {found_creative}")
                    
                    # Check theme integration
                    full_text = f"{data.get('drink_name', '')} {data.get('description', '')} {data.get('vibe', '')}".lower()
                    themes = {
                        'fantasy': ['fairy', 'magic', 'enchant', 'mystic', 'celestial', 'cosmic'],
                        'color': ['golden', 'silver', 'crimson', 'azure', 'violet'],
                        'mood': ['dreamy', 'serene', 'vibrant', 'peaceful', 'energetic'],
                        'seasonal': ['autumn', 'spring', 'winter', 'summer', 'blossom'],
                        'nostalgic': ['vintage', 'classic', 'memory', 'childhood']
                    }
                    
                    detected_themes = []
                    for theme, keywords in themes.items():
                        if any(keyword in full_text for keyword in keywords):
                            detected_themes.append(theme)
                    
                    print(f"   • Theme Integration: {'✅' if detected_themes else '❌'} {detected_themes}")
                    
                    # Check surprise ingredients
                    mods_text = ' '.join(data.get('modifications', [])).lower()
                    surprise_elements = ['espresso', 'shot', 'foam', 'cold foam', 'tea', 'matcha', 'passion', 'brown sugar', 'drizzle', 'layer']
                    found_surprise = [elem for elem in surprise_elements if elem in mods_text]
                    print(f"   • Surprise Ingredients: {'✅' if found_surprise else '❌'} {found_surprise}")
                    
                    # Check drive-thru format
                    ordering = data.get('ordering_script', '').lower()
                    has_greeting = 'hi' in ordering or 'hello' in ordering
                    has_request = 'can i get' in ordering or "i'd like" in ordering
                    print(f"   • Drive-thru Format: {'✅' if has_greeting and has_request else '❌'}")
                    
                else:
                    print(f"\n❌ SAMPLE {i}: HTTP {response.status_code}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"\n❌ SAMPLE {i}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(get_sample_responses())
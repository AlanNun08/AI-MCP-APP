import requests
import json
import time

# Test multiple Starbucks recipe generations to see if there's inconsistency
base_url = "https://407d4e17-1478-4b87-bdc3-d8a695a6f09c.preview.emergentagent.com/api"
user_id = "22199c6d-23e4-44b0-93af-9e346f90dd46"

test_cases = [
    {"cuisine_type": "frappuccino", "name": "Frappuccino"},
    {"cuisine_type": "latte", "name": "Latte"},
    {"cuisine_type": "refresher", "name": "Refresher"},
    {"cuisine_type": "macchiato", "name": "Macchiato"},
    {"cuisine_type": "cold_brew", "name": "Cold Brew"}
]

print("Testing multiple Starbucks recipe generations...")

for i, test_case in enumerate(test_cases):
    print(f"\n{'='*50}")
    print(f"Test {i+1}: {test_case['name']}")
    print(f"{'='*50}")
    
    data = {
        "user_id": user_id,
        "recipe_category": "starbucks",
        "cuisine_type": test_case["cuisine_type"],
        "servings": 1,
        "difficulty": "easy"
    }
    
    try:
        print(f"Sending request for {test_case['name']}...")
        start_time = time.time()
        
        response = requests.post(f"{base_url}/recipes/generate", json=data, timeout=45)
        
        elapsed_time = time.time() - start_time
        print(f"Response time: {elapsed_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ SUCCESS: Generated {test_case['name']}")
                print(f"   Drink name: {result.get('drink_name', 'N/A')}")
                print(f"   Category: {result.get('category', 'N/A')}")
                print(f"   ID: {result.get('id', 'N/A')}")
                
                # Check required fields
                required_fields = ['drink_name', 'description', 'base_drink', 'modifications', 'ordering_script', 'pro_tips', 'why_amazing', 'category']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"   ⚠️ Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:200]}...")
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw error: {response.text[:200]}...")
                
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Request took longer than 45 seconds")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Small delay between requests
    time.sleep(1)

print(f"\n{'='*50}")
print("Testing completed!")
print(f"{'='*50}")
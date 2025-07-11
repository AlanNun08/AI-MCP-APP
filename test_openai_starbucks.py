import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Test the exact prompt that the backend is using for Starbucks
prompt = """Create a creative Starbucks drink ordering guide that shows how to order an amazing custom drink at Starbucks. This should be a unique, Instagram-worthy drink like "Fresas con Crema Frappuccino" or "Twix Frappuccino" that uses creative modifications of existing Starbucks menu items.

IMPORTANT: Focus on the frappuccino category and create a drink that fits that style (frappuccino, latte, refresher, cold brew, macchiato, or seasonal special).

Respond with JSON in this exact format:
{
  "drink_name": "Creative catchy name like 'Twix Frappuccino'",
  "description": "Brief description of taste and experience",
  "base_drink": "Base Starbucks drink to order (e.g. 'Grande Vanilla Bean Frappuccino')",
  "modifications": [
    "Add 2 pumps caramel syrup",
    "Add 1 pump hazelnut syrup", 
    "Extra whipped cream",
    "Caramel drizzle on top and bottom"
  ],
  "ordering_script": "Hi, can I get a Grande Vanilla Bean Frappuccino with 2 pumps caramel syrup, 1 pump hazelnut syrup, extra whipped cream, and caramel drizzle on top and bottom?",
  "pro_tips": [
    "Order during off-peak hours for best customization",
    "Ask for extra drizzle to make it Instagram-worthy",
    "Can substitute any milk for extra creaminess"
  ],
  "why_amazing": "Detailed explanation of what makes this drink special and viral-worthy",
  "category": "frappuccino"
}

Make this sound like a viral TikTok Starbucks hack that people would want to try and share!"""

try:
    print("Testing OpenAI Starbucks prompt...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional chef. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # Get the response content
    recipe_json = response.choices[0].message.content.strip()
    print(f"Raw OpenAI Response:\n{recipe_json}")
    
    # Clean up the JSON (remove markdown formatting if present)
    if recipe_json.startswith("```json"):
        recipe_json = recipe_json[7:]
    if recipe_json.endswith("```"):
        recipe_json = recipe_json[:-3]
    
    print(f"\nCleaned JSON:\n{recipe_json}")
    
    # Try to parse the JSON
    try:
        recipe_data = json.loads(recipe_json)
        print(f"\nParsed JSON successfully!")
        print(f"Keys in response: {list(recipe_data.keys())}")
        
        # Check for required fields
        required_fields = ['drink_name', 'description', 'base_drink', 'modifications', 'ordering_script', 'pro_tips', 'why_amazing', 'category']
        missing_fields = [field for field in required_fields if field not in recipe_data]
        
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
        else:
            print("All required fields present!")
            print(f"Drink name: {recipe_data['drink_name']}")
            print(f"Category: {recipe_data['category']}")
            
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        
except Exception as e:
    print(f"OpenAI API error: {e}")
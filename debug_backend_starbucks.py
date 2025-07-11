import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def test_backend_starbucks_generation(recipe_type):
    """Test the exact same process as the backend"""
    
    # Build prompt exactly like the backend
    prompt_parts = []
    
    prompt_parts.append(f"""Create a creative Starbucks drink ordering guide that shows how to order an amazing custom drink at Starbucks. This should be a unique, Instagram-worthy drink like "Fresas con Crema Frappuccino" or "Twix Frappuccino" that uses creative modifications of existing Starbucks menu items.

IMPORTANT: Focus on the {recipe_type} category and create a drink that fits that style (frappuccino, latte, refresher, cold brew, macchiato, or seasonal special).

Respond with JSON in this exact format:
{{
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
  "category": "{recipe_type}"
}}

Make this sound like a viral TikTok Starbucks hack that people would want to try and share!""")
    
    # Add the standard ending like the backend does
    prompt_parts.append("""
Return ONLY a valid JSON object with this exact structure:

{
    "title": "Recipe Name",
    "description": "Brief description",
    "ingredients": ["ingredient 1", "ingredient 2"],
    "instructions": ["step 1", "step 2"],
    "prep_time": 15,
    "cook_time": 30,
    "calories_per_serving": 350,
    "shopping_list": ["ingredient_name_1", "ingredient_name_2"]
}

Recipe Category Guidelines:

SNACKS: Focus on healthy and refreshing snack options such as:
- Acai bowls (frozen acai puree, granola, fresh berries, honey, superfoods)
- Fruit lemon slices chili (fresh fruits, lemon juice, chili powder, lime, Mexican spices)
- Frozen yogurt berry bites (Greek yogurt, mixed berries, natural sweeteners, bite-sized treats)

BEVERAGES: Generate specific beverage recipes based on user selection:

1. LEMONADE-BASED DRINK: Refreshing, fruity, or herbal lemonades perfect for summer with unique fruit combinations, natural sweeteners, and fresh herbs

2. THAI TEA-BASED DRINK: Authentic Thai tea layered or infused with other flavors (fruit, spices, milk alternatives, or syrups) with traditional preparation methods

3. BOBA DRINK: Milk-based or fruit-based bubble tea using tapioca, popping boba, or creative textures with authentic bubble tea shop quality

For each beverage, include:
🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units (cups, tablespoons, ounces)
🍳 Step-by-step instructions including brewing, mixing, and serving techniques
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make each drink visually Instagram-worthy with professional techniques (shaking, layering, temperature control).

CRITICAL FOR BEVERAGE SHOPPING LIST: The shopping_list must contain ONLY clean ingredient names without any quantities, measurements, or preparation instructions. For beverage specifically:
- If ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- If ingredients include "1/4 cup fresh mint leaves" and "ice cubes", the shopping_list should be ["mint", "ice"]
- If ingredients include "1 cup oat milk" and "3/4 cup cooked tapioca pearls", the shopping_list should be ["oat milk", "tapioca pearls"]
- Remove ALL quantities (2 shots, 1/2 cup, 1/4 cup, etc.) and measurements (cups, tablespoons, ounces)
- Remove ALL preparation words (fresh, cooked, diced, chopped, etc.)
- Use clean, searchable ingredient names suitable for Walmart product search

Example beverage ingredients format:
- "2 shots espresso" instead of "espresso"
- "1/2 cup brown sugar syrup" instead of "brown sugar"
- "1 cup oat milk" instead of "milk"
- "3/4 cup cooked tapioca pearls" instead of "tapioca"

CUISINE: Traditional dishes from specific cultures and regions with authentic ingredients and cooking methods.

The shopping_list should be a separate bullet-pointed shopping list that includes only the names of the ingredients (no amounts, no measurements). For example:
- If ingredients include "1 cup diced tomatoes" and "2 tbsp olive oil", the shopping_list should be ["tomatoes", "olive oil"]
- If ingredients include "1 can chickpeas, drained" and "1/2 cup BBQ sauce", the shopping_list should be ["chickpeas", "BBQ sauce"]
- If beverage ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- BEVERAGE SPECIFIC: If ingredients include "4 lemons", "1/2 cup pineapple chunks", "1/4 cup fresh mint leaves", the shopping_list should be ["lemons", "pineapple", "mint"]
- BEVERAGE SPECIFIC: If ingredients include "1 cup oat milk", "ice cubes", "1/2 cup honey", the shopping_list should be ["oat milk", "ice", "honey"]
- Clean ingredient names without quantities, measurements, or preparation instructions

BEVERAGE EXAMPLES for reference (create one specific recipe based on user selection):
- Lemonade: Lavender Honey Lemonade with fresh herbs and edible flowers  
- Thai Tea: Coconut Mango Thai Tea with layered presentation and tropical fruit
- Boba: Taro Coconut Milk Tea with homemade taro paste and chewy tapioca pearls

IMPORTANT FOR SPICES: If the recipe uses spices, list each spice individually in the shopping_list instead of using generic terms like "spices" or "seasoning". For example:
- If ingredients include "2 tsp mixed spices (turmeric, cumin, coriander)", the shopping_list should include ["turmeric", "cumin", "coriander"]
- If ingredients include "1 tbsp garam masala and chili powder", the shopping_list should include ["garam masala", "chili powder"] 
- If ingredients include "salt, pepper, and paprika to taste", the shopping_list should include ["salt", "pepper", "paprika"]
- This ensures users can select specific spices and brands from Walmart rather than searching for generic "spices"
""")
    
    prompt = " ".join(prompt_parts)
    
    print(f"Testing {recipe_type} generation...")
    print(f"Prompt length: {len(prompt)} characters")
    
    try:
        # Call OpenAI exactly like the backend
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional chef. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse the response exactly like the backend
        recipe_json = response.choices[0].message.content.strip()
        print(f"Raw response length: {len(recipe_json)} characters")
        print(f"Raw response preview: {recipe_json[:200]}...")
        
        # Clean up the JSON (remove markdown formatting if present)
        if recipe_json.startswith("```json"):
            recipe_json = recipe_json[7:]
        if recipe_json.endswith("```"):
            recipe_json = recipe_json[:-3]
        
        print(f"Cleaned response preview: {recipe_json[:200]}...")
        
        # Try to parse JSON
        recipe_data = json.loads(recipe_json)
        
        print(f"✅ JSON parsed successfully!")
        print(f"Keys in response: {list(recipe_data.keys())}")
        
        # Check for drink_name specifically
        if 'drink_name' in recipe_data:
            print(f"✅ drink_name found: {recipe_data['drink_name']}")
            return True
        else:
            print(f"❌ drink_name NOT found in response")
            print(f"Available keys: {list(recipe_data.keys())}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Problematic JSON: {recipe_json}")
        return False
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

# Test different recipe types
test_cases = ["frappuccino", "latte", "refresher"]

for recipe_type in test_cases:
    print(f"\n{'='*60}")
    result = test_backend_starbucks_generation(recipe_type)
    print(f"Result: {'SUCCESS' if result else 'FAILED'}")
    print(f"{'='*60}")
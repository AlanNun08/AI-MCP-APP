# AI Recipe Generation Prompts

## OpenAI Configuration

**Model**: `gpt-3.5-turbo`
**System Message**: "You are a professional chef. Always respond with valid JSON only."
**Max Tokens**: 1000
**Temperature**: 0.7

---

## Recipe Category Prompts

### 1. SNACK CATEGORY

#### Acai Bowls
```
Create a delicious and nutritious acai bowl recipe for {servings} people. Focus on frozen acai puree, healthy superfoods, fresh toppings, granola, and colorful presentation. Include preparation techniques for the perfect consistency.
```

#### Fruit Lemon Slices Chili
```
Create a spicy and refreshing fruit lemon slices with chili recipe for {servings} people. Focus on fresh fruits, lemon juice, chili powder, lime, and traditional Mexican-style seasoning. Include cutting techniques and spice combinations.
```

#### Frozen Yogurt Berry Bites
```
Create healthy frozen yogurt berry bites recipe for {servings} people. Focus on Greek yogurt, mixed berries, natural sweeteners, and bite-sized frozen treats. Include freezing techniques and presentation.
```

#### Generic Snack
```
Create a {recipe_type} snack recipe for {servings} people. Focus on tasty, satisfying snacks that are perfect for any time of day.
```

---

### 2. BEVERAGE CATEGORY (Enhanced - 4 Recipes)

```
Generate 4 unique and original beverage recipes for {servings} people, one for each of the following types:

1. Coffee-based drink
   - May include elements like cold foam, whipped crème, flavored syrups, or layered toppings like caramel drizzle — but only if it enhances the concept.

2. Lemonade-based drink  
   - Refreshing, fruity, or herbal — perfect for summer.

3. Thai tea-based drink
   - Layered or infused with other flavors (like fruit, spices, milk alternatives, or syrups).

4. Boba drink (bubble tea)
   - Can be milk-based or fruit-based, and use tapioca, popping boba, or creative textures.

For each drink, include the following:
🧋 Creative, original drink name
✨ Brief flavor description (1–2 sentences that describe taste and style)
🧾 List of ingredients with exact quantities and units
🍳 Step-by-step instructions
💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make the drinks visually Instagram-worthy and perfect for any season.

IMPORTANT FOR BEVERAGE SHOPPING LIST: After all 4 recipes, create a clean shopping_list that contains ONLY the ingredient names without quantities, measurements, or preparation instructions. For example:
- If ingredients include "4 lemons" and "1/2 cup pineapple chunks", the shopping_list should be ["lemons", "pineapple"]
- If ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- If ingredients include "1/4 cup fresh mint leaves" and "ice cubes", the shopping_list should be ["mint", "ice"]
- Clean ingredient names suitable for Walmart product search.
```

---

### 3. CUISINE CATEGORY

#### Snacks & Bowls
```
Create a healthy snack or bowl recipe for {servings} people. Focus on nutritious snacks, smoothie bowls, acai bowls, poke bowls, grain bowls, or energy bites.
```

#### Generic Cuisine
```
Create a {recipe_type or 'delicious'} recipe for {servings} people.
```

---

## Dynamic Parameters

The following parameters are added dynamically based on user input:

### Basic Parameters
- `Difficulty level: {difficulty}.`
- `Dietary preferences: {dietary_preferences}.` (if provided)
- `Try to use these ingredients: {ingredients_on_hand}.` (if provided)
- `Maximum prep time: {prep_time_max} minutes.` (if provided)

### Healthy Mode
- `This should be a healthy recipe with maximum {max_calories_per_serving} calories per serving.` (if healthy mode enabled)

### Budget Mode
- `Keep the total ingredient cost under ${max_budget}.` (if budget mode enabled)

---

## JSON Response Format

### For BEVERAGES (4-recipe format):
```json
{
    "title": "4 Premium Beverage Collection",
    "description": "Four unique and original beverage recipes featuring coffee, lemonade, Thai tea, and boba drinks",
    "ingredients": ["combined list of all ingredients from all 4 recipes"],
    "instructions": [
        "🧋 COFFEE-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 LEMONADE-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 THAI TEA-BASED DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]",
        "",
        "🧋 BOBA DRINK: [Creative Name]",
        "✨ [Brief flavor description]",
        "🧾 Ingredients: [list with exact quantities]",
        "🍳 Instructions: [step-by-step]",
        "💡 Tips: [optional variations]"
    ],
    "prep_time": 45,
    "cook_time": 15,
    "calories_per_serving": 280,
    "shopping_list": ["ingredient_name_1", "ingredient_name_2", "ingredient_name_3"]
}
```

### For SNACKS and CUISINE:
```json
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
```

---

## Recipe Category Guidelines

### SNACKS
Focus on healthy and refreshing snack options such as:
- Acai bowls (frozen acai puree, granola, fresh berries, honey, superfoods)
- Fruit lemon slices chili (fresh fruits, lemon juice, chili powder, lime, Mexican spices)
- Frozen yogurt berry bites (Greek yogurt, mixed berries, natural sweeteners, bite-sized treats)

### BEVERAGES
Generate 4 unique and original beverage recipes with Instagram-worthy presentation:

1. **COFFEE-BASED DRINK**: Specialty espresso drinks, cold brews, or gourmet preparations with elements like cold foam, whipped crème, flavored syrups, or layered toppings like caramel drizzle

2. **LEMONADE-BASED DRINK**: Refreshing, fruity, or herbal lemonades perfect for summer with unique fruit combinations, natural sweeteners, and fresh herbs

3. **THAI TEA-BASED DRINK**: Authentic Thai tea layered or infused with other flavors (fruit, spices, milk alternatives, or syrups) with traditional preparation methods

4. **BOBA DRINK**: Milk-based or fruit-based bubble tea using tapioca, popping boba, or creative textures with authentic bubble tea shop quality

For each of the 4 beverages, include:
- 🧋 Creative, original drink name
- ✨ Brief flavor description (1–2 sentences that describe taste and style)
- 🧾 List of ingredients with exact quantities and units (cups, tablespoons, ounces)
- 🍳 Step-by-step instructions including brewing, mixing, and serving techniques
- 💡 Optional tips or variations (e.g., vegan swap, flavor twist, serving method)

Make each drink visually Instagram-worthy with professional techniques (shaking, layering, temperature control).

CRITICAL FOR BEVERAGE SHOPPING LIST: The shopping_list must contain ONLY clean ingredient names without any quantities, measurements, or preparation instructions. For beverages specifically:
- If ingredients include "4 lemons" and "1/2 cup pineapple chunks", the shopping_list should be ["lemons", "pineapple"]
- If ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- If ingredients include "1/4 cup fresh mint leaves" and "ice cubes", the shopping_list should be ["mint", "ice"]
- If ingredients include "1 cup oat milk" and "3/4 cup cooked tapioca pearls", the shopping_list should be ["oat milk", "tapioca pearls"]
- Remove ALL quantities (4, 1/2 cup, 2 shots, 1/4 cup, etc.) and measurements (cups, tablespoons, ounces)
- Remove ALL preparation words (fresh, cooked, diced, chopped, etc.)
- Use clean, searchable ingredient names suitable for Walmart product search

### CUISINE
Traditional dishes from specific cultures and regions with authentic ingredients and cooking methods.

---

## Shopping List Guidelines

The shopping_list should be a separate bullet-pointed shopping list that includes only the names of the ingredients (no amounts, no measurements). For example:

- If ingredients include "1 cup diced tomatoes" and "2 tbsp olive oil", the shopping_list should be ["tomatoes", "olive oil"]
- If ingredients include "1 can chickpeas, drained" and "1/2 cup BBQ sauce", the shopping_list should be ["chickpeas", "BBQ sauce"]
- If beverage ingredients include "2 shots espresso" and "1/2 cup brown sugar syrup", the shopping_list should be ["espresso beans", "brown sugar"]
- **BEVERAGE SPECIFIC**: If ingredients include "4 lemons", "1/2 cup pineapple chunks", "1/4 cup fresh mint leaves", the shopping_list should be ["lemons", "pineapple", "mint"]
- **BEVERAGE SPECIFIC**: If ingredients include "1 cup oat milk", "ice cubes", "1/2 cup honey", the shopping_list should be ["oat milk", "ice", "honey"]
- Clean ingredient names without quantities, measurements, or preparation instructions

### Beverage Ingredients Format Examples:
- "2 shots espresso" instead of "espresso"
- "1/2 cup brown sugar syrup" instead of "brown sugar"
- "1 cup oat milk" instead of "milk"
- "3/4 cup cooked tapioca pearls" instead of "tapioca"

---

## Example Beverage Recipes (Reference)

Create 4 unique recipes similar to these:
- **Coffee**: Salted Caramel Cold Foam Macchiato with vanilla syrup and sea salt
- **Lemonade**: Lavender Honey Lemonade with fresh herbs and edible flowers  
- **Thai Tea**: Coconut Mango Thai Tea with layered presentation and tropical fruit
- **Boba**: Taro Coconut Milk Tea with homemade taro paste and chewy tapioca pearls

---

## Important Notes for Spices

If the recipe uses spices, list each spice individually in the shopping_list instead of using generic terms like "spices" or "seasoning". For example:

- If ingredients include "2 tsp mixed spices (turmeric, cumin, coriander)", the shopping_list should include ["turmeric", "cumin", "coriander"]
- If ingredients include "1 tbsp garam masala and chili powder", the shopping_list should include ["garam masala", "chili powder"] 
- If ingredients include "salt, pepper, and paprika to taste", the shopping_list should include ["salt", "pepper", "paprika"]
- This ensures users can select specific spices and brands from Walmart rather than searching for generic "spices"

---

## Prompt Assembly

The final prompt is assembled by combining:
1. Category-specific prompt
2. Dynamic parameters (difficulty, dietary preferences, etc.)
3. JSON response format instructions
4. Recipe category guidelines
5. Shopping list guidelines
6. Spice handling instructions

All parts are joined with spaces to create the complete prompt sent to OpenAI.
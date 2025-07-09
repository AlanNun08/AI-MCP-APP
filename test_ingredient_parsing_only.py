import sys
import os

# Add the backend directory to the path so we can import the server module
sys.path.append('/app/backend')

# Import the _extract_core_ingredient function from server.py
try:
    from server import _extract_core_ingredient
    print("Successfully imported _extract_core_ingredient function")
except ImportError as e:
    print(f"Error importing _extract_core_ingredient: {e}")
    sys.exit(1)

def test_ingredient_parsing():
    """Test the _extract_core_ingredient function with specific ingredients"""
    print("=" * 80)
    print("Testing Ingredient Parsing Function")
    print("=" * 80)
    
    # Test ingredients from the user's request
    test_ingredients = [
        "1 can chickpeas, drained and rinsed",
        "1/2 cup BBQ sauce",
        "1 cup cooked quinoa",
        "1 cup mixed vegetables (bell peppers, zucchini, onions)",
        "1 avocado, sliced",
        "2 tbsp olive oil",
        "Salt and pepper to taste"
    ]
    
    # Expected core ingredients
    expected_results = [
        "chickpeas",
        "barbecue sauce",  # or "bbq sauce"
        "quinoa",
        "mixed vegetables",  # or "frozen mixed vegetables"
        "avocado",
        "olive oil",
        "salt pepper"
    ]
    
    # Test each ingredient
    all_passed = True
    
    for i, ingredient in enumerate(test_ingredients):
        print(f"\nTesting ingredient {i+1}: '{ingredient}'")
        
        # Call the function
        result = _extract_core_ingredient(ingredient)
        print(f"  Result: '{result}'")
        
        # Check if the result matches the expected value
        expected = expected_results[i]
        if expected in result or result in expected:
            print(f"  ✅ PASS: Found expected core ingredient '{expected}'")
        else:
            print(f"  ❌ FAIL: Expected '{expected}', got '{result}'")
            all_passed = False
    
    # Print summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All ingredient parsing tests PASSED")
    else:
        print("❌ Some ingredient parsing tests FAILED")
    print("=" * 50)
    
    return all_passed

def main():
    # Test ingredient parsing
    parsing_success = test_ingredient_parsing()
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    if parsing_success:
        print("✅ Ingredient parsing function is working correctly")
        print("✅ The improved parsing logic correctly extracts core ingredients")
        print("✅ The function successfully handles all test cases")
        print("\n✅ OVERALL: The improved ingredient parsing logic is working correctly")
    else:
        print("❌ Issues found with ingredient parsing function")
        print("❌ Some ingredients may not have been parsed correctly")
        print("\n❌ OVERALL: Issues found with the improved ingredient parsing logic")
    
    return 0 if parsing_success else 1

if __name__ == "__main__":
    main()
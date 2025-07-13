# Quick Testing Commands for AI Recipe + Grocery Delivery App

## 🚀 Fast Testing Script

### Environment Setup
```bash
# Preview Environment (Always Working)
PRODUCTION_URL="https://recipe-cart-app-1.emergent.host"

# Deployment Environment  
DEPLOY_URL="https://recipe-cart-app-1.emergent.host"
```

### 1. API Health Check
```bash
echo "🔍 Testing API Health..."
curl -X GET $PREVIEW_URL/api/ | jq
curl -X GET $DEPLOY_URL/api/ | jq
```

### 2. Recipe Generation Test
```bash
echo "🍳 Testing Recipe Generation..."

# Generate a recipe
RECIPE_ID=$(curl -X POST $PREVIEW_URL/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","recipe_category":"snacks","cuisine_type":"cookies","servings":1,"difficulty":"easy"}' \
  -s | jq -r '.id')

echo "Generated Recipe ID: $RECIPE_ID"
```

### 3. Walmart Integration Test (Critical)
```bash
echo "🛒 Testing Walmart Integration..."

# Test cart options with real Walmart product IDs
PRODUCT_ID=$(curl -X POST "$PREVIEW_URL/api/grocery/cart-options?recipe_id=$RECIPE_ID&user_id=test" \
  -H "Content-Type: application/json" \
  -d '{}' -s | jq -r '.ingredient_options[0].options[0].product_id // "manual"')

echo "First Product ID: $PRODUCT_ID"

if [ "$PRODUCT_ID" != "manual" ] && [ "$PRODUCT_ID" != "null" ]; then
    echo "✅ SUCCESS: Real Walmart product ID found: $PRODUCT_ID"
else
    echo "❌ FAILED: No real product IDs - got manual mode"
fi
```

### 4. Full Walmart Cart Test
```bash
echo "🛍️ Testing Complete Walmart Cart..."

# Get full cart response
curl -X POST "$PREVIEW_URL/api/grocery/cart-options?recipe_id=$RECIPE_ID&user_id=test" \
  -H "Content-Type: application/json" \
  -d '{}' -s | jq '{
    mode: .shopping_mode // "walmart",
    ingredients: .ingredient_options | length,
    first_product: .ingredient_options[0].options[0] | {product_id, name, price}
  }'
```

### 5. Authentication Test
```bash
echo "🔐 Testing Authentication..."

# Register user
USER_ID=$(curl -X POST $PREVIEW_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test'$(date +%s)'@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }' -s | jq -r '.user_id // "failed"')

echo "Registered User ID: $USER_ID"
```

### 6. All Categories Test
```bash
echo "📊 Testing All Recipe Categories..."

# Test each category
for category in "cuisine" "snacks" "beverages"; do
    echo "Testing $category..."
    RECIPE=$(curl -X POST $PREVIEW_URL/api/recipes/generate \
      -H "Content-Type: application/json" \
      -d "{\"user_id\":\"test\",\"recipe_category\":\"$category\",\"cuisine_type\":\"test\",\"servings\":1,\"difficulty\":\"easy\"}" \
      -s | jq -r '.title // "failed"')
    echo "$category: $RECIPE"
done

# Test Starbucks
echo "Testing starbucks..."
STARBUCKS=$(curl -X POST $PREVIEW_URL/api/starbucks/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","drink_type":"viral","flavor_profile":"sweet","caffeine_level":"medium"}' \
  -s | jq -r '.name // "failed"')
echo "starbucks: $STARBUCKS"
```

## ⚡ One-Line Super Test

```bash
# Complete test in one command
curl -X POST https://recipe-cart-app-1.emergent.host/api/grocery/cart-options?recipe_id={}&user_id=test" -H "Content-Type: application/json" -d '{}' -s | jq -r '.ingredient_options[0].options[0].product_id // "FAILED"'
```

**Expected Output**: A real Walmart product ID like `10403017` (SUCCESS) or `FAILED`/`manual` (BROKEN)

## 🎯 Success Validation

### ✅ What SUCCESS Looks Like:
```json
{
  "ingredient_options": [
    {
      "ingredient_name": "flour",
      "options": [
        {
          "product_id": "10403017",
          "name": "Great Value All Purpose Flour, 5 lb",
          "price": 2.92
        }
      ]
    }
  ]
}
```

### ❌ What FAILURE Looks Like:
```json
{
  "shopping_mode": "manual",
  "message": "Shopping list ready - visit Walmart.com to purchase these ingredients"
}
```

## 🔧 Quick Fixes

### If Walmart Integration Fails:
1. Check environment variables: `cat /app/backend/.env | grep WALMART`
2. Restart backend: `sudo supervisorctl restart backend`
3. Test API directly: `curl -X GET https://developer.api.walmart.com/ping`

### If Authentication Fails:
1. Check email service: `cat /app/backend/.env | grep MAILJET`
2. Test MongoDB: `mongo --eval "db.runCommand('ping')"`

### If Frontend Doesn't Load:
1. Check backend URL: `cat /app/frontend/.env`
2. Restart frontend: `sudo supervisorctl restart frontend`
3. Clear cache: Update service worker version in `/app/frontend/public/sw.js`

## 🏃‍♂️ Express Deployment Test

```bash
#!/bin/bash
echo "🧪 RAPID DEPLOYMENT TEST"
echo "========================"

# Test API
API_STATUS=$(curl -s https://recipe-cart-app-1.emergent.host/api/ | jq -r '.status // "DOWN"')
echo "API Status: $API_STATUS"

# Test Recipe + Walmart Integration  
WALMART_TEST=$(curl -X POST https://recipe-cart-app-1.emergent.host/api/grocery/cart-options?recipe_id={}&user_id=test" -H "Content-Type: application/json" -d '{}' -s | jq -r '.ingredient_options[0].options[0].product_id // "manual"')

if [ "$WALMART_TEST" != "manual" ] && [ "$WALMART_TEST" != "null" ]; then
    echo "✅ WALMART INTEGRATION: WORKING ($WALMART_TEST)"
else
    echo "❌ WALMART INTEGRATION: FAILED"
fi

# Test Frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://recipe-cart-app-1.emergent.host/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ FRONTEND: WORKING"
else
    echo "❌ FRONTEND: FAILED ($FRONTEND_STATUS)"
fi

echo "========================"
echo "🎯 Test Complete!"
```

Save this as `quick_test.sh` and run: `chmod +x quick_test.sh && ./quick_test.sh`
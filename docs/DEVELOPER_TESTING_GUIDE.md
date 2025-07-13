# 🛠️ AI Recipe + Grocery Delivery App - Developer Testing Guide

## ⚠️ **PRODUCTION-ONLY DEVELOPMENT**
**CRITICAL RULE**: Only develop for production domain `https://recipe-cart-app-1.emergent.host`
- **❌ NEVER use preview URLs**
- **✅ ONLY use production domain**
- **📋 See**: `/docs/PRODUCTION_ONLY_POLICY.md` for complete guidelines

---

## 📋 Quick Testing Commands

### **Production Environment Testing**
```bash
# Test API Health
curl -s https://recipe-cart-app-1.emergent.host/api/ | jq .

# Test Frontend Loading
curl -s https://recipe-cart-app-1.emergent.host/ | head -5

# Environment Configuration
REACT_APP_BACKEND_URL=https://recipe-cart-app-1.emergent.host
```

## 🔧 Backend API Testing

### **1. Health Check**
```bash
curl -X GET https://recipe-cart-app-1.emergent.host/api/
```

### **2. User Registration**
```bash
curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "first_name": "Test", 
    "last_name": "User"
  }'
```

### **3. Email Verification (Debug)**
```bash
# Get verification code (debug endpoint)
curl https://recipe-cart-app-1.emergent.host/api/debug/verification-codes/test@example.com

curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "verification_code": "123456"}'
```

### **4. User Login**
```bash
curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "securepassword123"}'
```

### **5. Recipe Generation**
```bash
# Basic Recipe Generation
curl -X POST https://recipe-cart-app-1.emergent.host/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user", 
    "ingredients": ["chicken", "broccoli", "rice"],
    "cuisine_type": "asian",
    "dietary_restrictions": ["gluten-free"],
    "prep_time": 30,
    "difficulty": "easy"
  }'

# Starbucks Recipe Generation  
curl -X POST https://recipe-cart-app-1.emergent.host/api/generate-starbucks-drink \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "drink_type": "frappuccino", 
    "flavor_inspiration": "vanilla dreams"
  }'
```

### **6. Walmart Integration**
```bash
curl -X POST "https://recipe-cart-app-1.emergent.host/api/grocery/cart-options?recipe_id=RECIPE_ID&user_id=USER_ID"
```

### **7. Community Features**
```bash
# Get Curated Starbucks Recipes
curl -X GET https://recipe-cart-app-1.emergent.host/api/curated-starbucks-recipes

# Get Community Shared Recipes
curl -X GET https://recipe-cart-app-1.emergent.host/api/shared-recipes

# Share a Recipe
curl -X POST https://recipe-cart-app-1.emergent.host/api/share-recipe?user_id=test-user \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_name": "My Amazing Drink",
    "description": "A wonderful creation", 
    "ingredients": ["base", "syrup", "milk"],
    "order_instructions": "Hi, can I get a...",
    "category": "frappuccino"
  }'

# Like a Recipe
curl -X POST https://recipe-cart-app-1.emergent.host/api/like-recipe \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "recipe-uuid",
    "user_id": "test-user"
  }'
```

## 🧪 Testing Workflows

### **Complete User Journey Test**
```bash
#!/bin/bash

echo "🧪 Testing Complete User Journey"

# 1. Register User
echo "📝 Registering user..."
curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "journey@test.com", "password": "test123", "first_name": "Journey", "last_name": "Test"}' \
  -s | jq .

# 2. Get verification code  
echo "🔍 Getting verification code..."
CODE=$(curl -s https://recipe-cart-app-1.emergent.host/api/debug/verification-codes/journey@test.com | jq -r '.verification_code')
echo "Verification code: $CODE"

# 3. Verify email
echo "✅ Verifying email..."
curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/verify \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"journey@test.com\", \"verification_code\": \"$CODE\"}" \
  -s | jq .

# 4. Login
echo "🔐 Logging in..."
LOGIN_RESPONSE=$(curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "journey@test.com", "password": "test123"}' \
  -s)
echo $LOGIN_RESPONSE | jq .

# 5. Generate Recipe
echo "🍳 Generating recipe..."
curl -X POST https://recipe-cart-app-1.emergent.host/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "journey-test", "ingredients": ["chicken", "vegetables"], "cuisine_type": "italian"}' \
  -s | jq .title

echo "✅ User journey test completed!"
```

### **Performance Testing**
```bash
#!/bin/bash

echo "⚡ Performance Testing"

# API Response Time Test
echo "🕐 Testing API response times..."
for i in {1..5}; do
  curl -s -w "%{time_total}\n" -o /dev/null https://recipe-cart-app-1.emergent.host/api/ &
done
wait

echo "✅ Performance test completed!"
```

### **CORS Testing** 
```bash
# Test CORS headers
curl -I -X OPTIONS https://recipe-cart-app-1.emergent.host/api/auth/login

# Test actual CORS request
curl -X POST https://recipe-cart-app-1.emergent.host/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Origin: https://recipe-cart-app-1.emergent.host" \
  -d '{"email": "cors@test.com", "password": "test123", "first_name": "CORS", "last_name": "Test"}' \
  -v
```

## 🎯 Frontend Testing

### **Browser Testing**
1. **Open Production App**: https://recipe-cart-app-1.emergent.host
2. **Test Registration Flow**: Create new account → verify email → login
3. **Test Recipe Generation**: Generate recipes in all categories
4. **Test Starbucks Features**: Use all 5 drink types + community features
5. **Test Mobile Responsiveness**: Check on different screen sizes
6. **Test PWA Features**: Install app, test offline functionality

### **Network Testing**
```javascript
// Test API connectivity from browser console
fetch('https://recipe-cart-app-1.emergent.host/api/')
  .then(response => response.json())
  .then(data => console.log('API Health:', data));

// Test Starbucks generation
fetch('https://recipe-cart-app-1.emergent.host/api/generate-starbucks-drink', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: 'test-user',
    drink_type: 'frappuccino'
  })
})
.then(response => response.json())
.then(data => console.log('Starbucks Recipe:', data));
```

## 🔧 Debugging Commands

### **Service Status**
```bash
# Check all services
sudo supervisorctl status

# Restart services
sudo supervisorctl restart all
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### **Log Monitoring**
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs  
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log
```

### **Database Testing**
```bash
# Test MongoDB connection
mongo --eval "db.users.count()"

# Check collections
mongo ai_recipe_app_production --eval "show collections"
```

## ✅ Success Criteria

### **Backend Health Checks**
- ✅ API responds with 200 status
- ✅ All endpoints return proper JSON
- ✅ Database connections successful
- ✅ External API integrations working

### **Frontend Health Checks**  
- ✅ Page loads under 3 seconds
- ✅ All components render correctly
- ✅ API calls complete successfully
- ✅ PWA features functional

### **Integration Health Checks**
- ✅ User registration/login flow
- ✅ Recipe generation in all categories
- ✅ Walmart product search working
- ✅ Community features operational
- ✅ Email notifications sending

---

**📊 All tests should pass with 100% success rate for production readiness!**
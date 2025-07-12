# AI Recipe + Grocery Delivery App - Complete Testing Guide

## 🎯 Overview

This comprehensive guide documents how the AI Recipe + Grocery Delivery App works in both preview and deployment environments. Use this to test future implementations and validate that the deployment matches expected functionality.

## 🏗️ Application Architecture

### Tech Stack
- **Frontend**: React 19 with PWA capabilities
- **Backend**: FastAPI (Python) with async operations
- **Database**: MongoDB for user data and recipes
- **AI Integration**: OpenAI GPT-3.5 for recipe generation
- **E-commerce**: Walmart Affiliate API for real product integration
- **Email Service**: Mailjet for user verification

### Environment URLs
- **Preview Environment**: https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com
- **Deployment Environment**: https://recipe-cart-app-1.emergent.host
- **Backend API**: Both environments use the working preview backend

## 🔐 Authentication System

### 1. User Registration
**Endpoint**: `POST /api/auth/register`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected Response**:
```json
{
  "message": "User registered successfully. Please check your email for verification code.",
  "user_id": "uuid-string"
}
```

**Validation**:
- ✅ User receives email verification code
- ✅ User is created in MongoDB
- ✅ Password is hashed securely

### 2. Email Verification
**Endpoint**: `POST /api/auth/verify-email`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "verification_code": "123456"
  }'
```

**Expected Response**:
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": "uuid-string",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_verified": true
  }
}
```

### 3. User Login
**Endpoint**: `POST /api/auth/login`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "user": {
    "id": "uuid-string",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_verified": true
  }
}
```

### 4. Authentication Persistence
**Frontend Behavior**:
- ✅ User session saved to `localStorage` with key `ai_chef_user`
- ✅ User remains logged in across page refreshes
- ✅ User can navigate between screens without logout
- ✅ Session restored automatically on app load

**Test Validation**:
1. Login to the app
2. Refresh the page - should remain logged in
3. Navigate: Dashboard → Recipe History → Generate Recipe → Recipe Detail
4. User should stay authenticated throughout

## 🍳 Recipe Generation System

### Recipe Categories
1. **Cuisine Recipes** - Traditional dishes with cultural authenticity
2. **Snack Recipes** - Quick and easy snack options
3. **Beverage Recipes** - Coffee, tea, smoothies, specialty drinks
4. **Starbucks Secret Menu** - Viral drink hacks with ordering instructions

### 1. Cuisine Recipe Generation
**Endpoint**: `POST /api/recipes/generate`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "recipe_category": "cuisine",
    "cuisine_type": "italian",
    "servings": 4,
    "difficulty": "medium"
  }'
```

**Expected Response**:
```json
{
  "id": "recipe-uuid",
  "title": "Authentic Italian Pasta Recipe",
  "description": "Traditional Italian pasta with rich tomato sauce...",
  "ingredients": ["pasta", "tomatoes", "garlic", "olive oil", "basil"],
  "instructions": ["Step 1: Boil water...", "Step 2: Cook pasta..."],
  "prep_time": "30 minutes",
  "servings": 4,
  "difficulty": "medium",
  "category": "cuisine",
  "shopping_list": ["pasta", "tomatoes", "garlic", "olive oil", "basil"]
}
```

### 2. Snack Recipe Generation
**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "recipe_category": "snacks",
    "cuisine_type": "energy balls",
    "servings": 2,
    "difficulty": "easy"
  }'
```

### 3. Beverage Recipe Generation
**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "recipe_category": "beverages",
    "cuisine_type": "coffee",
    "servings": 1,
    "difficulty": "easy"
  }'
```

### 4. Starbucks Secret Menu Generator
**Endpoint**: `POST /api/starbucks/generate`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/starbucks/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "drink_type": "viral tiktok",
    "flavor_profile": "sweet",
    "caffeine_level": "medium"
  }'
```

**Expected Response**:
```json
{
  "id": "drink-uuid",
  "name": "TikTok Famous Brown Sugar Oat Milk Shaken Espresso",
  "description": "Viral drink that's taking social media by storm...",
  "base_drink": "Iced Brown Sugar Oatmilk Shaken Espresso",
  "modifications": ["Add vanilla syrup", "Extra cinnamon"],
  "ordering_script": "Hi, can I get an Iced Brown Sugar Oatmilk Shaken Espresso...",
  "ingredients": ["Espresso", "Brown sugar syrup", "Oat milk"],
  "difficulty": "Medium",
  "popularity": "High"
}
```

## 🛒 Walmart Integration & Affiliate System

### How It Works
1. Recipe generates with `shopping_list` array of ingredients
2. Backend calls Walmart Product Search API for each ingredient
3. Returns real Walmart product IDs (itemId) for affiliate cart building
4. Frontend allows user to select specific products
5. Generates affiliate cart URL with selected product IDs

### 1. Cart Options Generation
**Endpoint**: `POST /api/grocery/cart-options`

**Test Case**:
```bash
# First generate a recipe
RECIPE_ID=$(curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","recipe_category":"snacks","cuisine_type":"cookies","servings":1,"difficulty":"easy"}' \
  | jq -r '.id')

# Then get cart options
curl -X POST "https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/grocery/cart-options?recipe_id=$RECIPE_ID&user_id=test" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response**:
```json
{
  "id": "cart-uuid",
  "user_id": "test",
  "recipe_id": "recipe-uuid",
  "ingredient_options": [
    {
      "ingredient_name": "flour",
      "options": [
        {
          "product_id": "10403017",
          "name": "Great Value All Purpose Flour, 5 lb",
          "price": 2.92,
          "thumbnail_image": "https://i5.walmartimages.com/...",
          "availability": "Available"
        },
        {
          "product_id": "10315247",
          "name": "Gold Medal All Purpose Flour, 5 lb",
          "price": 3.48,
          "thumbnail_image": "https://i5.walmartimages.com/...",
          "availability": "Available"
        }
      ]
    }
  ],
  "created_at": "2025-01-11T10:30:00Z"
}
```

**Validation Checklist**:
- ✅ Real Walmart product IDs (8-11 digit numbers)
- ✅ Authentic product names and prices
- ✅ Multiple options per ingredient (2-3 products)
- ✅ Valid thumbnail images
- ✅ NO mock data (no IDs starting with 10315, mock-, walmart-)

### 2. Custom Cart Creation
**Endpoint**: `POST /api/grocery/custom-cart`

**Test Case**:
```bash
curl -X POST https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com/api/grocery/custom-cart \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "selected_products": [
      {"ingredient_name": "flour", "product_id": "10403017"},
      {"ingredient_name": "sugar", "product_id": "10447781"}
    ]
  }'
```

**Expected Response**:
```json
{
  "walmart_url": "https://affil.walmart.com/cart/addToCart?items=10403017,10447781",
  "total_items": 2,
  "selected_products": [...]
}
```

### 3. Affiliate URL Format
**Correct Format**: `https://affil.walmart.com/cart/addToCart?items=PRODUCT_ID1,PRODUCT_ID2_QUANTITY`

**Examples**:
- Single items: `items=10403017,10447781,10448316`
- With quantities: `items=10403017_2,10447781_1,10448316_3`

## 🖥️ Frontend User Interface

### 1. Landing Page
**URL**: `/`
**Features**:
- ✅ Hero section with app description
- ✅ Login and Register buttons
- ✅ Responsive design
- ✅ PWA installation prompt

### 2. Dashboard
**URL**: `/dashboard` (after login)
**Features**:
- ✅ Recipe category cards (Cuisine, Snacks, Beverages, Starbucks)
- ✅ Recent recipes section
- ✅ User profile access
- ✅ Navigation menu

### 3. Recipe Generation
**URL**: `/generate-recipe`
**Workflow**:
1. User selects category and options
2. AI generates custom recipe
3. Automatic redirect to Recipe Detail page
4. Background generation of Walmart cart options

### 4. Recipe Detail Page
**Features**:
- ✅ Recipe information (title, ingredients, instructions)
- ✅ Two-column layout: Recipe | Shopping Cart
- ✅ Walmart product options for each ingredient
- ✅ Product selection with real prices
- ✅ "Add to Walmart Cart" button with affiliate URL
- ✅ Sticky shopping cart sidebar

### 5. Recipe History
**URL**: `/all-recipes`
**Features**:
- ✅ All user's generated recipes
- ✅ Category filtering (All, Cuisine, Snacks, Beverages, Starbucks)
- ✅ Recipe cards with preview
- ✅ Click to view full recipe

### 6. Starbucks Generator
**URL**: `/starbucks-generator`
**Features**:
- ✅ Specialized interface for Starbucks drinks
- ✅ Drink type selection
- ✅ Flavor and caffeine preferences
- ✅ Ordering script generation
- ✅ No Walmart integration (Starbucks-specific)

## 🧪 Testing Procedures

### Complete User Journey Test
1. **Registration Flow**:
   ```
   Landing Page → Register → Email Verification → Dashboard
   ```

2. **Recipe Generation Flow**:
   ```
   Dashboard → Select Category → Generate Recipe → Recipe Detail → Walmart Cart
   ```

3. **Authentication Persistence Test**:
   ```
   Login → Navigate to Recipe History → Generate Recipe → Refresh Page → Should stay logged in
   ```

4. **Walmart Integration Test**:
   ```
   Generate Recipe → Get Cart Options → Verify Real Product IDs → Test Affiliate URL
   ```

### API Testing Script
```bash
#!/bin/bash
BASE_URL="https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com"

echo "🧪 Testing API Health"
curl -X GET $BASE_URL/api/ | jq

echo "🧪 Testing Recipe Generation"
RECIPE_ID=$(curl -X POST $BASE_URL/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","recipe_category":"cuisine","cuisine_type":"italian","servings":2,"difficulty":"easy"}' \
  | jq -r '.id')

echo "Generated Recipe ID: $RECIPE_ID"

echo "🧪 Testing Walmart Integration"
curl -X POST "$BASE_URL/api/grocery/cart-options?recipe_id=$RECIPE_ID&user_id=test" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.ingredient_options[0].options[0].product_id'
```

### Frontend Testing Checklist
- [ ] All pages load without errors
- [ ] Authentication persistence works
- [ ] Recipe generation in all categories
- [ ] Walmart products display with real IDs
- [ ] Affiliate cart URLs are correctly formatted
- [ ] Mobile responsiveness
- [ ] PWA features (offline capability, install prompt)

## 📱 PWA Features

### Service Worker
- **Cache Version**: Automatically increments for updates
- **Offline Support**: Basic functionality available offline
- **Install Prompt**: Users can install app on mobile devices
- **Push Notifications**: For recipe updates (if enabled)

### Mobile Experience
- ✅ Responsive design for all screen sizes
- ✅ Touch-friendly interface
- ✅ Fast loading with caching
- ✅ Native app-like experience

## 🔧 Environment Configuration

### Required Environment Variables

**Backend (.env)**:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="buildyoursmartcart_production"
OPENAI_API_KEY="sk-proj-..."
WALMART_CONSUMER_ID="eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62"
WALMART_KEY_VERSION="1"
WALMART_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
MAILJET_API_KEY="..."
MAILJET_SECRET_KEY="..."
SENDER_EMAIL="..."
```

**Frontend (.env)**:
```env
REACT_APP_BACKEND_URL=https://310d9b8e-d018-47c6-9b14-e763b8dfbeb2.preview.emergentagent.com
WDS_SOCKET_PORT=443
```

### Service Status Check
```bash
sudo supervisorctl status
# Should show: backend, frontend, mongodb, code-server all RUNNING
```

## 🚨 Common Issues & Solutions

### 1. No Walmart Products Found
**Symptoms**: Cart options return manual shopping mode
**Solution**: Verify environment variables and API credentials

### 2. Authentication Not Persisting
**Symptoms**: User gets logged out on navigation
**Solution**: Check localStorage implementation and session management

### 3. Recipe Generation Fails
**Symptoms**: No recipes generated or errors
**Solution**: Verify OpenAI API key and model availability

### 4. Frontend Not Loading
**Symptoms**: White screen or build errors
**Solution**: Check service worker cache version and restart frontend

## 📋 Deployment Validation

### Pre-Deployment Checklist
- [ ] All environment variables configured
- [ ] Database contains test data
- [ ] Services running properly
- [ ] API endpoints responding
- [ ] Frontend builds successfully

### Post-Deployment Testing
1. **API Health Check**: `GET /api/` returns status
2. **User Registration**: Complete flow works
3. **Recipe Generation**: All categories working
4. **Walmart Integration**: Real product IDs returned
5. **Authentication**: Persistent login works
6. **Mobile Compatibility**: Responsive design

### Success Criteria
- ✅ 100% API endpoint success rate
- ✅ Real Walmart product IDs (not mock data)
- ✅ Persistent user authentication
- ✅ All recipe categories functional
- ✅ Affiliate cart URLs correctly formatted
- ✅ Mobile-responsive interface
- ✅ PWA features working

## 📊 Performance Benchmarks

### Expected Response Times
- Recipe Generation: < 5 seconds
- Walmart Cart Options: < 3 seconds
- User Authentication: < 1 second
- Page Load Times: < 2 seconds

### Database Metrics
- User Registration: Instant
- Recipe Storage: < 500ms
- Recipe Retrieval: < 200ms

---

## 🎯 Summary

This comprehensive guide ensures that both preview and deployment environments work identically with:

1. **Full Authentication System** with persistent login
2. **AI Recipe Generation** across all categories
3. **Real Walmart Integration** with authentic product IDs
4. **Affiliate Cart Building** with proper URL formatting
5. **Mobile-Responsive PWA** with offline capabilities

Use this guide to validate that future implementations maintain the same level of functionality and that deployments match the working preview environment exactly.
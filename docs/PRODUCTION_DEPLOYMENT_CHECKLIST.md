# 🚀 PRODUCTION DEPLOYMENT CHECKLIST

## ✅ PRE-DEPLOYMENT VERIFICATION

### **1. System Status Check**
```bash
# Check all services are running
sudo supervisorctl status
# Expected: All services RUNNING

# Verify API health
curl -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/ | jq .
# Expected: {"status": "running", "version": "2.0.0"}
```

### **2. Environment Configuration**
```bash
# Verify backend environment variables
cd /app/backend && grep -E "MONGO_URL|WALMART_|MAILJET_|OPENAI_" .env
# All required variables should be present

# Verify frontend environment variables  
cd /app/frontend && cat .env
# REACT_APP_BACKEND_URL should point to production domain
```

### **3. Database Connectivity**
```bash
# Test MongoDB connection
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
async def test():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    result = await client.admin.command('ismaster')
    print('MongoDB connected:', result['ismaster'])
asyncio.run(test())
"
```

### **4. Third-Party API Validation**
```bash
# Test Walmart API
python -c "
import os
print('Walmart Consumer ID:', os.getenv('WALMART_CONSUMER_ID', 'NOT SET'))
print('Walmart Key Version:', os.getenv('WALMART_KEY_VERSION', 'NOT SET'))
print('Walmart Private Key Length:', len(os.getenv('WALMART_PRIVATE_KEY', '')))
"

# Test Mailjet API
python -c "
import os
print('Mailjet API Key:', os.getenv('MAILJET_API_KEY', 'NOT SET'))
print('Mailjet Secret Key Length:', len(os.getenv('MAILJET_SECRET_KEY', '')))
print('Mailjet Sender Email:', os.getenv('MAILJET_SENDER_EMAIL', 'NOT SET'))
"

# Test OpenAI API
python -c "
import os
print('OpenAI API Key Length:', len(os.getenv('OPENAI_API_KEY', '')))
"
```

## ✅ COMPREHENSIVE TESTING

### **5. Run Full Test Suite**
```bash
cd /app && python tests/backend_test.py
# Expected: 16/16 tests pass (100% success rate)
```

### **6. Manual Feature Testing**

#### **Authentication Flow**
```bash
# Register new user
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Production",
    "last_name": "Test",
    "email": "prod.test@example.com", 
    "password": "ProdTest123!",
    "dietary_preferences": ["None"],
    "allergies": ["None"],
    "favorite_cuisines": ["Italian"]
  }'

# Get verification code
curl https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/debug/verification-codes/prod.test@example.com

# Verify email (use code from above)
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "prod.test@example.com", "code": "VERIFICATION_CODE"}'

# Test login
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "prod.test@example.com", "password": "ProdTest123!"}'
```

#### **Recipe Generation**
```bash
# Test cuisine recipe
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_category": "cuisine",
    "cuisine_type": "italian",
    "servings": 2,
    "user_id": "USER_ID_FROM_LOGIN",
    "healthy_mode": false,
    "budget_mode": false
  }' | jq .

# Test beverage recipe
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_category": "beverage",
    "cuisine_type": "coffee",
    "servings": 1,
    "user_id": "USER_ID_FROM_LOGIN",
    "healthy_mode": false,
    "budget_mode": false
  }' | jq .

# Test Starbucks recipe
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_category": "starbucks", 
    "cuisine_type": "frappuccino",
    "servings": 1,
    "user_id": "USER_ID_FROM_LOGIN"
  }' | jq .
```

#### **Walmart Integration**
```bash
# Test cart options (use recipe_id from above)
curl -X POST "https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/grocery/cart-options?recipe_id=RECIPE_ID&user_id=USER_ID" | jq .
```

### **7. Frontend Testing**
```bash
# Test frontend loads
curl -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/ | head -10

# Test service worker
curl -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/sw.js | head -5
```

## ✅ PERFORMANCE VALIDATION

### **8. Response Time Testing**
```bash
# API health check timing
curl -w "Total time: %{time_total}s\n" -o /dev/null -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/

# Recipe generation timing
time curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"recipe_category": "cuisine", "cuisine_type": "italian", "servings": 2, "user_id": "test"}' \
  -o /dev/null -s
```

### **9. Concurrent Request Testing**
```bash
# Test 10 concurrent requests
for i in {1..10}; do
  curl -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/ &
done
wait
echo "Concurrent test completed"
```

## ✅ SECURITY VALIDATION

### **10. Security Checks**
```bash
# Check CORS headers
curl -I -X OPTIONS https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/auth/login

# Test input validation
curl -X POST https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' | jq .

# Verify no sensitive data in responses
curl https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/ | grep -i "password\|key\|secret"
```

## ✅ MONITORING & LOGGING

### **11. Log Verification**
```bash
# Check logs are being written
tail -n 10 /var/log/supervisor/backend.out.log
tail -n 10 /var/log/supervisor/frontend.out.log

# No critical errors in logs
grep -i "error\|exception\|critical" /var/log/supervisor/*.log | tail -10
```

### **12. Service Monitoring**
```bash
# Check process status
ps aux | grep -E "(python|node|mongod)" | grep -v grep

# Check system resources
df -h
free -h
```

## ✅ POST-DEPLOYMENT VERIFICATION

### **13. Production Smoke Tests**
After deployment, run these tests on the production URL:

```bash
# Replace with actual production URL
PROD_URL="https://your-production-domain.com"

# Health check
curl -s $PROD_URL/api/ | jq .

# Frontend load
curl -s $PROD_URL/ | head -5

# Test registration flow
curl -X POST $PROD_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Prod",
    "last_name": "User",
    "email": "production.test@yourdomain.com",
    "password": "SecureProd123!",
    "dietary_preferences": ["None"],
    "allergies": ["None"],
    "favorite_cuisines": ["Italian"]
  }'
```

### **14. User Acceptance Testing**
- [ ] User can access the website
- [ ] User can register a new account
- [ ] User receives verification email
- [ ] User can verify their email
- [ ] User can log in successfully
- [ ] User can generate recipes in all categories
- [ ] User can view Walmart shopping cart
- [ ] User can access recipe history
- [ ] User can reset their password
- [ ] All buttons and features work

## ✅ DEPLOYMENT SUCCESS CRITERIA

- [ ] All 16 backend tests pass ✅
- [ ] All environment variables configured ✅
- [ ] Database connectivity verified ✅
- [ ] Third-party APIs tested ✅
- [ ] Authentication flow working ✅
- [ ] Recipe generation functional ✅
- [ ] Walmart integration operational ✅
- [ ] Email service sending codes ✅
- [ ] Frontend loading properly ✅
- [ ] Performance meets benchmarks ✅
- [ ] Security validation complete ✅
- [ ] No critical errors in logs ✅
- [ ] User acceptance tests pass ✅

## 🚨 ROLLBACK PLAN

If any critical issues are found after deployment:

1. **Immediate Actions**
   ```bash
   # Revert to previous version
   git checkout PREVIOUS_VERSION_TAG
   
   # Restart services
   sudo supervisorctl restart all
   
   # Verify rollback
   curl -s https://4a624c76-fc66-4a7c-91df-de079314ff82.preview.emergentagent.com/api/ | jq .
   ```

2. **Communication**
   - Notify stakeholders of the rollback
   - Document the issues encountered
   - Plan resolution for next deployment

## 📊 DEPLOYMENT METRICS

Track these metrics post-deployment:
- **Response Times**: API < 500ms, Recipe Generation < 3000ms
- **Success Rates**: Registration > 99%, Login > 99%, Recipe Generation > 95%
- **Error Rates**: < 1% for all endpoints
- **Uptime**: > 99.9%
- **User Satisfaction**: Monitor user feedback and support tickets

## 🎉 DEPLOYMENT COMPLETE

When all checklist items are verified:
- [ ] Document deployment time and version
- [ ] Update monitoring dashboards  
- [ ] Notify team of successful deployment
- [ ] Monitor for first 24 hours
- [ ] Archive deployment logs

**The AI Recipe + Grocery Delivery App is ready for production deployment!** 🚀
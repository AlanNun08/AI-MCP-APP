# 🚫 DEVELOPMENT POLICY: PRODUCTION-ONLY CODE

## ⚠️ CRITICAL RULE: NO PREVIEW WEBSITE CODE

### **STRICT POLICY**
- **❌ NEVER generate preview website code**
- **❌ NEVER create preview-specific URLs or configurations**
- **❌ NEVER use preview domains in documentation**
- **❌ NEVER add preview environment variables**
- **✅ ONLY create production deployment code**
- **✅ ONLY use production domain: https://recipe-cart-app-1.emergent.host**

---

## 🎯 **PRODUCTION-ONLY DEVELOPMENT GUIDELINES**

### **Environment Configuration Rules**
```env
# ✅ CORRECT - Production only
REACT_APP_BACKEND_URL=https://recipe-cart-app-1.emergent.host

# ❌ FORBIDDEN - Never use preview URLs
REACT_APP_BACKEND_URL=https://[any-id].preview.emergentagent.com
```

### **Documentation Standards**
- **✅ All curl examples**: Use `https://recipe-cart-app-1.emergent.host`
- **✅ All testing scripts**: Point to production domain
- **✅ All user guides**: Reference production URL only
- **❌ No preview URLs**: In any documentation files

### **Code Configuration Standards**
```javascript
// ✅ CORRECT - Production domain
const API_URL = process.env.REACT_APP_BACKEND_URL; // Points to production

// ❌ FORBIDDEN - Hardcoded preview URLs
const API_URL = "https://anything.preview.emergentagent.com";
```

### **CORS Configuration Standards**
```python
# ✅ CORRECT - Production domain only
allow_origins=[
    "https://recipe-cart-app-1.emergent.host",  # Production
    "http://localhost:3000",                    # Local development
]

# ❌ FORBIDDEN - Preview domains
allow_origins=[
    "https://anything.preview.emergentagent.com"
]
```

---

## 🔧 **APPROVED ENVIRONMENTS**

### **✅ ALLOWED ENVIRONMENTS**
1. **Local Development**
   - Backend: `http://localhost:8001`
   - Frontend: `http://localhost:3000`
   - Purpose: Development and testing

2. **Production Deployment**
   - URL: `https://recipe-cart-app-1.emergent.host`
   - Purpose: Live application for end users

### **❌ FORBIDDEN ENVIRONMENTS**
- **Preview environments**: Any `.preview.emergentagent.com` URLs
- **Staging environments**: Any temporary or preview domains
- **Test environments**: Any non-production external URLs

---

## 📋 **DEVELOPER CHECKLIST**

Before committing any code, ensure:

### **✅ Configuration Check**
- [ ] All `.env` files point to production domain
- [ ] No preview URLs in environment variables
- [ ] CORS settings include production domain only
- [ ] Service worker cache names are production-focused

### **✅ Documentation Check**
- [ ] All curl examples use production URLs
- [ ] All testing scripts reference production
- [ ] User guides point to production site
- [ ] No preview URLs in any markdown files

### **✅ Code Review Check**
- [ ] No hardcoded preview URLs in JavaScript/Python
- [ ] All API calls use environment variables
- [ ] No preview-specific conditionals or logic
- [ ] Production domain consistently used

---

## 🚨 **VIOLATION CONSEQUENCES**

### **If Preview Code is Found:**
1. **Immediate Removal**: Delete all preview references
2. **Configuration Update**: Point everything to production
3. **Documentation Cleanup**: Remove preview URLs
4. **Testing**: Verify production functionality
5. **Cache Invalidation**: Update service worker versions

---

## ✅ **PRODUCTION-ONLY COMMANDS**

### **Development Commands**
```bash
# ✅ Start local development
npm start  # Uses localhost for development

# ✅ Build for production
npm run build  # Uses production environment variables
```

### **Testing Commands**
```bash
# ✅ Test production API
curl -s https://recipe-cart-app-1.emergent.host/api/

# ✅ Run production verification
./verify_production.sh
```

### **Deployment Commands**
```bash
# ✅ Deploy to production
sudo supervisorctl restart all

# ✅ Check production status
sudo supervisorctl status
```

---

## 📚 **REFERENCE DOCUMENTATION**

### **Production-Only Files**
- `/app/README.md` - Production application guide
- `/app/verify_production.sh` - Production testing script
- `/app/frontend/.env.production` - Production environment config
- `/app/docs/PRODUCTION_DEPLOYMENT_CHECKLIST.md` - Production deployment

### **Production Domain**
- **Live Application**: https://recipe-cart-app-1.emergent.host
- **API Endpoints**: https://recipe-cart-app-1.emergent.host/api/
- **Documentation**: All guides reference this domain

---

## 🎯 **SUMMARY**

**REMEMBER**: This application has **ONE PRODUCTION DOMAIN** only:
**https://recipe-cart-app-1.emergent.host**

- **✅ All code** should work with this domain
- **✅ All documentation** should reference this domain  
- **✅ All testing** should verify this domain
- **❌ Never create** preview-specific code
- **❌ Never use** preview URLs anywhere

---

**🚀 Keep it simple: PRODUCTION ONLY!**
# Production Deployment Configuration for buildyoursmartcart.com

## Backend Configuration
The backend should be deployed and accessible at: https://buildyoursmartcart.com/api

### Environment Variables for Production Backend:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=ai_recipe_app_production
OPENAI_API_KEY=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
WALMART_CONSUMER_ID=eb0f49e9-fe3f-4c3b-8709-6c0c704c5d62
WALMART_KEY_VERSION=1
WALMART_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQChD5cdZ5YhVzu9
4eMXMqPaoHndt8lM8cgdFi3zLxc2CfPr4Ga8TBnz8JmT+dnjXYvz47jeNnLRF95b
udPTwm822W8s+LVIb4mvnD71sSa0eVMoe0r91xtb0viEt0AW2mTkCdK6R8TdQLvz
kcN2z/iHo7u/dEQI3LJUA6tbza7sENpz1TZC9pGtpokpTaC3nrlqFvsXlmTxcDZX
Bvys6JBeyJe7gY//NgaSiHog37MqXHV99VRCjRBOUmp5NcIPi0narqaZo60KRLEC
AGlqZIdPWaMlmMkO+sEeFOCzvqUP5N0UR/EYUqtNZoMrMCzCPowC13FjUCn47k5U
/bea4xjpAgMBAAECggEAAjt9dleAF9Z2EiXSQFkv9vjsM3/ngwDja47KBIHBtjqp
VjrCJcg+wFg0gr3u8JU0ekUM5AyYZxBIAVi4KEpcwQN+xF5uodJE8+mMIFrsHMqF
Ne2Ojqnne8x27Bz/nwl4JkaCFJmnz4LFECVUMp6DlPq2oJrXkhFgCeTSoFc/nk9A
XF+DpAgN1ww/sm/s8TXM4+8TAr+fShkv89qp8LYvK4J6KIdqO+ayidklNXS4/zjL
Gt0yV2OUYoHZYXchjeyAxkE3CCzijI8GddV+vuYE6crPVPvMfSJvDNyCeN9LbWpR
Yxmqg5Oh6GIbQxCgxa6489O6QEJ0Lyj1eF1LgGYiwQKBgQDQd2K/qCLjMiz2TeMg
feFU1DGJ0JPADEXUzGljNnyNmJc4G8saO8HkW8JYqkmsQxm+O3wCCXCF1WnDuMZe
GTDDdzeh6coMmbTCI6CG9S6soyZhObTT5Mm0U0kX/cwXR2rHq7puzvwYFl4a9aEd
7Cy5qRjuQAW5b84bxG8kxgQ9QQKBgQDFyQzBxJZZ3y3585U7Gw78vRRYofdTR+FW
7R1kp/PG1RaEk3fSScLZdLAP5CnkHS7TZcHwKP/b2/BBxVQVWo9znCY7EwEfzcoE
rdfiEKqL2dPlb7YHSmlcvxVi75NItnoRoHq8TwD53Tu6auy0NqFfNlwrbKXNC/3i
XZ0E/DdpqQKBgEa0d1Wx3UNZvU481JAsocR3w+WOTM6SWwz117jCvjP4UTHCm3xm
UDj3tk8EUsCOcajH3COEuBlsbNbpUL6RpKxnPwM3nEPxzhEarFOZzR7YpyfKvr4v
lwoGRYBRoGs02c6nPDBhG7e/vmM+dEsF05WU+NO1+zsN5MYeNeQvFTkBAoGAKF1a
tCTpxles62kR2KkyCtSP1XLgpedyjqn/qK46KycL3Gy4NHuHP5f34pZfEkX+a3hF
9zx20yj0xIeAHIeJ5T9F8iJzxUjbZM8R0voxxC7ldtqwnJZMIHiC5dkdBubuzLAi
vFGnUlcbPHVb73+CuYq/jsEyqUE8RDl0tTLAIFkCgYB8qgvZNpCWUL1Fe9hFXz9D
N/Aor9OBxVySMsceg9ejW7/iUcRsqy4KEQPwMD5dQVbEsjCWFzPZrh53llyi0q6n
w/n0UuoRcmZ7kLrFIOf6ZStmHnZ1BX/6VKD4m9k6O9LSCGxPWhU+k7uqaFnH720g
0Sj9Z58+3ELzkinERznDcg==
-----END PRIVATE KEY-----
MAILJET_API_KEY=5c7ca7fe01cf13886b5ce84fd3a1aff9
MAILJET_SECRET_KEY=dd922beab20d156a49faff9e140380f9
SENDER_EMAIL=Alan.nunez0310@icloud.com
```

## Frontend Configuration
The frontend should be deployed to: https://buildyoursmartcart.com

### Environment Variables for Production Frontend:
```
REACT_APP_BACKEND_URL=https://buildyoursmartcart.com
WDS_SOCKET_PORT=443
```

## Login Credentials (Updated)
- **Email:** alannunezsilva0310@gmail.com
- **Password:** password123

## Deployment Architecture
- Frontend: React app served from https://buildyoursmartcart.com
- Backend: FastAPI server accessible at https://buildyoursmartcart.com/api/*
- Database: MongoDB (ensure it's accessible from the backend)

## Testing the Deployment
1. Navigate to https://buildyoursmartcart.com
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try logging in with the credentials above
4. Check browser console for any API errors

## Troubleshooting Common Issues
1. **CORS Errors:** Backend is configured to allow https://buildyoursmartcart.com
2. **API Connection:** Backend endpoints should be accessible at https://buildyoursmartcart.com/api/
3. **Environment Variables:** Ensure all environment variables are properly set in production
4. **Database Connection:** Make sure MongoDB is accessible from the production server

## Cache Clearing Script
If the user still has cache issues, run this in the browser console:
```javascript
(async function() {
    if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)));
    }
    if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (let registration of registrations) {
            await registration.unregister();
        }
    }
    localStorage.clear();
    sessionStorage.clear();
    alert('Cache cleared! Page will reload.');
    window.location.reload(true);
})();
```
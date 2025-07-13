#!/usr/bin/env python3
"""
Direct Walmart API Test
Test the Walmart API directly to see if the issue is with the API calls themselves
"""

import asyncio
import httpx
import os
import logging
from dotenv import load_dotenv

# Load environment variables  
load_dotenv('/app/backend/.env')

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_walmart_api_directly():
    """Test Walmart API directly"""
    
    # Get credentials
    WALMART_CONSUMER_ID = os.environ.get('WALMART_CONSUMER_ID')
    WALMART_PRIVATE_KEY = os.environ.get('WALMART_PRIVATE_KEY') 
    WALMART_KEY_VERSION = os.environ.get('WALMART_KEY_VERSION')
    
    logger.info(f"Walmart Consumer ID: {WALMART_CONSUMER_ID}")
    logger.info(f"Walmart Key Version: {WALMART_KEY_VERSION}")
    logger.info(f"Private Key Length: {len(WALMART_PRIVATE_KEY) if WALMART_PRIVATE_KEY else 'None'}")
    
    if not all([WALMART_CONSUMER_ID, WALMART_PRIVATE_KEY, WALMART_KEY_VERSION]):
        logger.error("❌ Missing Walmart API credentials")
        return
    
    # Import the signature function from the backend
    import sys
    sys.path.append('/app/backend')
    
    try:
        # Test the signature generation
        from datetime import datetime
        import time
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        import base64
        
        # Generate timestamp
        current_utc = datetime.utcnow()
        timestamp = str(int(current_utc.timestamp() * 1000))
        
        logger.info(f"Generated timestamp: {timestamp}")
        
        # Create string to sign
        string_to_sign = f"{WALMART_CONSUMER_ID}\n{timestamp}\n{WALMART_KEY_VERSION}\n"
        logger.info(f"String to sign: {repr(string_to_sign)}")
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            WALMART_PRIVATE_KEY.encode('utf-8'),
            password=None
        )
        
        # Sign with RSA-SHA256
        signature_bytes = private_key.sign(
            string_to_sign.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Encode to base64
        signature = base64.b64encode(signature_bytes).decode('utf-8')
        logger.info(f"Generated signature: {signature[:50]}... (length: {len(signature)})")
        
        # Test API call
        ingredient = "eggs"
        query = ingredient.replace(' ', '+')
        url = f"https://developer.api.walmart.com/api-proxy/service/affil/product/v2/search?query={query}&numItems=3"
        
        headers = {
            "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
            "WM_CONSUMER.INTIMESTAMP": timestamp,
            "WM_SEC.KEY_VERSION": WALMART_KEY_VERSION,
            "WM_SEC.AUTH_SIGNATURE": signature,
            "Content-Type": "application/json",
            "User-Agent": "BuildYourSmartCart/1.0"
        }
        
        logger.info(f"🌐 Testing Walmart API call for '{ingredient}'")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {headers}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            logger.info(f"📡 Response Status: {response.status_code}")
            logger.info(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success! Response data keys: {list(data.keys())}")
                
                if 'items' in data:
                    items = data['items']
                    logger.info(f"✅ Found {len(items)} items for '{ingredient}'")
                    
                    for i, item in enumerate(items[:3]):
                        product_id = item.get('itemId')
                        name = item.get('name')
                        price = item.get('salePrice')
                        
                        logger.info(f"   Product {i+1}: {name} - ${price} (ID: {product_id})")
                else:
                    logger.warning("⚠️ No 'items' key in response")
                    logger.info(f"Response data: {data}")
            else:
                logger.error(f"❌ API Error: {response.status_code}")
                logger.error(f"Response text: {response.text}")
                
    except Exception as e:
        logger.error(f"💥 Direct API test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_walmart_api_directly())
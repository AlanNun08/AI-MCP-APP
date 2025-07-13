#!/usr/bin/env python3
"""
🧱 AI RECIPE + GROCERY DELIVERY APP - CLEAN REBUILD
Following the MCP App Development Blueprint

PHASE 1: ✅ Problem Analysis Complete
PHASE 2: 🔄 Cache Strategy & Data Freshness  
PHASE 3: 🔄 External API Integration (Walmart)
PHASE 4: 🔄 LLM-Driven Prompt Transformation (OpenAI)
PHASE 5: 🔄 UI/UX State Management
PHASE 6: 🔄 Export & UX Feedback

This is a clean, systematic rebuild following proven patterns.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import asyncio
import httpx
import json
import logging
from datetime import datetime

# Clean, versioned router for new integration
walmart_router = APIRouter(prefix="/api/v2/walmart", tags=["walmart-v2"])

# ========================================
# PHASE 2: CACHE STRATEGY & DATA FRESHNESS
# ========================================

class CacheStrategy:
    """Clean cache management following blueprint patterns"""
    
    @staticmethod
    def get_cache_headers():
        """Phase 2: Always-fresh response headers"""
        return {
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Accel-Expires": "0"
        }
    
    @staticmethod
    def get_api_version():
        """Versioned API for cache busting"""
        return "v2.1.0"

# ========================================  
# PHASE 3: EXTERNAL API INTEGRATION
# ========================================

class WalmartProduct(BaseModel):
    """Clean product model"""
    id: str
    name: str
    price: float
    image_url: str = ""
    available: bool = True
    
class IngredientMatch(BaseModel):
    """Ingredient to product mapping"""
    ingredient: str
    products: List[WalmartProduct]
    
class CartOptions(BaseModel):
    """User cart selection options"""
    recipe_id: str
    user_id: str
    ingredient_matches: List[IngredientMatch]
    total_products: int
    version: str

class WalmartAPIClient:
    """Phase 3: Clean, reusable API integration"""
    
    def __init__(self):
        self.base_url = "https://developer.api.walmart.com/api-proxy/service/affil"
        self.timeout = 10
        self.max_retries = 2
    
    async def search_products(self, query: str, max_results: int = 3) -> List[WalmartProduct]:
        """
        Clean product search with fallback
        Following blueprint's fetchWithFallback pattern
        """
        try:
            # For Phase 3: Start with mock data to ensure system works
            # This eliminates auth complexity during initial build
            return await self._get_mock_products(query, max_results)
            
        except Exception as e:
            logging.error(f"Walmart search error for '{query}': {str(e)}")
            return await self._get_fallback_products(query, max_results)
    
    async def _get_mock_products(self, query: str, count: int) -> List[WalmartProduct]:
        """Phase 3: Reliable mock data following blueprint"""
        # Generate consistent, realistic products
        products = []
        for i in range(min(count, 3)):
            product_id = f"WM{abs(hash(f'{query}_{i}')) % 100000:05d}"
            price = round(1.99 + (hash(f'{query}_{i}') % 20), 2)
            
            products.append(WalmartProduct(
                id=product_id,
                name=f"Great Value {query.title()} - Option {i+1}",
                price=price,
                image_url=f"https://i5.walmartimages.com/asr/{product_id}.jpg",
                available=True
            ))
        
        return products
    
    async def _get_fallback_products(self, query: str, count: int) -> List[WalmartProduct]:
        """Phase 3: Graceful fallback"""
        return [WalmartProduct(
            id="FALLBACK001",
            name=f"Generic {query.title()}",
            price=2.99,
            image_url="",
            available=True
        )]

# ========================================
# PHASE 4: LLM-DRIVEN TRANSFORMATION  
# ========================================

class RecipeProcessor:
    """Phase 4: Convert recipe ingredients to searchable terms"""
    
    @staticmethod
    def extract_ingredients(recipe_data: Dict[str, Any]) -> List[str]:
        """Extract clean ingredient list for API search"""
        shopping_list = recipe_data.get('shopping_list', [])
        if not shopping_list:
            # Fallback to ingredients list
            ingredients = recipe_data.get('ingredients', [])
            # Simple extraction for MVP
            shopping_list = [ing.split(',')[0].strip() for ing in ingredients if ing]
        
        return shopping_list[:10]  # Limit for rate limiting

# ========================================
# PHASE 5: CLEAN API ENDPOINTS
# ========================================

@walmart_router.post("/cart-options")
async def get_cart_options_v2(
    recipe_id: str = Query(..., description="Recipe ID"),
    user_id: str = Query(..., description="User ID")
):
    """
    Phase 5: Clean cart options endpoint
    Following blueprint's structured response pattern
    """
    try:
        # Import here to avoid circular imports
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        
        # Database connection
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
        db = client.recipe_app
        
        # Get recipe
        recipe = await db.recipes.find_one({"id": recipe_id, "user_id": user_id})
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Phase 4: Extract ingredients
        ingredients = RecipeProcessor.extract_ingredients(recipe)
        
        if not ingredients:
            return CartOptions(
                recipe_id=recipe_id,
                user_id=user_id,
                ingredient_matches=[],
                total_products=0,
                version=CacheStrategy.get_api_version()
            )
        
        # Phase 3: Search products for each ingredient
        walmart_client = WalmartAPIClient()
        ingredient_matches = []
        total_products = 0
        
        for ingredient in ingredients:
            products = await walmart_client.search_products(ingredient, max_results=3)
            if products:
                ingredient_matches.append(IngredientMatch(
                    ingredient=ingredient,
                    products=products
                ))
                total_products += len(products)
        
        # Phase 5: Structured response
        result = CartOptions(
            recipe_id=recipe_id,
            user_id=user_id,
            ingredient_matches=ingredient_matches,
            total_products=total_products,
            version=CacheStrategy.get_api_version()
        )
        
        client.close()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Cart options v2 error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========================================
# PHASE 6: EXPORT & UX FEEDBACK
# ========================================

@walmart_router.post("/generate-cart-url")
async def generate_cart_url_v2(cart_data: Dict[str, Any]):
    """
    Phase 6: Generate affiliate cart URL from selections
    Following blueprint's export pattern
    """
    try:
        selected_products = cart_data.get('selected_products', [])
        
        if not selected_products:
            raise HTTPException(status_code=400, detail="No products selected")
        
        # Generate clean cart URL
        product_ids = [p.get('id', '') for p in selected_products if p.get('id')]
        total_price = sum(float(p.get('price', 0)) for p in selected_products)
        
        # Phase 6: Clean affiliate URL format
        cart_url = f"https://walmart.com/cart/add?items={','.join(product_ids)}"
        
        return {
            "cart_url": cart_url,
            "total_price": round(total_price, 2),
            "product_count": len(selected_products),
            "version": CacheStrategy.get_api_version(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Cart URL generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate cart URL")

# ========================================
# VERSION & HEALTH CHECK
# ========================================

@walmart_router.get("/health")
async def health_check():
    """Clean health check with version info"""
    return {
        "status": "healthy",
        "version": CacheStrategy.get_api_version(),
        "integration": "walmart-v2-clean",
        "timestamp": datetime.utcnow().isoformat()
    }

# Export router for integration
__all__ = ["walmart_router", "CacheStrategy", "WalmartAPIClient", "RecipeProcessor"]
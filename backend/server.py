from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import base64
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Product Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    subcategory: str
    brand: str
    image_url: str
    image_base64: Optional[str] = None
    tags: List[str] = []
    in_stock: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    subcategory: str
    brand: str
    image_url: str
    image_base64: Optional[str] = None
    tags: List[str] = []

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None

class ImageSearchRequest(BaseModel):
    image_base64: str
    category: Optional[str] = None

# Sample products data
SAMPLE_PRODUCTS = [
    {
        "name": "Classic Leather Sneakers",
        "description": "Premium leather sneakers with comfortable cushioning, perfect for casual and semi-formal occasions",
        "price": 129.99,
        "category": "men",
        "subcategory": "shoes",
        "brand": "StyleCraft",
        "image_url": "https://images.unsplash.com/photo-1592840054664-6bc0f6fbc3d6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzaG9wcGluZ3xlbnwwfHx8d2hpdGV8MTc1MzgwMzc2NXww&ixlib=rb-4.1.0&q=85",
        "tags": ["leather", "sneakers", "casual", "comfortable", "premium"]
    },
    {
        "name": "Elegant Fashion Dress",
        "description": "Stylish white dress perfect for special occasions and professional settings",
        "price": 89.99,
        "category": "women",
        "subcategory": "clothing",
        "brand": "ElegantStyle",
        "image_url": "https://images.unsplash.com/photo-1603344797033-f0f4f587ab60?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxmYXNoaW9ufGVufDB8fHx3aGl0ZXwxNzUzODAzNzcxfDA&ixlib=rb-4.1.0&q=85",
        "tags": ["dress", "elegant", "white", "professional", "special occasion"]
    },
    {
        "name": "Premium Face Moisturizer",
        "description": "Advanced anti-aging moisturizer with natural ingredients for glowing skin",
        "price": 45.99,
        "category": "cosmetics",
        "subcategory": "skincare",
        "brand": "GlowBeauty",
        "image_url": "https://images.pexels.com/photos/4123709/pexels-photo-4123709.jpeg",
        "tags": ["moisturizer", "anti-aging", "skincare", "natural", "premium"]
    },
    {
        "name": "Designer Handbag",
        "description": "Luxury designer handbag with premium materials and elegant design",
        "price": 299.99,
        "category": "women",
        "subcategory": "accessories",
        "brand": "LuxuryCraft",
        "image_url": "https://images.pexels.com/photos/3434997/pexels-photo-3434997.jpeg",
        "tags": ["handbag", "luxury", "designer", "accessories", "premium"]
    },
    {
        "name": "Classic Business Shirt",
        "description": "Professional cotton shirt perfect for business and formal occasions",
        "price": 59.99,
        "category": "men",
        "subcategory": "clothing",
        "brand": "BusinessWear",
        "image_url": "https://images.unsplash.com/photo-1585144860131-245d551c77f6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHw0fHxzaG9wcGluZ3xlbnwwfHx8d2hpdGV8MTc1MzgwMzc2NXww&ixlib=rb-4.1.0&q=85",
        "tags": ["shirt", "business", "cotton", "formal", "professional"]
    },
    {
        "name": "High-Heel Pumps",
        "description": "Elegant black high-heel pumps perfect for formal events and professional settings",
        "price": 79.99,
        "category": "women",
        "subcategory": "shoes",
        "brand": "ElegantSteps",
        "image_url": "https://images.unsplash.com/photo-1592840054664-6bc0f6fbc3d6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzaG9wcGluZ3xlbnwwfHx8d2hpdGV8MTc1MzgwMzc2NXww&ixlib=rb-4.1.0&q=85",
        "tags": ["heels", "pumps", "elegant", "formal", "professional"]
    },
    {
        "name": "Luxury Lipstick Set",
        "description": "Premium lipstick collection with long-lasting formula and rich colors",
        "price": 34.99,
        "category": "cosmetics",
        "subcategory": "makeup",
        "brand": "GlamourPro",
        "image_url": "https://images.pexels.com/photos/4123709/pexels-photo-4123709.jpeg",
        "tags": ["lipstick", "makeup", "luxury", "long-lasting", "collection"]
    },
    {
        "name": "Casual Canvas Shoes",
        "description": "Comfortable canvas shoes perfect for everyday wear and casual outings",
        "price": 49.99,
        "category": "men",
        "subcategory": "shoes",
        "brand": "ComfortWalk",
        "image_url": "https://images.unsplash.com/photo-1592840054664-6bc0f6fbc3d6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxzaG9wcGluZ3xlbnwwfHx8d2hpdGV8MTc1MzgwMzc2NXww&ixlib=rb-4.1.0&q=85",
        "tags": ["canvas", "casual", "comfortable", "everyday", "shoes"]
    }
]

# Initialize database with sample products
@api_router.post("/init-products")
async def init_sample_products():
    try:
        # Clear existing products
        await db.products.delete_many({})
        
        # Insert sample products
        products = []
        for product_data in SAMPLE_PRODUCTS:
            product = Product(**product_data)
            products.append(product.dict())
        
        result = await db.products.insert_many(products)
        return {"message": f"Initialized {len(result.inserted_ids)} sample products"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product CRUD endpoints
@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    limit: int = 50
):
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        if subcategory:
            filter_query["subcategory"] = subcategory
            
        products = await db.products.find(filter_query).limit(limit).to_list(limit)
        return [Product(**product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    try:
        product = await db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return Product(**product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    try:
        product_obj = Product(**product.dict())
        await db.products.insert_one(product_obj.dict())
        return product_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@api_router.post("/search")
async def search_products(search_request: SearchRequest):
    try:
        query = search_request.query.lower()
        filter_query = {}
        
        # Text search in name, description, tags, brand
        text_conditions = [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"brand": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [{"$regex": query, "$options": "i"}]}}
        ]
        
        filter_query["$or"] = text_conditions
        
        # Category filter
        if search_request.category:
            filter_query["category"] = search_request.category
            
        # Price filters
        if search_request.min_price is not None or search_request.max_price is not None:
            price_filter = {}
            if search_request.min_price is not None:
                price_filter["$gte"] = search_request.min_price
            if search_request.max_price is not None:
                price_filter["$lte"] = search_request.max_price
            filter_query["price"] = price_filter
        
        products = await db.products.find(filter_query).limit(50).to_list(50)
        return [Product(**product) for product in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/search/image")
async def search_by_image(search_request: ImageSearchRequest):
    try:
        # For now, return all products with category filter if provided
        # This will be enhanced with actual image analysis later
        filter_query = {}
        if search_request.category:
            filter_query["category"] = search_request.category
            
        products = await db.products.find(filter_query).limit(20).to_list(20)
        return {
            "message": "Image search functionality will be enhanced with AI",
            "products": [Product(**product) for product in products]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Categories endpoint
@api_router.get("/categories")
async def get_categories():
    try:
        categories = await db.products.distinct("category")
        subcategories = await db.products.distinct("subcategory")
        return {
            "categories": categories,
            "subcategories": subcategories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@api_router.get("/")
async def root():
    return {"message": "AI Shopping Mall API is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
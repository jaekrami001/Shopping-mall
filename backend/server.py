from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import base64
import json
from jose import JWTError, jwt
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "a_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# User Model
class User(BaseModel):
    username: str
    hashed_password: str

class Cart(BaseModel):
    username: str
    products: List[str] = []

class Message(BaseModel):
    sender: str
    receiver: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_user(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return User(**user)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user

from starlette.requests import Request
from starlette.responses import JSONResponse

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )

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

from pydantic import validator

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

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

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

# Token endpoint
@api_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Initialize database with sample products and a default user
@api_router.post("/init-products")
async def init_sample_products():
    try:
        # Clear existing products and users
        await db.products.delete_many({})
        await db.users.delete_many({})
        
        # Insert sample products
        products = []
        for product_data in SAMPLE_PRODUCTS:
            product = Product(**product_data)
            products.append(product.dict())
        
        result = await db.products.insert_many(products)

        # Insert a default user
        hashed_password = pwd_context.hash("password")
        await db.users.insert_one({"username": "user", "hashed_password": hashed_password})

        return {"message": f"Initialized {len(result.inserted_ids)} sample products and 1 user"}
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
async def create_product(product: ProductCreate, current_user: User = Depends(get_current_user)):
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
            {"tags": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
            {"subcategory": {"$regex": query, "$options": "i"}}
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

# Cart endpoints
@api_router.get("/cart", response_model=Cart)
async def get_cart(current_user: User = Depends(get_current_user)):
    cart = await db.carts.find_one({"username": current_user.username})
    if not cart:
        return Cart(username=current_user.username)
    return Cart(**cart)

@api_router.post("/cart", response_model=Cart)
async def add_to_cart(product_id: str, current_user: User = Depends(get_current_user)):
    await db.carts.update_one(
        {"username": current_user.username},
        {"$push": {"products": product_id}},
        upsert=True
    )
    cart = await db.carts.find_one({"username": current_user.username})
    return Cart(**cart)

@api_router.delete("/cart/{product_id}", response_model=Cart)
async def remove_from_cart(product_id: str, current_user: User = Depends(get_current_user)):
    await db.carts.update_one(
        {"username": current_user.username},
        {"$pull": {"products": product_id}}
    )
    cart = await db.carts.find_one({"username": current_user.username})
    return Cart(**cart)

# Chat endpoints
@api_router.get("/chat", response_model=List[Message])
async def get_messages(current_user: User = Depends(get_current_user)):
    messages = await db.messages.find(
        {"$or": [{"sender": current_user.username}, {"receiver": current_user.username}]}
    ).to_list(100)
    return [Message(**message) for message in messages]

@api_router.post("/chat", response_model=Message)
async def send_message(message: Message, current_user: User = Depends(get_current_user)):
    if message.sender != current_user.username:
        raise HTTPException(status_code=403, detail="You can only send messages as yourself")
    await db.messages.insert_one(message.dict())
    return message

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
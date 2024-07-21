from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import uuid
import random

app = FastAPI()


# Configure CORS
origins = [
    "http://localhost:3000",  # Example: Allow requests from localhost:3000
    "https://your-frontend-domain.com",  # Allow requests from your production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# In-memory list for valid API keys
VALID_API_KEYS: List[str] = []

# In-memory data store for sales data
sales_data = {
    "total_sales": 1000,
    "number_of_orders": 150,
    "daily_sales": [
        {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
         "name": (datetime.now() - timedelta(days=i)).strftime("%A"),
         "uv": random.randint(1000, 4000),
         "pv": random.randint(1000, 4000),
         "amt": random.randint(1000, 4000)}
        for i in range(7)
    ]
}

# API Key Header
api_key_header = APIKeyHeader(name='API-Key', auto_error=False)

# Dependency to verify API key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header is empty or missing"
        )
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login(request: LoginRequest):
    if not request.email or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password must be provided"
        )
    # Generate a new API key
    api_key = str(uuid.uuid4())
    VALID_API_KEYS.append(api_key)
    return {"api_key": api_key}

@app.get("/dashboard/metrics")
async def get_metrics(api_key: str = Depends(get_api_key)):
    return {
        "total_sales": sales_data["total_sales"],
        "number_of_orders": sales_data["number_of_orders"]
    }

@app.get("/dashboard/weekly-sales")
async def get_weekly_sales(api_key: str = Depends(get_api_key)):
    return sales_data["daily_sales"]



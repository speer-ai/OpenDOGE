from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import contracts

app = FastAPI(
    title="OpenDOGE API",
    description="Open Department of Government Efficiency API",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["contracts"])

@app.get("/")
async def root():
    return {"message": "Welcome to OpenDOGE API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
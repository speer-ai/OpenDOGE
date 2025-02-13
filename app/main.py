from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import usaspending, treasury

app = FastAPI(title="OpenDOGE", description="Open source platform for analyzing government spending data")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(usaspending.router, prefix="/api/v1")
app.include_router(treasury.router, prefix="/api/v1")

@app.get("/")
async def root(request: Request):
    """Serve the main dashboard"""
    return templates.TemplateResponse("usaspending.html", {"request": request})

@app.get("/contract")
async def contract_details(request: Request):
    """Serve the contract details page"""
    return templates.TemplateResponse("contract_details.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
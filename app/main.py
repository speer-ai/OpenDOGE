from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import usaspending, treasury, government_data
from app.core.config import settings

app = FastAPI(
    title="OpenDOGE",
    description="Open Data on Government Expenditure",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(usaspending.router, prefix="/api/v1/usaspending", tags=["USAspending"])
app.include_router(treasury.router, prefix="/api/v1/treasury", tags=["Treasury"])
app.include_router(
    government_data.router,
    prefix="/api/v1/government-data",
    tags=["Government Data"]
)

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
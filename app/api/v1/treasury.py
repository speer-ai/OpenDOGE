from fastapi import APIRouter, Query
from app.services.scrapers.treasury import TreasuryClient
from app.core.cache import get_cache, set_cache, generate_cache_key
from app.core.logger import logger

router = APIRouter(prefix="/treasury", tags=["Treasury"])

@router.get("/debt/current")
async def get_current_debt():
    """Get the current national debt information"""
    # Try to get from cache first
    cache_key = "current_debt"
    cached_data = await get_cache(cache_key)
    if cached_data:
        logger.info("Returning cached debt data")
        return cached_data
    
    # Fetch fresh data
    client = TreasuryClient()
    data = await client.get_debt_to_penny()
    
    if "error" not in data:
        # Cache for 1 hour
        await set_cache(cache_key, data, expire=3600)
    
    return data

@router.get("/debt/historical")
async def get_historical_debt(
    days: int = Query(365, description="Number of days of historical data to retrieve", ge=1, le=366)
):
    """Get historical national debt information"""
    # Try to get from cache first
    cache_key = generate_cache_key("historical_debt", days=days)
    cached_data = await get_cache(cache_key)
    if cached_data:
        logger.info("Returning cached historical debt data")
        return cached_data
    
    # Fetch fresh data
    client = TreasuryClient()
    data = await client.get_debt_historical(days=days)
    
    if "error" not in data:
        # Cache for 1 hour
        await set_cache(cache_key, data, expire=3600)
    
    return data 
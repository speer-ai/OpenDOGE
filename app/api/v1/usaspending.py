from typing import Optional, List
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

from app.services.scrapers.usaspending import USSpendingClient

router = APIRouter(prefix="/usaspending", tags=["USAspending.gov"])

@router.get("/awards/recent")
async def get_recent_awards(
    days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(10, description="Number of awards to return"),
    award_types: List[str] = Query(["A", "B", "C", "D"], description="Award type codes")
):
    """Get recent contract awards"""
    client = USSpendingClient()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_period = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    return await client.search_awards(
        time_period=time_period,
        award_type=award_types,
        limit=limit
    )

@router.get("/federal-accounts")
async def get_federal_accounts(
    fiscal_year: Optional[int] = Query(None, description="Fiscal year to query"),
    limit: int = Query(10, description="Number of accounts to return")
):
    """Get federal account information"""
    client = USSpendingClient()
    if fiscal_year is None:
        fiscal_year = datetime.now().year
        
    return await client.get_federal_accounts(
        fiscal_year=fiscal_year,
        limit=limit
    )

@router.get("/state/{state_code}")
async def get_state_spending(
    state_code: str,
    fiscal_year: Optional[int] = Query(None, description="Fiscal year to query")
):
    """Get spending data for a specific state"""
    client = USSpendingClient()
    if fiscal_year is None:
        fiscal_year = datetime.now().year
        
    return await client.get_state_data(
        state_code=state_code,
        fiscal_year=fiscal_year
    )

@router.get("/search")
async def search_awards(
    keyword: str = Query(..., description="Search keyword"),
    days: int = Query(365, description="Number of days to look back"),
    limit: int = Query(10, description="Number of awards to return"),
    award_types: List[str] = Query(["A", "B", "C", "D"], description="Award type codes")
):
    """Search for specific awards"""
    client = USSpendingClient()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_period = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    return await client.search_awards(
        keyword=keyword,
        time_period=time_period,
        award_type=award_types,
        limit=limit
    ) 
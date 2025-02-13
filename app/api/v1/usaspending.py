from typing import Optional, List
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy import select

from app.services.scrapers.usaspending import USSpendingClient
from app.core.cache import get_cache, set_cache, generate_cache_key
from app.db.session import get_db
from app.models.awards import Award
from app.core.config import settings
from app.core.logger import logger
from app.services.ai.smart_search import process_search_query, get_search_suggestions
from app.services.scrapers.data_collector import DataCollector

router = APIRouter(prefix="/usaspending", tags=["USAspending.gov"])

@router.get("/awards/recent")
async def get_recent_awards(
    days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(100, description="Number of awards to return"),
    page: int = Query(1, description="Page number"),
    award_types: List[str] = Query(["A", "B", "C", "D"], description="Award type codes"),
    min_amount: float = Query(1000000, description="Minimum award amount"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent contract awards from database with API fallback"""
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Try to get from database first
        query = select(Award).where(
            Award.award_amount >= min_amount,
            Award.award_type.in_(award_types),
            Award.start_date >= start_date,
            Award.start_date <= end_date
        ).order_by(Award.start_date.desc())
        
        # Add pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        awards = result.scalars().all()
        
        if awards:
            logger.info(f"Retrieved {len(awards)} awards from database")
            return {
                "results": [award.raw_data for award in awards],
                "page": page,
                "has_more": len(awards) == limit
            }
            
        # If no data in database, fetch from API
        logger.info("No data in database, fetching from API...")
        collector = DataCollector()
        awards = await collector.collect_recent_awards(days=days, min_amount=min_amount)
        
        if awards:
            # Store in database for future use
            await collector.store_awards(awards)
            
            # Return paginated results
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_awards = awards[start_idx:end_idx]
            
            return {
                "results": paginated_awards,
                "page": page,
                "has_more": end_idx < len(awards)
            }
            
        return {"results": [], "page": page, "has_more": False}
        
    except Exception as e:
        logger.error(f"Error fetching recent awards: {str(e)}")
        return {"results": [], "error": str(e), "page": page, "has_more": False}

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
    award_types: List[str] = Query(["A", "B", "C", "D"], description="Award type codes"),
    agency: Optional[str] = Query(None, description="Agency code to filter by"),
    state: Optional[str] = Query(None, description="State code to filter by"),
    min_amount: float = Query(0, description="Minimum award amount")
):
    """Search for specific awards"""
    client = USSpendingClient()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    time_period = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    # Build filters
    filters = {
        "award_type_codes": award_types,
        "time_period": [time_period],
        "award_amounts": [
            {
                "lower_bound": min_amount,
                "upper_bound": 1000000000000  # $1 trillion as upper bound
            }
        ]
    }
    
    if state:
        filters["recipient_locations"] = [{"country": "USA", "state": state}]
    
    if agency:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency}]
    
    logger.info(f"Searching awards with keyword: {keyword}, min_amount: ${min_amount:,.2f}")
    return await client.search_awards(
        keyword=keyword,
        time_period=time_period,
        award_type=award_types,
        limit=limit,
        filters=filters
    )

@router.get("/awards/{award_id}")
async def get_award_details(award_id: str):
    """Get detailed information about a specific award"""
    client = USSpendingClient()
    try:
        logger.info(f"Fetching details for award {award_id}")
        data = await client.get_award_details(award_id)
        
        if "error" in data:
            logger.error(f"Error fetching award {award_id}: {data['error']}")
            return {"error": data["error"]}
            
        # Format the response data
        formatted_data = {
            "award_id": award_id,
            "description": data.get("description", "No description available"),
            "amount": float(data.get("total_obligation", 0)),
            "award_type": data.get("type", "Unknown"),
            "period_of_performance_start_date": data.get("period_of_performance_start_date"),
            "period_of_performance_end_date": data.get("period_of_performance_end_date"),
            "status": data.get("status", "Unknown"),
            
            # Agency information
            "awarding_agency_name": data.get("awarding_agency", {}).get("name", "Unknown"),
            "funding_agency_name": data.get("funding_agency", {}).get("name", "Unknown"),
            "awarding_sub_agency_name": data.get("awarding_agency", {}).get("subtier_agency", {}).get("name", "Unknown"),
            
            # Recipient information
            "recipient_name": data.get("recipient", {}).get("recipient_name", "Unknown"),
            "recipient_duns": data.get("recipient", {}).get("duns", "Unknown"),
            "recipient_business_type": data.get("recipient", {}).get("business_types_description", "Unknown"),
            "recipient_city": data.get("recipient", {}).get("location", {}).get("city_name", "Unknown"),
            "recipient_state": data.get("recipient", {}).get("location", {}).get("state_code", "Unknown"),
            "recipient_zip": data.get("recipient", {}).get("location", {}).get("zip5", "Unknown"),
            "recipient_congressional_district": data.get("recipient", {}).get("location", {}).get("congressional_code", "Unknown"),
            
            # Additional details
            "naics": data.get("naics", ""),
            "psc": data.get("psc", "")
        }
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error processing award {award_id}: {str(e)}")
        return {"error": str(e)}

@router.post("/smart-search")
async def smart_search(
    query: str = Query(..., description="Natural language search query"),
    include_suggestions: bool = Query(False, description="Whether to include search suggestions")
):
    """
    Process a natural language search query and return matching contracts
    """
    try:
        # Process the natural language query
        search_params = await process_search_query(query)
        
        # Get suggestions if requested
        suggestions = await get_search_suggestions(query) if include_suggestions else None
        
        # Convert min_amount to actual value
        min_amount = 0
        if search_params.get("min_amount"):
            amount_map = {
                "1m+": 1000000,
                "10m+": 10000000,
                "100m+": 100000000,
                "1b+": 1000000000
            }
            min_amount = amount_map.get(search_params["min_amount"], 0)
        
        # Perform the actual search
        client = USSpendingClient()
        results = await search_awards(
            keyword=search_params.get("keyword", ""),
            days=search_params.get("days", 365),
            limit=50,
            agency=search_params.get("agency", ""),
            min_amount=min_amount
        )
        
        # Return combined results
        response = {
            "search_params": search_params,
            "results": results
        }
        
        if suggestions:
            response["suggestions"] = suggestions
            
        return response
        
    except Exception as e:
        logger.error(f"Error in smart search: {str(e)}")
        return {"error": str(e)} 
from typing import Optional, Dict, Any, List
import aiohttp
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USSpendingClient:
    """Client for interacting with the USAspending.gov API"""
    
    BASE_URL = "https://api.usaspending.gov/api/v2"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
    
    async def search_awards(
        self,
        keyword: Optional[str] = None,
        award_type: Optional[List[str]] = None,
        time_period: Optional[Dict] = None,
        page: int = 1,
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search for award data including contracts, grants, and other spending
        """
        try:
            # Get current date for time period
            now = datetime.now()
            start_date = now - timedelta(days=365)  # Look back 1 year by default
            
            payload = {
                "page": page,
                "limit": limit,
                "fields": [
                    "Award ID",
                    "Recipient Name",
                    "Description",
                    "Award Amount",
                    "Start Date",
                    "End Date",
                    "Award Type",
                    "Awarding Agency",
                    "Funding Agency",
                    "recipient_state"
                ],
                "sort": "Award Amount",
                "order": "desc",
                "subawards": False
            }
            
            # Ensure we have valid filters
            if filters:
                payload["filters"] = filters
            else:
                # Default filters to ensure we get data
                payload["filters"] = {
                    "award_type_codes": award_type or ["A", "B", "C", "D"],  # Contract types
                    "time_period": [time_period] if time_period else [{
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": now.strftime("%Y-%m-%d")
                    }],
                    "award_amounts": [
                        {
                            "lower_bound": 1000000,
                            "upper_bound": 1000000000000  # $1 trillion as upper bound instead of None
                        }
                    ]
                }
            
            if keyword and isinstance(keyword, str):
                payload["filters"]["keywords"] = [keyword]
            
            logger.info(f"Making request to USAspending API with payload: {payload}")
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/search/spending_by_award/"
                logger.info(f"Request URL: {url}")
                
                async with session.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}")
                    logger.info(f"Response text: {response_text[:500]}...")  # Log first 500 chars
                    
                    if response.status == 200:
                        data = await response.json()
                        result_count = len(data.get('results', []))
                        logger.info(f"Successfully retrieved {result_count} results")
                        return data
                    else:
                        error_msg = f"API Error ({response.status}): {response_text}"
                        logger.error(error_msg)
                        return {"results": [], "error": error_msg}
                        
        except Exception as e:
            error_msg = f"Exception in search_awards: {str(e)}"
            logger.error(error_msg)
            return {"results": [], "error": error_msg}
    
    async def get_award_details(self, award_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific award"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/awards/{award_id}/"
                logger.info(f"Fetching award details for {award_id}")
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully retrieved details for award {award_id}")
                        return data
                    
                    error_text = await response.text()
                    error_msg = f"Error fetching award {award_id}: {error_text}"
                    logger.error(error_msg)
                    return {"error": error_msg}
                    
        except Exception as e:
            error_msg = f"Exception fetching award {award_id}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def get_federal_accounts(
        self,
        fiscal_year: Optional[int] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get federal account information"""
        payload = {
            "filters": {
                "fy": str(fiscal_year) if fiscal_year else None
            },
            "page": page,
            "limit": limit,
            "sort": {
                "field": "budgetary_resources",
                "direction": "desc"
            }
        }
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/federal_accounts/",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {"data": result.get("results", [])}
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")

    async def get_agency_spending(
        self,
        fiscal_year: int,
        agency_id: str
    ) -> Dict[str, Any]:
        """Get detailed agency spending data"""
        payload = {
            "fiscal_year": fiscal_year,
            "agency": agency_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/agency/{agency_id}/spending/",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")

    async def get_recipient_profile(
        self,
        recipient_id: str,
        fiscal_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get detailed recipient/contractor profile"""
        params = {"recipient_id": recipient_id}
        if fiscal_year:
            params["fiscal_year"] = fiscal_year
            
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/recipient/profile/",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")

    async def get_subawards(
        self,
        award_id: str,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get subawards for a specific award"""
        params = {
            "award_id": award_id,
            "page": page,
            "limit": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/subawards/",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")

    async def get_spending_by_category(
        self,
        fiscal_year: int,
        category: str,  # e.g., 'awarding_agency', 'recipient', 'cfda'
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get spending aggregated by various categories"""
        payload = {
            "fiscal_year": fiscal_year,
            "category": category,
            "filters": filters or {}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/search/spending_by_category/",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")

    async def get_state_data(
        self,
        state_code: str,
        fiscal_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get spending data for a specific state"""
        payload = {
            "scope": "recipient_location",
            "geo_layer": "state",
            "data_type": "obligated_amount",
            "filters": {
                "recipient_locations": [{
                    "country": "USA",
                    "state": state_code
                }],
                "time_period": [
                    {
                        "start_date": f"{fiscal_year}-10-01" if fiscal_year else "2024-10-01",
                        "end_date": f"{fiscal_year + 1}-09-30" if fiscal_year else "2025-09-30"
                    }
                ]
            }
        }
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/search/spending_by_geography/",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}") 
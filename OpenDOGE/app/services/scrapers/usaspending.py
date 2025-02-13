from typing import Optional, Dict, Any, List
import aiohttp
from datetime import datetime
from app.core.config import settings

class USSpendingClient:
    """Client for interacting with the USSpending.gov API"""
    
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
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search for award data including contracts, grants, and other spending
        """
        payload = {
            "page": page,
            "limit": limit,
            "filters": {
                "keywords": [keyword] if keyword else [],
                "award_type_codes": award_type or [],
                "time_period": [time_period] if time_period else []
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/search/spending_by_award/",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")
    
    async def get_award_details(self, award_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific award
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/awards/{award_id}/",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}")
    
    async def get_federal_accounts(
        self,
        fiscal_year: Optional[int] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get federal account information
        """
        params = {
            "page": page,
            "limit": limit
        }
        if fiscal_year:
            params["fiscal_year"] = fiscal_year
            
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/federal_accounts/",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
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
        params = {"state_code": state_code}
        if fiscal_year:
            params["fiscal_year"] = fiscal_year
            
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/recipient/state/{state_code}/",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"USSpending API Error: {error_text}") 
"""Additional government data source clients"""
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FPDSClient:
    """Federal Procurement Data System API Client"""
    
    BASE_URL = "https://api.fpds.gov/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FPDS_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def get_contract_opportunities(self, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Get active contract opportunities"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/opportunities"
                params = {
                    "page": page,
                    "limit": limit,
                    "status": "active"
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"FPDS API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error fetching FPDS opportunities: {str(e)}")
            return {"error": str(e)}

class FBOClient:
    """Federal Business Opportunities (beta.SAM.gov) API Client"""
    
    BASE_URL = "https://api.sam.gov/opportunities/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SAM_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def search_opportunities(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search contract opportunities"""
        try:
            params = {
                "page": page,
                "limit": limit,
            }
            if keyword:
                params["q"] = keyword
            if status:
                params["status"] = status
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/search",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"FBO API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error searching FBO opportunities: {str(e)}")
            return {"error": str(e)}

class FSRSClient:
    """Federal Subaward Reporting System API Client"""
    
    BASE_URL = "https://api.fsrs.gov/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FSRS_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def get_subawards(
        self,
        prime_award_id: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get subaward data"""
        try:
            params = {
                "page": page,
                "limit": limit
            }
            if prime_award_id:
                params["prime_award_id"] = prime_award_id
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/subawards",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"FSRS API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error fetching subawards: {str(e)}")
            return {"error": str(e)}

class DataGovClient:
    """Data.gov API Client"""
    
    BASE_URL = "https://api.data.gov/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DATA_GOV_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
    
    async def search_datasets(
        self,
        keyword: str,
        agency: Optional[str] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search government datasets"""
        try:
            params = {
                "q": keyword,
                "page": page,
                "limit": limit
            }
            if agency:
                params["agency"] = agency
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/datasets",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"Data.gov API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error searching datasets: {str(e)}")
            return {"error": str(e)}

class FederalReserveClient:
    """Federal Reserve Economic Data (FRED) API Client"""
    
    BASE_URL = "https://api.stlouisfed.org/fred/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FRED_API_KEY
        self.headers = {
            "Content-Type": "application/json"
        }
    
    async def get_economic_data(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get economic data series"""
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json"
            }
            if start_date:
                params["observation_start"] = start_date
            if end_date:
                params["observation_end"] = end_date
                
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/series/observations",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"FRED API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error fetching economic data: {str(e)}")
            return {"error": str(e)}

class SECClient:
    """SEC EDGAR API Client"""
    
    BASE_URL = "https://data.sec.gov/api/v1"
    
    def __init__(self):
        self.headers = {
            "User-Agent": f"OpenDOGE/1.0 ({settings.SEC_EMAIL})"
        }
    
    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """Get company financial facts"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/companies/{cik}/facts",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"SEC API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error fetching company facts: {str(e)}")
            return {"error": str(e)}

    async def get_company_submissions(self, cik: str) -> Dict[str, Any]:
        """Get company SEC submissions"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/companies/{cik}/submissions",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"SEC API Error: {error_text}")
        except Exception as e:
            logger.error(f"Error fetching company submissions: {str(e)}")
            return {"error": str(e)} 
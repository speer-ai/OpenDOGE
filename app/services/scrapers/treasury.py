from typing import Optional, Dict, Any
import aiohttp
from datetime import datetime
from app.core.config import settings

class SAMClient:
    BASE_URL = "https://api.sam.gov/entity-information/v3"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def search_entities(
        self,
        keyword: Optional[str] = None,
        cage_code: Optional[str] = None,
        duns: Optional[str] = None,
        page_size: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Search for entity (contractor) information
        """
        params = {
            "page": page,
            "size": page_size,
        }
        
        if keyword:
            params["q"] = keyword
        if cage_code:
            params["cageCode"] = cage_code
        if duns:
            params["ueiDUNS"] = duns
            
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.BASE_URL + "/entities",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"SAM API Error: {error_text}")

    async def get_contract_opportunities(
        self,
        posted_from: Optional[datetime] = None,
        posted_to: Optional[datetime] = None,
        status: Optional[str] = None,
        page_size: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get contract opportunities
        """
        params = {
            "page": page,
            "size": page_size,
        }
        
        if posted_from:
            params["postedFrom"] = posted_from.isoformat()
        if posted_to:
            params["postedTo"] = posted_to.isoformat()
        if status:
            params["status"] = status
            
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.sam.gov/opportunities/v2/search",
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"SAM API Error: {error_text}") 
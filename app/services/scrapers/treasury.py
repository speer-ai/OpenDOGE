from typing import Optional, Dict, Any
import aiohttp
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

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

class TreasuryClient:
    """Client for interacting with the Treasury Fiscal Data API"""
    
    BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }
    
    async def get_debt_to_penny(self) -> Dict[str, Any]:
        """Get the latest national debt information"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get the most recent debt information
                url = f"{self.BASE_URL}/v2/accounting/od/debt_to_penny"
                params = {
                    "sort": "-record_date",  # Sort by date descending
                    "limit": 1  # Get only the most recent record
                }
                
                logger.info("Fetching latest debt information from Treasury API")
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("data") and len(data["data"]) > 0:
                            latest = data["data"][0]
                            # Format the response
                            return {
                                "total_debt": float(latest.get("tot_pub_debt_out_amt", 0)),
                                "debt_held_public": float(latest.get("debt_held_public_amt", 0)),
                                "intragov_holdings": float(latest.get("intragov_hold_amt", 0)),
                                "record_date": latest.get("record_date"),
                                "as_of": datetime.utcnow().isoformat()
                            }
                        else:
                            error_msg = "No debt data available"
                            logger.error(error_msg)
                            return {"error": error_msg}
                    else:
                        error_msg = f"Treasury API Error: {response.status}"
                        logger.error(error_msg)
                        return {"error": error_msg}
                        
        except Exception as e:
            error_msg = f"Error fetching debt information: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def get_debt_historical(self, days: int = 365) -> Dict[str, Any]:
        """Get historical debt information"""
        try:
            async with aiohttp.ClientSession() as session:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                url = f"{self.BASE_URL}/v2/accounting/od/debt_to_penny"
                params = {
                    "filter": f"record_date:gte:{start_date.strftime('%Y-%m-%d')}",
                    "sort": "-record_date",
                    "page[size]": 366  # Get up to a year of daily data
                }
                
                logger.info(f"Fetching historical debt data for the last {days} days")
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("data"):
                            # Format the response
                            return {
                                "data": [{
                                    "date": record["record_date"],
                                    "total_debt": float(record["tot_pub_debt_out_amt"]),
                                    "debt_held_public": float(record["debt_held_public_amt"]),
                                    "intragov_holdings": float(record["intragov_hold_amt"])
                                } for record in data["data"]],
                                "as_of": datetime.utcnow().isoformat()
                            }
                        else:
                            error_msg = "No historical debt data available"
                            logger.error(error_msg)
                            return {"error": error_msg}
                    else:
                        error_msg = f"Treasury API Error: {response.status}"
                        logger.error(error_msg)
                        return {"error": error_msg}
                        
        except Exception as e:
            error_msg = f"Error fetching historical debt data: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg} 
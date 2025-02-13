from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.awards import Award
from app.services.scrapers.usaspending import USSpendingClient
from app.services.scrapers.treasury import TreasuryClient, SAMClient
from app.core.logger import logger
from app.core.config import settings

class DataCollector:
    """Service for collecting and storing data from multiple sources"""
    
    def __init__(self):
        self.usaspending_client = USSpendingClient()
        self.treasury_client = TreasuryClient()
        self.sam_client = SAMClient(settings.SAM_API_KEY)
        
    async def collect_recent_awards(self, days: int = 30, min_amount: float = 1000000) -> List[Dict]:
        """Collect recent awards with proper pagination"""
        all_awards = []
        page = 1
        has_more = True
        
        while has_more:
            try:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                time_period = {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
                
                # Fetch page of results
                result = await self.usaspending_client.search_awards(
                    time_period=time_period,
                    award_type=["A", "B", "C", "D"],
                    limit=100,  # Max page size
                    page=page,
                    filters={
                        "award_type_codes": ["A", "B", "C", "D"],
                        "time_period": [time_period],
                        "award_amounts": [{
                            "lower_bound": min_amount,
                            "upper_bound": 1000000000000
                        }]
                    }
                )
                
                if result.get("results"):
                    all_awards.extend(result["results"])
                    # Check if there are more pages
                    has_more = len(result["results"]) == 100
                    page += 1
                    logger.info(f"Collected {len(all_awards)} awards so far...")
                else:
                    has_more = False
                    
            except Exception as e:
                logger.error(f"Error collecting awards on page {page}: {str(e)}")
                break
                
        return all_awards
    
    async def store_awards(self, awards: List[Dict]) -> None:
        """Store awards in database"""
        async with AsyncSessionLocal() as session:
            for award_data in awards:
                try:
                    # Check if award already exists
                    existing = await session.execute(
                        select(Award).where(Award.award_id == award_data.get("Award ID"))
                    )
                    existing = existing.scalar_one_or_none()
                    
                    if existing:
                        # Update existing award
                        existing.award_amount = float(award_data.get("Award Amount", 0))
                        existing.raw_data = award_data
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new award
                        award = Award(
                            award_id=award_data.get("Award ID"),
                            description=award_data.get("Description"),
                            award_amount=float(award_data.get("Award Amount", 0)),
                            recipient_name=award_data.get("Recipient Name"),
                            awarding_agency=award_data.get("Awarding Agency"),
                            funding_agency=award_data.get("Funding Agency"),
                            award_type=award_data.get("Award Type"),
                            start_date=datetime.strptime(award_data.get("Start Date", ""), "%Y-%m-%d") if award_data.get("Start Date") else None,
                            end_date=datetime.strptime(award_data.get("End Date", ""), "%Y-%m-%d") if award_data.get("End Date") else None,
                            recipient_state=award_data.get("recipient_state"),
                            raw_data=award_data
                        )
                        session.add(award)
                        
                except Exception as e:
                    logger.error(f"Error storing award {award_data.get('Award ID')}: {str(e)}")
                    continue
            
            try:
                await session.commit()
            except Exception as e:
                logger.error(f"Error committing awards to database: {str(e)}")
                await session.rollback()
    
    async def collect_and_store_all(self) -> None:
        """Collect and store data from all sources"""
        # Collect awards
        awards = await self.collect_recent_awards()
        if awards:
            await self.store_awards(awards)
            logger.info(f"Stored {len(awards)} awards in database")
        
        # Collect debt information
        try:
            debt_data = await self.treasury_client.get_debt_to_penny()
            if "error" not in debt_data:
                # TODO: Implement debt data storage
                logger.info("Successfully collected debt information")
        except Exception as e:
            logger.error(f"Error collecting debt information: {str(e)}")
        
        # Collect contractor information
        try:
            # Get unique DUNS numbers from recent awards
            duns_numbers = {award.get("recipient", {}).get("duns") for award in awards if award.get("recipient")}
            duns_numbers.discard(None)
            
            for duns in duns_numbers:
                try:
                    contractor_data = await self.sam_client.search_entities(duns=duns)
                    if contractor_data:
                        # TODO: Implement contractor data storage
                        logger.info(f"Successfully collected information for contractor {duns}")
                except Exception as e:
                    logger.error(f"Error collecting contractor information for {duns}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error processing contractor information: {str(e)}")

async def run_collector():
    """Run the data collector as a background task"""
    while True:
        try:
            collector = DataCollector()
            await collector.collect_and_store_all()
            logger.info("Completed data collection cycle")
            
            # Wait for next collection cycle (e.g., every hour)
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in data collection cycle: {str(e)}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying 
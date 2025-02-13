from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.db.session import AsyncSessionLocal
from app.models.awards import Award
from app.services.scrapers.usaspending import USSpendingClient
from app.services.scrapers.treasury import TreasuryClient, SAMClient
from app.core.logger import logger
from app.core.config import settings
from app.services.scrapers.fpds import FPDSClient
from app.services.scrapers.fbo import FBOClient
from app.services.scrapers.fsrs import FSRSClient
from app.services.scrapers.fred import FederalReserveClient
from app.services.scrapers.sec import SECClient
from app.models.government_data import (
    ContractOpportunity,
    Subaward,
    EconomicIndicator,
    CompanyFiling,
    CompanyFinancial
)

logger = logging.getLogger(__name__)

class DataCollector:
    """Service for collecting and storing data from multiple sources"""
    
    def __init__(self):
        self.usaspending_client = USSpendingClient()
        self.treasury_client = TreasuryClient()
        self.sam_client = SAMClient(settings.SAM_API_KEY)
        self.fpds_client = FPDSClient()
        self.fbo_client = FBOClient()
        self.fsrs_client = FSRSClient()
        self.fred_client = FederalReserveClient()
        self.sec_client = SECClient()
        self.db = AsyncSessionLocal()
        
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

    async def collect_contract_opportunities(self):
        """Collect contract opportunities from FBO"""
        try:
            opportunities = await self.fbo_client.get_contract_opportunities()
            for opp in opportunities:
                existing = await self.db.execute(
                    select(ContractOpportunity).where(ContractOpportunity.opportunity_id == opp["opportunity_id"])
                )
                existing = existing.scalar_one_or_none()
                
                if not existing:
                    opportunity = ContractOpportunity(
                        opportunity_id=opp["opportunity_id"],
                        title=opp["title"],
                        description=opp["description"],
                        agency=opp["agency"],
                        status=opp["status"],
                        posted_date=opp["posted_date"],
                        response_deadline=opp["response_deadline"],
                        estimated_value=opp["estimated_value"],
                        place_of_performance=opp["place_of_performance"],
                        naics_code=opp["naics_code"],
                        set_aside=opp["set_aside"],
                        raw_data=opp
                    )
                    await self.db.add(opportunity)
            
            await self.db.commit()
            logger.info(f"Collected {len(opportunities)} contract opportunities")
        except Exception as e:
            logger.error(f"Error collecting contract opportunities: {str(e)}")
            await self.db.rollback()

    async def collect_subawards(self):
        """Collect subaward data from FSRS"""
        try:
            subawards = await self.fsrs_client.get_subawards()
            for sub in subawards:
                existing = await self.db.execute(
                    select(Subaward).where(Subaward.subaward_id == sub["subaward_id"])
                )
                existing = existing.scalar_one_or_none()
                
                if not existing:
                    subaward = Subaward(
                        subaward_id=sub["subaward_id"],
                        prime_award_id=sub["prime_award_id"],
                        recipient_name=sub["recipient_name"],
                        recipient_address=sub["recipient_address"],
                        amount=sub["amount"],
                        description=sub["description"],
                        place_of_performance=sub["place_of_performance"],
                        period_of_performance_start=sub["period_of_performance_start"],
                        period_of_performance_end=sub["period_of_performance_end"],
                        raw_data=sub
                    )
                    await self.db.add(subaward)
            
            await self.db.commit()
            logger.info(f"Collected {len(subawards)} subawards")
        except Exception as e:
            logger.error(f"Error collecting subawards: {str(e)}")
            await self.db.rollback()

    async def collect_economic_indicators(self):
        """Collect economic indicators from FRED"""
        try:
            indicators = await self.fred_client.get_economic_data()
            for ind in indicators:
                existing = await self.db.execute(
                    select(EconomicIndicator).where(EconomicIndicator.series_id == ind["series_id"] and EconomicIndicator.date == ind["date"])
                )
                existing = existing.scalar_one_or_none()
                
                if not existing:
                    indicator = EconomicIndicator(
                        series_id=ind["series_id"],
                        date=ind["date"],
                        value=ind["value"],
                        indicator_type=ind["indicator_type"],
                        units=ind["units"],
                        seasonally_adjusted=ind["seasonally_adjusted"],
                        raw_data=ind
                    )
                    await self.db.add(indicator)
            
            await self.db.commit()
            logger.info(f"Collected {len(indicators)} economic indicators")
        except Exception as e:
            logger.error(f"Error collecting economic indicators: {str(e)}")
            await self.db.rollback()

    async def collect_company_filings(self):
        """Collect company filings from SEC EDGAR"""
        try:
            filings = await self.sec_client.get_company_filings()
            for filing in filings:
                existing = await self.db.execute(
                    select(CompanyFiling).where(CompanyFiling.cik == filing["cik"] and CompanyFiling.filing_type == filing["filing_type"] and CompanyFiling.filing_date == filing["filing_date"])
                )
                existing = existing.scalar_one_or_none()
                
                if not existing:
                    new_filing = CompanyFiling(
                        cik=filing["cik"],
                        company_name=filing["company_name"],
                        filing_type=filing["filing_type"],
                        filing_date=filing["filing_date"],
                        period_end_date=filing["period_end_date"],
                        fiscal_year=filing["fiscal_year"],
                        fiscal_period=filing["fiscal_period"],
                        raw_data=filing
                    )
                    await self.db.add(new_filing)
                    await self.db.flush()

                    # Add financial metrics
                    for metric in filing.get("financials", []):
                        financial = CompanyFinancial(
                            filing_id=new_filing.id,
                            metric_name=metric["name"],
                            value=metric["value"],
                            unit=metric["unit"],
                            start_date=metric["start_date"],
                            end_date=metric["end_date"],
                            raw_data=metric
                        )
                        await self.db.add(financial)
            
            await self.db.commit()
            logger.info(f"Collected {len(filings)} company filings")
        except Exception as e:
            logger.error(f"Error collecting company filings: {str(e)}")
            await self.db.rollback()

    async def collect_all(self):
        """Collect all data from various sources"""
        tasks = [
            self.collect_contract_opportunities(),
            self.collect_subawards(),
            self.collect_economic_indicators(),
            self.collect_company_filings()
        ]
        await asyncio.gather(*tasks)

async def run_collector():
    """Run the data collector as a background task"""
    while True:
        try:
            collector = DataCollector()
            await collector.collect_and_store_all()
            await collector.collect_all()
            logger.info("Completed data collection cycle")
            
            # Wait for next collection cycle (e.g., every hour)
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in data collection cycle: {str(e)}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying 

if __name__ == "__main__":
    asyncio.run(run_collector()) 
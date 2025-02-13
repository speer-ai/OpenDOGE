import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.services.scrapers.data_collector import DataCollector

async def main():
    collector = DataCollector()
    
    print("Collecting recent contract opportunities...")
    opportunities = await collector.collect_recent_opportunities(days_back=7)
    print(f"Found {len(opportunities)} opportunities")
    
    print("Storing opportunities in database...")
    await collector.store_opportunities(opportunities)
    
    # Extract unique DUNS numbers from opportunities
    duns_numbers = set()
    for opp in opportunities:
        if 'awardee' in opp and 'duns' in opp['awardee']:
            duns_numbers.add(opp['awardee']['duns'])
    
    if duns_numbers:
        print(f"Updating information for {len(duns_numbers)} contractors...")
        await collector.update_contractor_info(list(duns_numbers))
    
    print("Data collection complete!")

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
from app.services.scrapers.usaspending import USSpendingClient

async def demo_search_awards():
    """Demo the award search functionality"""
    client = USSpendingClient()
    
    # Search for recent awards from the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    time_period = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    print("\n=== Recent Contract Awards ===")
    results = await client.search_awards(
        time_period=time_period,
        award_type=["A", "B", "C", "D"],  # Contract award types
        limit=5  # Just get a few results for demo
    )
    
    if results and results.get("results"):
        for award in results["results"]:
            print("\nAward Details:")
            print(f"  Description: {award.get('Description', 'N/A')}")
            print(f"  Amount: ${award.get('Award Amount', 0):,.2f}")
            print(f"  Recipient: {award.get('Recipient Name', 'N/A')}")
            print(f"  Agency: {award.get('Awarding Agency', 'N/A')}")
            print(f"  Period: {award.get('Start Date', 'N/A')} to {award.get('End Date', 'N/A')}")
    else:
        print("No recent awards found")

async def demo_federal_accounts():
    """Demo the federal accounts functionality"""
    client = USSpendingClient()
    current_year = datetime.now().year
    
    print("\n=== Top Federal Accounts ===")
    results = await client.get_federal_accounts(
        fiscal_year=current_year,
        limit=5  # Just get a few results for demo
    )
    
    if results and results.get("data"):
        for account in results["data"]:
            print("\nAccount Details:")
            print(f"  Account Name: {account.get('account_name', 'N/A')}")
            print(f"  Agency: {account.get('agency_name', 'N/A')}")
            print(f"  Budgetary Resources: ${account.get('budgetary_resources', 0):,.2f}")
            print(f"  Managing Agency: {account.get('managing_agency', 'N/A')}")
    else:
        print("No federal accounts found")

async def demo_state_spending():
    """Demo the state spending functionality"""
    client = USSpendingClient()
    current_year = datetime.now().year
    
    print("\n=== California Spending Data ===")
    results = await client.get_state_data(
        state_code="CA",
        fiscal_year=current_year
    )
    
    if results and results.get("results"):
        for result in results["results"]:
            print("\nSpending Details:")
            print(f"  State: {result.get('shape_code', 'N/A')}")
            print(f"  Amount: ${result.get('aggregated_amount', 0):,.2f}")
            print(f"  Per Capita: ${result.get('per_capita', 0):,.2f}")
            if result.get('display_name'):
                print(f"  Region: {result['display_name']}")
    else:
        print("No state spending data found")

async def main():
    """Run all demos"""
    print("=== USAspending.gov API Demo ===")
    print("Fetching live data from USAspending.gov...")
    
    try:
        await demo_search_awards()
        await demo_federal_accounts()
        await demo_state_spending()
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 
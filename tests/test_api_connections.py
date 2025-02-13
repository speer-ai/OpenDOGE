import asyncio
import pytest
from datetime import datetime, timedelta

from app.services.scrapers.usaspending import USSpendingClient

@pytest.mark.asyncio
async def test_search_awards():
    """Test searching for recent awards"""
    client = USSpendingClient()
    
    # Search for awards from the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    time_period = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    results = await client.search_awards(
        time_period=time_period,
        award_type=["A", "B", "C", "D"],  # Contract award types
        limit=10
    )
    
    assert results is not None
    assert isinstance(results, dict)
    assert "results" in results
    print(f"\nFound {len(results['results'])} awards")
    if results["results"]:
        print("Sample award:", results["results"][0])

@pytest.mark.asyncio
async def test_get_federal_accounts():
    """Test retrieving federal account information"""
    client = USSpendingClient()
    current_year = datetime.now().year
    
    results = await client.get_federal_accounts(
        fiscal_year=current_year,
        limit=10
    )
    
    assert results is not None
    assert isinstance(results, dict)
    assert "data" in results
    assert isinstance(results["data"], list)
    print(f"\nFound {len(results['data'])} federal accounts")
    if results["data"]:
        print("Sample account:", results["data"][0])

@pytest.mark.asyncio
async def test_get_state_data():
    """Test retrieving state spending data"""
    client = USSpendingClient()
    current_year = datetime.now().year
    
    results = await client.get_state_data(
        state_code="CA",
        fiscal_year=current_year
    )
    
    assert results is not None
    assert isinstance(results, dict)
    assert "results" in results
    print("\nState spending data:", results)

if __name__ == "__main__":
    asyncio.run(test_search_awards())
    asyncio.run(test_get_federal_accounts())
    asyncio.run(test_get_state_data()) 
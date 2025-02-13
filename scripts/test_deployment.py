#!/usr/bin/env python3
import asyncio
import httpx
import sys
from datetime import datetime

async def test_endpoints():
    """Test all major endpoints of the application"""
    base_url = "http://localhost:8080"
    endpoints = {
        "health": "/health",
        "recent_awards": "/api/v1/usaspending/awards/recent",
        "federal_accounts": "/api/v1/usaspending/federal-accounts",
        "state_data": "/api/v1/usaspending/state/CA",
    }
    
    async with httpx.AsyncClient() as client:
        print("\n=== Testing OpenDOGE Endpoints ===")
        all_passed = True
        
        for name, endpoint in endpoints.items():
            try:
                print(f"\nTesting {name}...")
                response = await client.get(f"{base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"✅ {name}: Success (200 OK)")
                    # Print sample of response data
                    data = response.json()
                    print(f"Sample response: {str(data)[:200]}...")
                else:
                    print(f"❌ {name}: Failed ({response.status_code})")
                    print(f"Error: {response.text}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {name}: Error - {str(e)}")
                all_passed = False
        
        return all_passed

async def test_search():
    """Test the search functionality"""
    base_url = "http://localhost:8080"
    search_url = f"{base_url}/api/v1/usaspending/search"
    
    print("\n=== Testing Search Functionality ===")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test with a simple search term
            params = {
                "keyword": "construction",
                "days": 30,
                "limit": 5
            }
            
            print("\nTesting search with 'construction'...")
            response = await client.get(search_url, params=params)
            
            if response.status_code == 200:
                print("✅ Search: Success (200 OK)")
                data = response.json()
                if data.get("results"):
                    print(f"Found {len(data['results'])} results")
                    print("Sample result:", str(data["results"][0])[:200])
                else:
                    print("No results found")
                return True
            else:
                print(f"❌ Search: Failed ({response.status_code})")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Search: Error - {str(e)}")
            return False

async def main():
    print(f"Starting tests at {datetime.now()}")
    
    # Test basic endpoints
    endpoints_passed = await test_endpoints()
    
    # Test search functionality
    search_passed = await test_search()
    
    # Final results
    print("\n=== Test Results ===")
    print(f"Basic Endpoints: {'✅ Passed' if endpoints_passed else '❌ Failed'}")
    print(f"Search Functionality: {'✅ Passed' if search_passed else '❌ Failed'}")
    
    if not (endpoints_passed and search_passed):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
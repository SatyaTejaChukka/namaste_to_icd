"""
Test script to verify search API returns mappings
"""

import asyncio
import aiohttp
import json

async def test_search_api():
    """Test the search API to see if it returns ICD mappings"""
    
    # Test search queries
    test_queries = [
        "",  # Empty search to get some results
        "vata",  # Common Ayurveda term
        "san",   # Partial match
    ]
    
    from config import config
    
    async with aiohttp.ClientSession() as session:
        for query in test_queries:
            url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}/lookup?q={query}&limit=5"
            print(f"\n=== Testing query: '{query}' ===")
            print(f"URL: {url}")
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"Status: {response.status}")
                        print(f"Total concepts returned: {len(data.get('concepts', []))}")
                        
                        for i, concept in enumerate(data.get('concepts', [])[:3]):  # Show first 3
                            print(f"\nConcept {i+1}:")
                            print(f"  Code: {concept.get('code')}")
                            print(f"  Term: {concept.get('term')}")
                            print(f"  System: {concept.get('system')}")
                            print(f"  Native term: {concept.get('native_term', 'N/A')}")
                            
                            mappings = concept.get('icd_mappings', [])
                            print(f"  ICD Mappings: {len(mappings)}")
                            
                            for j, mapping in enumerate(mappings[:2]):  # Show first 2 mappings
                                print(f"    Mapping {j+1}:")
                                print(f"      ICD Code: {mapping.get('icd_code')}")
                                print(f"      ICD Title: {mapping.get('icd_title')}")
                                print(f"      Similarity: {mapping.get('similarity_score')}")
                    else:
                        print(f"Error: HTTP {response.status}")
                        error_text = await response.text()
                        print(f"Error response: {error_text}")
                        
            except Exception as e:
                print(f"Request failed: {e}")

# Test statistics API
async def test_statistics_api():
    """Test the statistics API"""
    from config import config
    
    print("\n" + "="*50)
    print("=== Testing Statistics API ===")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://{config.SERVER_HOST}:{config.SERVER_PORT}/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Status: {response.status}")
                    print(f"Total terms: {data.get('total_terms')}")
                    print(f"Total mappings: {data.get('total_mappings')}")
                    print(f"Total encounters: {data.get('total_encounters')}")
                    print("System distribution:")
                    for system, count in data.get('system_distribution', {}).items():
                        print(f"  {system}: {count}")
                else:
                    print(f"Error: HTTP {response.status}")
                    
        except Exception as e:
            print(f"Request failed: {e}")

async def main():
    await test_statistics_api()
    await test_search_api()

if __name__ == "__main__":
    asyncio.run(main())
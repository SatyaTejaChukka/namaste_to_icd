import requests
import json

# Test endpoints
import requests
import json
from config import config

# Configuration
base_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"

def test_endpoints():
    print("Testing AYUSH Terminology API Endpoints")
    print("="*50)
    
    # 1. Test validation endpoint
    print("\n1. Testing Validation Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/validate/ayurveda/AAE-001")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Test search endpoint  
    print("\n2. Testing Search Endpoint:")
    try:
        response = requests.get(f"{base_url}/lookup?q=sandhigata&system=ayurveda&limit=3")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Test mappings endpoint
    print("\n3. Testing Mappings Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/mappings/ayurveda?limit=3")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Test lookup endpoint for comparison
    print("\n4. Testing Lookup Endpoint:")
    try:
        response = requests.get(f"{base_url}/fhir/CodeSystem/$lookup?system=ayurveda&code=AAE-001")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
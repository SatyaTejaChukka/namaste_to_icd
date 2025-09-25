#!/usr/bin/env python3
"""
Test script for the translate_concept endpoint
"""

import requests
import json

def test_translate_endpoint():
    from config import config
    url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}/fhir/ConceptMap/$translate"
    
    # Test data in FHIR Parameters format
    test_data = {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "system",
                "valueUri": "http://ayush.namaste.gov.in/ayurveda"
            },
            {
                "name": "code", 
                "valueCode": "AAE-001"
            },
            {
                "name": "target",
                "valueUri": "http://id.who.int/icd/entity"
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Testing POST request to: {url}")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Parsed Response: {json.dumps(result, indent=2)}")
            except:
                print("Could not parse response as JSON")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error making request: {e}")
        return False

if __name__ == "__main__":
    success = test_translate_endpoint()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
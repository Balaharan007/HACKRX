#!/usr/bin/env python3
"""
Test script for HackRx 6.0 Document Intelligence Agent
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Test data
TEST_DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

TEST_QUESTIONS = [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?"
]

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=60)
        else:
            response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n{'='*50}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS")
            return result
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST FAILED: {str(e)}")
        return None

def main():
    print("🧪 HackRx 6.0 Document Intelligence Agent - Test Suite")
    print("="*60)
    
    # Test 1: Health check
    print("\n🔍 Test 1: Health Check")
    test_api_endpoint("/health")
    
    # Test 2: Root endpoint
    print("\n🔍 Test 2: Root Endpoint")
    test_api_endpoint("/")
    
    # Test 3: List documents (should be empty initially)
    print("\n🔍 Test 3: List Documents")
    test_api_endpoint("/documents")
    
    # Test 4: Upload document
    print("\n🔍 Test 4: Upload Document")
    upload_data = {
        "url": TEST_DOCUMENT_URL,
        "title": "Test Policy Document"
    }
    upload_result = test_api_endpoint("/documents/upload", "POST", upload_data)
    
    # Test 5: List documents again
    print("\n🔍 Test 5: List Documents (After Upload)")
    documents = test_api_endpoint("/documents")
    
    # Test 6: Query document
    print("\n🔍 Test 6: Query Document")
    if documents and len(documents) > 0:
        query_data = {
            "document_url": TEST_DOCUMENT_URL,
            "question": "What is the grace period for premium payment?"
        }
        test_api_endpoint("/query", "POST", query_data)
    
    # Test 7: Main HackRx endpoint
    print("\n🔍 Test 7: HackRx Main Endpoint")
    hackrx_data = {
        "documents": TEST_DOCUMENT_URL,
        "questions": TEST_QUESTIONS[:3]  # Test with first 3 questions
    }
    
    print("📝 Request Data:")
    print(json.dumps(hackrx_data, indent=2))
    
    start_time = time.time()
    result = test_api_endpoint("/hackrx/run", "POST", hackrx_data)
    end_time = time.time()
    
    if result:
        print(f"\n⏱️  Processing Time: {end_time - start_time:.2f} seconds")
        print("\n📋 Answers:")
        for i, answer in enumerate(result.get("answers", [])):
            print(f"\nQ{i+1}: {hackrx_data['questions'][i]}")
            print(f"A{i+1}: {answer[:200]}...")
    
    print("\n" + "="*60)
    print("🏁 Test Suite Complete!")

if __name__ == "__main__":
    main()

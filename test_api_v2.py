import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

def test_api():
    print("🧪 Testing HackRx 6.0 Document Intelligence Agent v2.0")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Health check
    print("\n✅ Test 1: Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: System stats
    print("\n📊 Test 2: System Stats")
    try:
        response = requests.get(f"{API_BASE_URL}/stats", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Stats: {response.json()}")
    except Exception as e:
        print(f"❌ Stats failed: {e}")
    
    # Test 3: HackRx endpoint with sample data
    print("\n🚀 Test 3: HackRx Endpoint")
    hackrx_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "Does this policy cover maternity expenses?"
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/hackrx/run", json=hackrx_data, headers=headers, timeout=120)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ HackRx endpoint working!")
            print(f"Answers received: {len(result.get('answers', []))}")
            for i, answer in enumerate(result.get('answers', [])[:2]):
                print(f"\nQ{i+1}: {hackrx_data['questions'][i]}")
                print(f"A{i+1}: {answer[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ HackRx test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    print("\n🌐 Access points:")
    print(f"- API Docs: {API_BASE_URL}/docs")
    print(f"- Health Check: {API_BASE_URL}/health")
    print(f"- HackRx Endpoint: {API_BASE_URL}/hackrx/run")
    print(f"- Streamlit UI: http://localhost:8501 (run streamlit_app_v2.py)")

if __name__ == "__main__":
    test_api()

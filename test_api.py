"""
Simple test script to verify API endpoints
Run this after starting the server with: python main.py
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_chat():
    """Test chat endpoint"""
    print("\n💬 Testing Chat Agent...")
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json={
            "message": "I want to visit Paris in December",
            "history": []
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_weather():
    """Test weather endpoint"""
    print("\n🌤️ Testing Weather...")
    response = requests.post(
        f"{API_BASE_URL}/api/weather",
        json={"city": "Paris"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_flights():
    """Test flight search endpoint"""
    print("\n✈️ Testing Flight Search...")
    response = requests.post(
        f"{API_BASE_URL}/api/flights/search",
        json={
            "from_city": "New York",
            "to_city": "Paris",
            "date": "2024-12-25",
            "passengers": 2
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_budget():
    """Test budget estimation endpoint"""
    print("\n💰 Testing Budget Estimation...")
    response = requests.post(
        f"{API_BASE_URL}/api/budget/estimate",
        json={
            "destination": "Paris",
            "days": 7,
            "budget_level": "Moderate"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_activities():
    """Test activities recommendation endpoint"""
    print("\n🎯 Testing Activities Recommendation...")
    response = requests.post(
        f"{API_BASE_URL}/api/activities/recommend",
        json={
            "destination": "Paris",
            "interests": ["museums", "food"]
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_currency():
    """Test currency conversion endpoint"""
    print("\n💱 Testing Currency Conversion...")
    response = requests.post(
        f"{API_BASE_URL}/api/currency/convert",
        json={
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "EUR"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 AI Travel Agent API Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running on http://localhost:8000")
    print("Start it with: python main.py")
    
    try:
        # Run all tests
        test_health()
        test_chat()
        test_weather()
        test_flights()
        test_budget()
        test_activities()
        test_currency()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
        print("Start it with: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

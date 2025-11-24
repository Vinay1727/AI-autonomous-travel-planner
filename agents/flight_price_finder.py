import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_flights(from_city, to_city, date, passengers=1):
    """
    Searches for flights using SerpApi (Google Flights engine).
    Returns a list of flight dictionaries.
    """
    if not SERPAPI_KEY:
        return {"error": "API Key missing", "flights": []}

    try:
        params = {
            "engine": "google_flights",
            "departure_id": from_city,
            "arrival_id": to_city,
            "outbound_date": date,
            "adults": passengers,
            "currency": "USD",
            "hl": "en",
            "api_key": SERPAPI_KEY
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"], "flights": []}
            
        flights = []
        # Parse best flights
        if "best_flights" in data:
            for f in data["best_flights"]:
                flights.append({
                    "airline": f["flights"][0]["airline"],
                    "price": f["price"],
                    "duration": f["total_duration"],
                    "departure": f["flights"][0]["departure_airport"]["time"],
                    "arrival": f["flights"][-1]["arrival_airport"]["time"],
                    "link": f.get("airline_logo"), # Placeholder for link if available
                    "type": "Best"
                })
                
        # Parse other flights
        if "other_flights" in data:
             for f in data["other_flights"][:5]: # Limit to 5
                flights.append({
                    "airline": f["flights"][0]["airline"],
                    "price": f["price"],
                    "duration": f["total_duration"],
                    "departure": f["flights"][0]["departure_airport"]["time"],
                    "arrival": f["flights"][-1]["arrival_airport"]["time"],
                    "type": "Other"
                })
                
        return {"flights": flights}

    except Exception as e:
        return {"error": str(e), "flights": []}

def get_mock_flights(from_city, to_city, date):
    """Returns mock flight data for fallback."""
    return [
        {
            "airline": "Mock Air",
            "price": 120,
            "duration": 180,
            "departure": f"{date} 08:00",
            "arrival": f"{date} 11:00",
            "type": "Best"
        },
        {
            "airline": "Demo Airlines",
            "price": 145,
            "duration": 170,
            "departure": f"{date} 14:00",
            "arrival": f"{date} 16:50",
            "type": "Other"
        }
    ]

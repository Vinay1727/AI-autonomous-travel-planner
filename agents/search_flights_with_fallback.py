from agents.flight_price_finder import search_flights, get_mock_flights
from agents.flight_price_link import get_google_flights_link, get_kayak_link

def search_flights_with_fallback(from_city, to_city, date, passengers=1):
    """
    Orchestrates flight search.
    1. Tries to fetch real-time data via API.
    2. If fails or empty, returns mock data + deep links.
    """
    result = search_flights(from_city, to_city, date, passengers)
    
    flights = result.get("flights", [])
    error = result.get("error")
    
    response = {
        "flights": flights,
        "links": {
            "google_flights": get_google_flights_link(from_city, to_city, date),
            "kayak": get_kayak_link(from_city, to_city, date)
        },
        "status": "success"
    }
    
    if error or not flights:
        response["status"] = "fallback"
        response["message"] = "Real-time data unavailable. Showing estimates and direct booking links."
        # Add mock data for UI demonstration if real data failed
        if not flights:
            response["flights"] = get_mock_flights(from_city, to_city, date)
            
    return response

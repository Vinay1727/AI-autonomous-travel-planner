import os
import requests
from dotenv import load_dotenv
from agents.hotel_finder import get_city_coords, fetch_place_details

load_dotenv()
# Use the same env var as hotel_finder for consistency
OPENTRIPMAP_KEY = os.getenv("OPENTRIP_API_KEY")

_DEFAULT_RESTAURANT_IMAGE = "https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg?auto=compress&cs=tinysrgb&w=400"

def get_cuisines(city, radius=5000, limit=10, cuisine_filter=None):
    """Fetch restaurants in a city with optional cuisine filter"""
    # If API key not available return mock restaurants so frontend shows something
    lat, lon = get_city_coords(city)
    if not lat:
        # mock list
        return [
            {"name": f"{city} Bistro", "description": "Cozy local bistro", "address": f"Center, {city}", "preview": {"source": _DEFAULT_RESTAURANT_IMAGE}},
            {"name": f"{city} Rooftop", "description": "Scenic views and cocktails", "address": f"Harbor Road, {city}", "preview": {"source": _DEFAULT_RESTAURANT_IMAGE}}
        ]

    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "kinds": "restaurants",
        "limit": limit,
        "apikey": OPENTRIPMAP_KEY
    }
    try:
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        results = []
        for place in res.json().get("features", []):
            xid = place.get("properties", {}).get("xid")
            details = fetch_place_details(xid)
            if details and not details.get("preview"):
                details["preview"] = {"source": _DEFAULT_RESTAURANT_IMAGE}
            if cuisine_filter:
                if cuisine_filter.lower() in (details.get("name", "") or "").lower():
                    results.append(details)
            else:
                results.append(details)
        return results
    except Exception:
        return []

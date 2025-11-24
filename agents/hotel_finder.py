import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
OPENTRIP_API_KEY = os.getenv("OPENTRIP_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

_DEFAULT_HOTEL_IMAGES = [
    "https://images.pexels.com/photos/261102/pexels-photo-261102.jpeg?auto=compress&cs=tinysrgb&w=400",
    "https://images.pexels.com/photos/271624/pexels-photo-271624.jpeg?auto=compress&cs=tinysrgb&w=400",
    "https://images.pexels.com/photos/164595/pexels-photo-164595.jpeg?auto=compress&cs=tinysrgb&w=400",
    "https://images.pexels.com/photos/189296/pexels-photo-189296.jpeg?auto=compress&cs=tinysrgb&w=400",
    "https://images.pexels.com/photos/271619/pexels-photo-271619.jpeg?auto=compress&cs=tinysrgb&w=400"
]

PLACEHOLDER_IMAGE = "https://via.placeholder.com/400x300?text=Hotel"

def get_fake_rating(name):
    """Generate consistent fake rating based on place name (3.8-4.7)"""
    return 3.8 + (hash(name) % 10) / 10

def get_fake_offers(name):
    """Generate consistent fake offer based on place name"""
    offers = [
        f"💰 10% off",
        f"🔥 Weekend Special Deal",
        f"📅 Book now & Save 15%",
        f"⭐ Free cancellation",
        f"🎁 Complimentary breakfast"
    ]
    return offers[hash(name) % len(offers)]

def fetch_image(query):
    """Fetch image URL using Pexels -> Unsplash -> Wikimedia -> Placeholder fallback"""
    
    # 1️⃣ Pexels
    if PEXELS_API_KEY:
        try:
            pexels_url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=1"
            headers = {"Authorization": PEXELS_API_KEY}
            res = requests.get(pexels_url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data.get("photos"):
                return data["photos"][0]["src"]["medium"]
        except Exception as e:
            print(f"Pexels error: {e}")

    # 2️⃣ Unsplash
    if UNSPLASH_ACCESS_KEY:
        try:
            unsplash_url = (
                f"https://api.unsplash.com/search/photos?"
                f"query={quote(query)}&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
            )
            res = requests.get(unsplash_url, timeout=10)
            res.raise_for_status()
            data = res.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
        except Exception as e:
            print(f"Unsplash error: {e}")

    # 3️⃣ Wikimedia Commons
    try:
        wiki_url = (
            f"https://commons.wikimedia.org/w/api.php"
            f"?action=query&format=json&prop=imageinfo&generator=search"
            f"&gsrsearch={quote(query)}&iiprop=url&gsrlimit=1"
        )
        res = requests.get(wiki_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                return imageinfo[0]["url"]
    except Exception as e:
        print(f"Wikimedia error: {e}")

    # 4️⃣ Default image based on name hash
    return _DEFAULT_HOTEL_IMAGES[hash(query) % len(_DEFAULT_HOTEL_IMAGES)]

def get_city_coords(city):
    """Get latitude and longitude of a city"""
    if not OPENTRIP_API_KEY:
        return None, None

    url = "https://api.opentripmap.com/0.1/en/places/geoname"
    params = {"name": city, "apikey": OPENTRIP_API_KEY}
    try:
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        data = res.json()
        return data.get("lat"), data.get("lon")
    except Exception:
        return None, None

def fetch_place_details(xid):
    """Get detailed info about a place"""
    if not OPENTRIP_API_KEY or not xid:
        return {}

    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
    params = {"apikey": OPENTRIP_API_KEY}
    try:
        res = requests.get(url, params=params, timeout=8)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {}

def get_places(city, kinds, radius=10000, limit=8):
    """Generic function to get places by kinds"""
    try:
        lat, lon = get_city_coords(city)
        if not lat:
            return []

        url = "https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "kinds": kinds,
            "format": "json",
            "limit": limit,
            "apikey": OPENTRIP_API_KEY
        }
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            return []
        
        places_data = res.json()
        return places_data if isinstance(places_data, list) else []
    except Exception as e:
        print(f"Error in get_places: {e}")
        return []

def search_hotels(city, radius=10000, limit=10):
    """Search hotels & resorts in a city using flexible kinds parameter (like Streamlit)"""
    
    # If API key not configured, return enriched mock dataset
    if not OPENTRIP_API_KEY:
        mock_hotels = [
            {
                "name": f"{city} Grand Hotel",
                "address": f"Central area, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[0],
                "rating": 4.5,
                "offer": "💰 10% off",
                "description": f"Experience luxury accommodation in the heart of {city}. Perfect for business and leisure travelers.",
                "xid": "mock1"
            },
            {
                "name": f"{city} Boutique Stay",
                "address": f"Old Town, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[1],
                "rating": 4.2,
                "offer": "🎁 Complimentary breakfast",
                "description": f"A charming boutique hotel offering personalized service and unique design.",
                "xid": "mock2"
            },
            {
                "name": f"{city} Plaza Hotel",
                "address": f"Downtown, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[2],
                "rating": 4.6,
                "offer": "📅 Book now & Save 15%",
                "description": f"Modern hotel with excellent amenities and central location.",
                "xid": "mock3"
            }
        ]
        return mock_hotels

    # Try multiple kinds parameters until we get results (LIKE STREAMLIT)
    kinds_list = ["accomodations", "hotels", "accommodation", "lodging", "other_hotels"]
    
    places = []
    for kinds in kinds_list:
        places = get_places(city, kinds, radius, limit)
        if places:
            break  # Found results, stop trying
    
    # If still no results, return mock data as fallback
    if not places:
        print(f"No hotels found via API for {city}, returning mock data")
        mock_hotels = [
            {
                "name": f"{city} Grand Hotel",
                "address": f"Central area, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[0],
                "rating": 4.5,
                "offer": "💰 10% off",
                "description": f"Experience luxury accommodation in the heart of {city}. Perfect for business and leisure travelers.",
                "xid": "mock1",
                "point": {"lat": 0, "lon": 0},
                "preview": {"source": _DEFAULT_HOTEL_IMAGES[0]},
                "rate": "4.5"
            },
            {
                "name": f"{city} Boutique Stay",
                "address": f"Old Town, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[1],
                "rating": 4.2,
                "offer": "🎁 Complimentary breakfast",
                "description": f"A charming boutique hotel offering personalized service and unique design.",
                "xid": "mock2",
                "point": {"lat": 0, "lon": 0},
                "preview": {"source": _DEFAULT_HOTEL_IMAGES[1]},
                "rate": "4.2"
            },
            {
                "name": f"{city} Plaza Hotel",
                "address": f"Downtown, {city}",
                "image_url": _DEFAULT_HOTEL_IMAGES[2],
                "rating": 4.6,
                "offer": "📅 Book now & Save 15%",
                "description": f"Modern hotel with excellent amenities and central location.",
                "xid": "mock3",
                "point": {"lat": 0, "lon": 0},
                "preview": {"source": _DEFAULT_HOTEL_IMAGES[2]},
                "rate": "4.6"
            }
        ]
        return mock_hotels

    # Enrich each place with details
    enriched_hotels = []
    for place in places:
        try:
            name = place.get("name", "")
            # Filter out invalid places (LIKE STREAMLIT)
            if not name or name.startswith("Unknown"):
                continue
            
            xid = place.get("xid")
            details = fetch_place_details(xid) if xid else {}
            
            # Get description from Wikipedia extracts
            description = details.get("wikipedia_extracts", {}).get("text", "") or \
                         f"Experience the best accommodation at {name}."
            
            # Limit description to 3 lines (approx 120 chars)
            if len(description) > 120:
                description = description[:117] + "..."
            
            # Generate image URL
            search_query = f"{name} hotel"
            image_url = fetch_image(search_query)
            
            # Build enriched hotel object
            hotel = {
                "name": name,
                "address": place.get("address") or details.get("address") or f"{city}",
                "image_url": image_url,
                "rating": get_fake_rating(name),
                "offer": get_fake_offers(name),
                "description": description,
                "xid": xid,
                "point": place.get("point", {}),
                # Keep backward compatibility
                "preview": {"source": image_url},
                "rate": str(get_fake_rating(name))
            }
            
            enriched_hotels.append(hotel)
            
        except Exception as e:
            print(f"Error enriching hotel: {e}")
            continue
    
    return enriched_hotels

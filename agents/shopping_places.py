"""
Shopping Places Finder Agent - AI Trip Planner
Uses Geoapify API to find nearby shopping places including malls, local markets, and retail areas
"""

import requests
import json
from typing import List, Dict, Optional, Tuple
try:
    import streamlit as st
except Exception:
    # Minimal shim so this module can run in non-streamlit environments (API servers)
    class _StreamlitShim:
        @staticmethod
        def error(msg):
            print("[streamlit.error]", msg)

    st = _StreamlitShim()
from geopy.distance import geodesic
import time
import os 
from dotenv import load_dotenv
load_dotenv()

# Load Geoapify API key from environment variable

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


class ShoppingPlacesFinder:
    def __init__(self, api_key: str):
        """
        Initialize the Shopping Places Finder with Geoapify API key
        
        Args:
            api_key (str): Your Geoapify API key
        """
        self.api_key = api_key
        self.base_url = "https://api.geoapify.com/v2/places"
        self.geocode_url = "https://api.geoapify.com/v1/geocode/search"
        
        # Famous local markets database for priority ranking
        self.famous_markets = {
            "delhi": [
                "chandni chowk", "karol bagh", "sarojini nagar", "lajpat nagar",
                "janpath", "palika bazaar", "connaught place", "khan market"
            ],
            "mumbai": [
                "colaba causeway", "linking road", "hill road", "crawford market",
                "chor bazaar", "zaveri bazaar", "palladium mall"
            ],
            "bangalore": [
                "commercial street", "brigade road", "chickpet", "malleswaram"
            ],
            "kolkata": [
                "new market", "gariahat", "shyama charan", "hatibagan"
            ]
        }

    # ------------------ IMAGE FETCHER ------------------
    def get_place_image(self, place_name: str) -> str:
        """
        Fetch an image for the given place using fallback system:
        Geoapify → Unsplash API → Unsplash random → Pexels → Wikimedia → Default
        """
        # 1. Geoapify Place Image
        try:
            url = f"https://api.geoapify.com/v1/place-details?name={place_name}&apiKey={self.api_key}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    if "image" in props:
                        return props["image"]
        except:
            pass

        # 2. Unsplash API (if access key is set)
        if UNSPLASH_ACCESS_KEY:
            try:
                unsplash_url = f"https://api.unsplash.com/search/photos?query={place_name} shopping&per_page=1&client_id={UNSPLASH_ACCESS_KEY}"
                res = requests.get(unsplash_url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("results"):
                        return data["results"][0]["urls"]["regular"]
            except:
                pass

        # 3. Unsplash (random image, no API key needed)
        try:
            return f"https://source.unsplash.com/400x300/?shopping,{place_name}"
        except:
            pass

        # 4. Pexels API
        if PEXELS_API_KEY:
            try:
                headers = {"Authorization": PEXELS_API_KEY}
                url = f"https://api.pexels.com/v1/search?query={place_name} shopping&per_page=1"
                res = requests.get(url, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("photos"):
                        return data["photos"][0]["src"]["medium"]
            except:
                pass

        # 5. Wikimedia Commons
        try:
            url = (
                "https://commons.wikimedia.org/w/api.php?"
                f"action=query&generator=search&gsrsearch={place_name}&gsrlimit=1&"
                "prop=imageinfo&iiprop=url&format=json"
            )
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                pages = data.get("query", {}).get("pages", {})
                if pages:
                    return list(pages.values())[0]["imageinfo"][0]["url"]
        except:
            pass

        # 6. Fallback
        return "https://source.unsplash.com/400x300/?shopping"

    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Convert location name to coordinates using Geoapify Geocoding API
        
        Args:
            location (str): Location name (e.g., "Karol Bagh, Delhi")
            
        Returns:
            Tuple[float, float]: (latitude, longitude) or None if failed
        """
        try:
            params = {
                "text": location,
                "apiKey": self.api_key,
                "limit": 1
            }
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("features") and len(data["features"]) > 0:
                coordinates = data["features"][0]["geometry"]["coordinates"]
                # Geoapify returns [longitude, latitude]
                return coordinates[1], coordinates[0]  # Return as (lat, lng)
            
            return None
            
        except Exception as e:
            st.error(f"Geocoding failed: {str(e)}")
            return None

    def find_shopping_places(
        self, 
        location: str = None, 
        coordinates: Tuple[float, float] = None,
        radius_km: int = 5,
        limit: int = 30
    ) -> Dict[str, List[Dict]]:
        """
        Find shopping places near a location using Geoapify Places API
        
        Args:
            location (str): Location name to search around
            coordinates (Tuple[float, float]): (lat, lng) coordinates
            radius_km (int): Search radius in kilometers
            limit (int): Maximum number of results
            
        Returns:
            Dict[str, List[Dict]]: Categorized shopping places
        """
        try:
            # Get coordinates if not provided
            if coordinates is None and location:
                coordinates = self.geocode_location(location)
                if coordinates is None:
                    return {"error": "Could not find location coordinates"}
            
            if coordinates is None:
                return {"error": "No valid location provided"}
            
            lat, lng = coordinates
            radius_meters = radius_km * 1000
            
            # Define shopping categories for Geoapify - CORRECTED FORMAT
            shopping_categories = [
                "commercial.shopping_mall",
                "commercial.marketplace", 
                "commercial.supermarket",
                "commercial.department_store",
                "commercial"  # General commercial category as fallback
            ]
            
            # FIXED: Proper parameter formatting
            params = {
                "categories": ",".join(shopping_categories),
                "filter": f"circle:{lng},{lat},{radius_meters}",
                "bias": f"proximity:{lng},{lat}",
                "limit": min(limit, 100),  # Geoapify limits to 100 per request
                "apiKey": self.api_key
            }
            
            # Debug: Print the actual URL being called
            print(f"API URL: {self.base_url}")
            print(f"Parameters: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=15)
            
            # Better error handling
            if response.status_code == 400:
                error_details = response.text
                print(f"400 Error details: {error_details}")
                return {"error": f"Bad request: {error_details}"}
            elif response.status_code == 401:
                return {"error": "Invalid API key"}
            elif response.status_code == 403:
                return {"error": "API key exceeded quota or lacks permissions"}
            
            response.raise_for_status()
            
            data = response.json()
            
            # Process and categorize results
            return self._process_shopping_results(data, (lat, lng), location)
            
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def _process_shopping_results(
        self, 
        api_data: Dict, 
        user_location: Tuple[float, float],
        search_location: str = None
    ) -> Dict[str, List[Dict]]:
        """
        Process and categorize Geoapify API results
        
        Args:
            api_data (Dict): Raw API response
            user_location (Tuple[float, float]): User's coordinates
            search_location (str): Original search location
            
        Returns:
            Dict[str, List[Dict]]: Categorized and processed results
        """
        categorized_places = {
            "shopping_malls": [],
            "local_markets": [],
            "retail_areas": [],
            "supermarkets": [],
            "all_places": []
        }
        
        if not api_data.get("features"):
            return categorized_places
        
        # Get city name for local market detection
        city = self._extract_city_name(search_location) if search_location else ""
        
        for feature in api_data["features"]:
            try:
                place_info = self._extract_place_info(feature, user_location, city)
                if place_info:
                    # Categorize the place
                    category = self._categorize_place(place_info)
                    categorized_places[category].append(place_info)
                    categorized_places["all_places"].append(place_info)
                    
            except Exception as e:
                continue  # Skip problematic entries
        
        # Sort each category by distance and local importance
        for category in categorized_places:
            if category != "all_places":
                categorized_places[category] = self._sort_places(
                    categorized_places[category], city
                )
        
        return categorized_places

    def _extract_place_info(
        self, 
        feature: Dict, 
        user_location: Tuple[float, float],
        city: str
    ) -> Optional[Dict]:
        """
        Extract relevant information from a place feature
        
        Args:
            feature (Dict): Geoapify place feature
            user_location (Tuple[float, float]): User coordinates
            city (str): City name
            
        Returns:
            Dict: Processed place information
        """
        try:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            
            # Extract coordinates
            coords = geometry.get("coordinates", [])
            if len(coords) < 2:
                return None
            
            place_location = (coords[1], coords[0])  # Convert to (lat, lng)
            
            # Calculate distance
            distance_km = round(geodesic(user_location, place_location).kilometers, 2)
            
            # Extract place information
            place_info = {
                "name": properties.get("name", "Unknown Place"),
                "address": properties.get("formatted", "Address not available"),
                "category": properties.get("categories", []),
                "distance_km": distance_km,
                "coordinates": place_location,
                "place_id": properties.get("place_id"),
                "opening_hours": properties.get("opening_hours"),
                "contact": {
                    "phone": properties.get("contact", {}).get("phone") if properties.get("contact") else None,
                    "website": properties.get("contact", {}).get("website") if properties.get("contact") else None
                },
                "rating": properties.get("rating"),
                "is_famous_local": self._is_famous_local_market(
                    properties.get("name", ""), city
                )
            }
            
            return place_info
            
        except Exception as e:
            return None

    def _categorize_place(self, place_info: Dict) -> str:
        """
        Categorize a shopping place based on its properties
        
        Args:
            place_info (Dict): Place information
            
        Returns:
            str: Category name
        """
        categories = place_info.get("category", [])
        name = place_info.get("name", "").lower()
        
        # Check for malls
        if any("shopping_mall" in cat or "department_store" in cat for cat in categories):
            return "shopping_malls"
        
        # Check for supermarkets
        if any("supermarket" in cat for cat in categories):
            return "supermarkets"
        
        # Check for local/traditional markets
        if (any("marketplace" in cat for cat in categories) or 
            place_info.get("is_famous_local", False) or
            any(word in name for word in ["market", "bazaar", "chowk", "nagar"])):
            return "local_markets"
        
        # Default to retail areas
        return "retail_areas"

    def _is_famous_local_market(self, place_name: str, city: str) -> bool:
        """
        Check if a place is a famous local market
        
        Args:
            place_name (str): Name of the place
            city (str): City name
            
        Returns:
            bool: True if it's a famous local market
        """
        if not city or not place_name:
            return False
        
        city_lower = city.lower()
        place_lower = place_name.lower()
        
        famous_markets = self.famous_markets.get(city_lower, [])
        
        return any(market in place_lower for market in famous_markets)

    def _extract_city_name(self, location: str) -> str:
        """
        Extract city name from location string
        
        Args:
            location (str): Location string
            
        Returns:
            str: City name
        """
        if not location:
            return ""
        
        # Common patterns: "Area, City" or just "City"
        parts = location.split(",")
        if len(parts) >= 2:
            return parts[-1].strip().lower()
        return parts[0].strip().lower()

    def _sort_places(self, places: List[Dict], city: str) -> List[Dict]:
        """
        Sort places by importance (famous local markets first) then by distance
        
        Args:
            places (List[Dict]): List of places
            city (str): City name
            
        Returns:
            List[Dict]: Sorted places
        """
        def sort_key(place):
            # Famous local markets get priority (lower number = higher priority)
            fame_score = 0 if place.get("is_famous_local", False) else 1
            distance = place.get("distance_km", 999)
            return (fame_score, distance)
        
        return sorted(places, key=sort_key)

    def get_shopping_summary(self, results: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Get a summary of found shopping places
        
        Args:
            results (Dict): Categorized shopping results
            
        Returns:
            Dict[str, int]: Summary counts
        """
        return {
            "total_places": len(results.get("all_places", [])),
            "shopping_malls": len(results.get("shopping_malls", [])),
            "local_markets": len(results.get("local_markets", [])),
            "retail_areas": len(results.get("retail_areas", [])),
            "supermarkets": len(results.get("supermarkets", []))
        }

    def format_place_for_display(self, place: Dict) -> str:
        """
        Format a place for display in Streamlit
        
        Args:
            place (Dict): Place information
            
        Returns:
            str: Formatted place string
        """
        name = place.get("name", "Unknown")
        distance = place.get("distance_km", 0)
        address = place.get("address", "")
        
        # Truncate long addresses
        if len(address) > 50:
            address = address[:47] + "..."
        
        famous_indicator = " ⭐" if place.get("is_famous_local", False) else ""
        
        return f"**{name}**{famous_indicator}\n📍 {address}\n🚶 {distance} km away"


# Test function to validate API connectivity
def test_api_connection():
    """
    Test function to validate API key and connection
    """
    API_KEY = os.getenv("GEOAPIFY_API_KEY")
    
    if not API_KEY:
        print("❌ GEOAPIFY_API_KEY not found in environment variables")
        return False
    
    # Test geocoding first
    geocode_url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": "Delhi, India",
        "apiKey": API_KEY,
        "limit": 1
    }
    
    try:
        response = requests.get(geocode_url, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ API key is valid and working")
            return True
        elif response.status_code == 401:
            print("❌ Invalid API key")
        elif response.status_code == 403:
            print("❌ API key exceeded quota or lacks permissions")
        else:
            print(f"❌ API returned status code: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


# Usage example and testing function
def test_shopping_finder():
    """
    Test function for the Shopping Places Finder
    """
    # Test API connection first
    if not test_api_connection():
        return
    
    # Replace with your actual Geoapify API key
    API_KEY = os.getenv("GEOAPIFY_API_KEY")
    
    finder = ShoppingPlacesFinder(API_KEY)
    
    # Test with Delhi location
    results = finder.find_shopping_places(
        location="Karol Bagh, Delhi",
        radius_km=3,
        limit=20
    )
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    # Print summary
    summary = finder.get_shopping_summary(results)
    print("Shopping Places Summary:")
    for category, count in summary.items():
        print(f"  {category}: {count}")
    
    # Print some results
    print("\nLocal Markets found:")
    for place in results.get("local_markets", [])[:3]:
        print(f"- {place['name']} ({place['distance_km']} km)")


if __name__ == "__main__":
    test_shopping_finder()
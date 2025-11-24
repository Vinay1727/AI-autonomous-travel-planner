import urllib.parse

def get_google_flights_link(from_city, to_city, date):
    """Generates a Google Flights search URL."""
    base_url = "https://www.google.com/travel/flights"
    query = f"flights from {from_city} to {to_city} on {date}"
    encoded_query = urllib.parse.quote(query)
    return f"{base_url}?q={encoded_query}"

def get_skyscanner_link(from_city, to_city, date):
    """Generates a Skyscanner search URL (generic)."""
    # Skyscanner URLs are complex and require IATA codes. 
    # This is a simplified search link.
    base_url = "https://www.skyscanner.com/transport/flights"
    # Format: /from/to/date
    # Assuming inputs are city names, this might not work perfectly without IATA resolution.
    # Fallback to a search query style if possible, or just return homepage with query params if supported.
    # For now, returning a generic search link.
    return f"https://www.skyscanner.com/"

def get_kayak_link(from_city, to_city, date):
    """Generates a Kayak search URL."""
    return f"https://www.kayak.com/flights/{from_city}-{to_city}/{date}"

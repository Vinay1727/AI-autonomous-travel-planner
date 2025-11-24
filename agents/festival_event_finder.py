# agents/festival_event_finder.py
import requests
import os
from datetime import datetime, timedelta

EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")
TICKETMASTER_KEY = os.getenv("TICKETMASTER_KEY")

def fetch_eventbrite_events(location="India", days_ahead=7, keyword="festival"):
    url = "https://www.eventbriteapi.com/v3/events/search/"
    headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
    
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=days_ahead)
    
    params = {
        "q": keyword,
        "location.address": location,
        "start_date.range_start": start_date.isoformat(),
        "start_date.range_end": end_date.isoformat(),
        "sort_by": "date",
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        events = response.json().get("events", [])
        return [{
            "name": e["name"]["text"],
            "start": e["start"]["local"],
            "url": e["url"],
            "source": "Eventbrite"
        } for e in events]
    return []

def fetch_ticketmaster_events(location="India", days_ahead=7, keyword="festival"):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    
    start_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    params = {
        "apikey": TICKETMASTER_KEY,
        "keyword": keyword,
        "locale": "*",
        "startDateTime": start_date,
        "endDateTime": end_date,
        "city": location
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        events = response.json().get("_embedded", {}).get("events", [])
        return [{
            "name": e["name"],
            "start": e["dates"]["start"]["dateTime"],
            "url": e["url"],
            "source": "Ticketmaster"
        } for e in events]
    return []

def fetch_festivals_and_events(location="India", days_ahead=7, keyword="festival"):
    """
    Combine Eventbrite + Ticketmaster events with smart fallback
    """
    # Try city first
    events = fetch_eventbrite_events(location, days_ahead, keyword)
    events += fetch_ticketmaster_events(location, days_ahead, keyword)
    
    # If no events, fallback to country-level search
    if not events:
        fallback_country = location.split(",")[-1].strip()  # e.g., "Berlin, Germany" -> "Germany"
        if fallback_country != location:
            events = fetch_eventbrite_events(fallback_country, days_ahead, keyword)
            events += fetch_ticketmaster_events(fallback_country, days_ahead, keyword)
    
    # Sort events by start date
    return sorted(events, key=lambda x: x["start"])

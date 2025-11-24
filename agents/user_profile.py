import streamlit as st
from datetime import datetime

def initialize_user_profile():
    """Initialize user profile in session state if not exists."""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            "name": "Traveler",
            "home_city": "New York",
            "budget_level": "Moderate",
            "travel_style": "Balanced",
            "languages": ["English"],
            "trips": [],  # List of past trips
            "saved_itineraries": [],
            "recent_searches": []
        }

def get_user_profile():
    initialize_user_profile()
    return st.session_state.user_profile

def update_user_profile(key, value):
    initialize_user_profile()
    st.session_state.user_profile[key] = value

def add_trip_to_history(destination, start_date, end_date, summary):
    initialize_user_profile()
    trip = {
        "destination": destination,
        "dates": f"{start_date} - {end_date}",
        "summary": summary,
        "added_on": datetime.now().strftime("%Y-%m-%d")
    }
    st.session_state.user_profile['trips'].append(trip)

def add_recent_search(from_city, to_city, date):
    initialize_user_profile()
    search = f"{from_city} -> {to_city} on {date}"
    if search not in st.session_state.user_profile['recent_searches']:
        st.session_state.user_profile['recent_searches'].insert(0, search)
        # Keep only last 5
        st.session_state.user_profile['recent_searches'] = st.session_state.user_profile['recent_searches'][:5]

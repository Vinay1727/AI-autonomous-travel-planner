def get_useful_links():
    """Returns a dictionary of useful travel links categories."""
    return {
        "Flight Booking": [
            {"name": "Google Flights", "url": "https://www.google.com/travel/flights"},
            {"name": "Skyscanner", "url": "https://www.skyscanner.com/"},
            {"name": "Kayak", "url": "https://www.kayak.com/"}
        ],
        "Accommodation": [
            {"name": "Booking.com", "url": "https://www.booking.com/"},
            {"name": "Airbnb", "url": "https://www.airbnb.com/"},
            {"name": "Agoda", "url": "https://www.agoda.com/"}
        ],
        "Navigation & Maps": [
            {"name": "Google Maps", "url": "https://www.google.com/maps"},
            {"name": "Rome2rio", "url": "https://www.rome2rio.com/"}
        ],
        "Safety & Visas": [
            {"name": "US State Dept Travel", "url": "https://travel.state.gov/"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/"},
            {"name": "CDC Travel Health", "url": "https://wwwnc.cdc.gov/travel"}
        ]
    }

def get_activities_and_food(destination):
    """
    Returns recommended activities and food for a destination.
    Uses a simple mock database for demonstration.
    """
    # Mock Database
    data = {
        "Paris": {
            "activities": ["Eiffel Tower Visit", "Louvre Museum Tour", "Seine River Cruise", "Montmartre Walk"],
            "food": ["Croissants at Du Pain et des Idees", "Macarons at Ladurée", "Steak Frites in a Bistro"]
        },
        "Tokyo": {
            "activities": ["Shibuya Crossing", "Senso-ji Temple", "TeamLab Planets", "Akihabara Shopping"],
            "food": ["Sushi at Tsukiji Market", "Ramen at Ichiran", "Tempura in Ginza"]
        },
        "New York": {
            "activities": ["Statue of Liberty", "Central Park Stroll", "Broadway Show", "Empire State Building"],
            "food": ["NY Style Pizza", "Bagels with Lox", "Cheesecake at Junior's"]
        },
        "London": {
            "activities": ["British Museum", "Tower of London", "London Eye", "Buckingham Palace"],
            "food": ["Fish and Chips", "Afternoon Tea", "Full English Breakfast"]
        }
    }
    
    # Default generic response if city not found
    default = {
        "activities": [f"Explore {destination} City Center", "Visit Local Museums", "Walking Tour", "Shopping at Local Markets"],
        "food": ["Try Local Street Food", "Visit Top Rated Restaurants", "Coffee at Popular Cafes"]
    }
    
    # Simple fuzzy match or direct lookup
    for city, info in data.items():
        if city.lower() in destination.lower():
            return info
            
    return default
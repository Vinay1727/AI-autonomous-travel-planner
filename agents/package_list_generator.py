def generate_packages(destination):
    """
    Generates travel packages for a destination.
    """
    return [
        {
            "title": f"Weekend in {destination}",
            "duration": "3 Days / 2 Nights",
            "price": "$499",
            "highlights": ["City Tour", "4-Star Hotel", "Airport Transfer"],
            "rating": "4.5/5"
        },
        {
            "title": f"{destination} Explorer",
            "duration": "5 Days / 4 Nights",
            "price": "$899",
            "highlights": ["All Main Attractions", "Daily Breakfast", "Guided Tours"],
            "rating": "4.8/5"
        },
        {
            "title": f"Luxury {destination} Experience",
            "duration": "7 Days / 6 Nights",
            "price": "$1,999",
            "highlights": ["5-Star Accommodation", "Private Chauffeur", "Fine Dining"],
            "rating": "5.0/5"
        }
    ]

def estimate_budget(destination, days, style="Moderate", travelers=1):
    """
    Estimates budget based on heuristics.
    Styles: Budget, Moderate, Luxury
    """
    # Base daily costs (USD)
    base_costs = {
        "Budget": 50,
        "Moderate": 150,
        "Luxury": 400
    }
    
    # Destination multipliers (simplified)
    multipliers = {
        "Paris": 1.5,
        "London": 1.5,
        "New York": 1.8,
        "Tokyo": 1.4,
        "Bangkok": 0.6,
        "Bali": 0.7
    }
    
    daily_cost = base_costs.get(style, 150)
    multiplier = multipliers.get(destination, 1.0) # Default to 1.0 if unknown
    
    total_cost = daily_cost * multiplier * days * travelers
    
    return {
        "total_estimated": round(total_cost, 2),
        "breakdown": {
            "accommodation": round(total_cost * 0.4, 2),
            "food": round(total_cost * 0.25, 2),
            "activities": round(total_cost * 0.2, 2),
            "transport": round(total_cost * 0.15, 2)
        },
        "currency": "USD"
    }

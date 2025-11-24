import requests

def get_weather(city):
    """
    Fetches weather data for a given city using Open-Meteo API.
    Returns a dictionary with current weather and forecast summary.
    """
    try:
        # 1. Geocoding to get lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return {"error": "City not found"}
            
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        country = location.get("country", "")
        
        # 2. Fetch Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
        weather_res = requests.get(weather_url).json()
        
        current = weather_res.get("current", {})
        daily = weather_res.get("daily", {})
        
        # Map WMO codes to icons/text (simplified)
        # https://open-meteo.com/en/docs
        def get_icon(code):
            if code == 0: return "☀️ Clear"
            if code in [1, 2, 3]: return "bq Partly Cloudy"
            if code in [45, 48]: return "🌫️ Foggy"
            if code in [51, 53, 55]: return "🌧️ Drizzle"
            if code in [61, 63, 65]: return "🌧️ Rain"
            if code in [71, 73, 75]: return "❄️ Snow"
            if code in [95, 96, 99]: return "⛈️ Thunderstorm"
            return "☁️ Cloudy"

        return {
            "location": f"{name}, {country}",
            "current_temp": current.get("temperature_2m"),
            "current_condition": get_icon(current.get("weather_code")),
            "wind_speed": current.get("wind_speed_10m"),
            "forecast": [
                {
                    "day": i,
                    "max": daily["temperature_2m_max"][i],
                    "min": daily["temperature_2m_min"][i],
                    "condition": get_icon(daily["weather_code"][i])
                }
                for i in range(min(5, len(daily.get("time", []))))
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}

# agents/nearby_attractions/attractions_finder.py

import requests

def get_attractions(destination):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{destination}"
        res = requests.get(url).json()
        summary = res.get("extract", "No information found.")
        return {
            "success": True,
            "attractions": summary   # ⬅ ONLY clean string
        }
    except Exception as e:
        return {
            "success": False,
            "attractions": f"Failed to fetch attractions: {e}"
        }

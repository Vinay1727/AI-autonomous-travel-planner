"""
AI Travel Agent - Main API Router
FastAPI backend to connect all agents with frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn

# Import all agents
from agents.chat_agent import get_chat_response
from agents.flight_price_finder import search_flights, get_mock_flights
from agents.flight_price_link import get_google_flights_link, get_skyscanner_link, get_kayak_link
from agents.weather import get_weather
from agents.budget_estimator import estimate_budget
from agents.currency_converter import convert_currency
from agents.recommend_activities import get_activities_and_food
from agents.hotel_finder import search_hotels
from agents.cuisine_recommend import get_cuisines
from agents.attractions_finder import get_attractions
from agents.youtube_travel_agent import get_destination_video_data
from agents.festival_event_finder import fetch_festivals_and_events
from agents.fetch_travel_news import fetch_travel_news
from agents.food_culture_recommender import food_culture_recommender
from agents.package_list_generator import generate_packages
from agents.itinerary import generate_itinerary
from agents.shopping_places import ShoppingPlacesFinder
import os

# Initialize FastAPI app
app = FastAPI(
    title="AI Travel Agent API",
    description="Backend API for AI Travel Planning Application",
    version="1.0.0"
)

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# ==================== Request Models ====================

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class FlightSearchRequest(BaseModel):
    from_city: str
    to_city: str
    date: str
    passengers: int = 1

class WeatherRequest(BaseModel):
    city: str

class BudgetRequest(BaseModel):
    destination: str
    days: int
    budget_level: str = "Moderate"

class CurrencyRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class ActivityRequest(BaseModel):
    destination: str
    interests: List[str] = []

class ItineraryRequest(BaseModel):
    destination: str
    days: int
    interests: List[str] = []
    budget_level: str = "Moderate"

class HotelRequest(BaseModel):
    city: str
    checkin: str
    checkout: str
    guests: int = 1

class PackingListRequest(BaseModel):
    destination: str
    days: int
    season: str = "summer"

class CuisineRequest(BaseModel):
    destination: str

class AttractionsRequest(BaseModel):
    destination: str

# Authentication Request Models
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Import authentication utilities
from database.mongodb import get_users_collection, get_otp_collection
from utils.email_sender import email_sender
from utils.auth_utils import auth_utils

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Travel Agent API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "chat": "operational",
            "flights": "operational",
            "weather": "operational",
            "hotels": "operational"
        }
    }

# ==================== Authentication ====================

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """
    User signup - sends OTP to email
    """
    try:
        # Validate email
        if not auth_utils.validate_email(request.email):
            return {
                "success": False,
                "message": "Invalid email format"
            }
        
        # Validate password strength
        is_valid, error_msg = auth_utils.validate_password_strength(request.password)
        if not is_valid:
            return {
                "success": False,
                "message": error_msg
            }
        
        users_collection = get_users_collection()
        otp_collection = get_otp_collection()
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": request.email})
        if existing_user:
            return {
                "success": False,
                "message": "Email already registered"
            }
        
        # Generate OTP
        otp = email_sender.generate_otp()
        
        # Send OTP email
        email_sent = email_sender.send_otp_email(request.email, otp, request.name)
        
        if not email_sent:
            return {
                "success": False,
                "message": "Failed to send OTP email. Please try again."
            }
        
        # Store OTP with user data (temporary)
        from datetime import datetime, timedelta
        otp_data = {
            "email": request.email,
            "name": request.name,
            "password_hash": auth_utils.hash_password(request.password),
            "otp": otp,
            "otp_expiry": datetime.utcnow() + timedelta(minutes=10),
            "created_at": datetime.utcnow()
        }
        
        # Delete any existing OTP for this email
        otp_collection.delete_many({"email": request.email})
        
        # Insert new OTP
        otp_collection.insert_one(otp_data)
        
        return {
            "success": True,
            "message": "OTP sent to your email. Please verify to complete registration.",
            "email": request.email
        }
        
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """
    Verify OTP and create user account
    """
    try:
        from datetime import datetime
        otp_collection = get_otp_collection()
        users_collection = get_users_collection()
        
        # Find OTP record
        otp_record = otp_collection.find_one({"email": request.email})
        
        if not otp_record:
            return {
                "success": False,
                "message": "No OTP found for this email. Please signup again."
            }
        
        # Check if OTP expired
        if datetime.utcnow() > otp_record['otp_expiry']:
            otp_collection.delete_one({"email": request.email})
            return {
                "success": False,
                "message": "OTP expired. Please signup again."
            }
        
        # Verify OTP
        if otp_record['otp'] != request.otp:
            return {
                "success": False,
                "message": "Invalid OTP. Please try again."
            }
        
        # Create user account
        user_data = {
            "name": otp_record['name'],
            "email": otp_record['email'],
            "password_hash": otp_record['password_hash'],
            "verified": True,
            "created_at": datetime.utcnow()
        }
        
        users_collection.insert_one(user_data)
        
        # Delete OTP record
        otp_collection.delete_one({"email": request.email})
        
        # Create JWT token
        token = auth_utils.create_access_token({
            "email": user_data['email'],
            "name": user_data['name']
        })
        
        # Send welcome email
        email_sender.send_welcome_email(user_data['email'], user_data['name'])
        
        return {
            "success": True,
            "message": "Account created successfully!",
            "user": {
                "name": user_data['name'],
                "email": user_data['email']
            },
            "token": token
        }
        
    except Exception as e:
        print(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """
    User login
    """
    try:
        users_collection = get_users_collection()
        
        # Find user
        user = users_collection.find_one({"email": request.email})
        
        if not user:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Check if verified
        if not user.get('verified', False):
            return {
                "success": False,
                "message": "Please verify your email first"
            }
        
        # Verify password
        if not auth_utils.verify_password(request.password, user['password_hash']):
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        
        # Create JWT token
        token = auth_utils.create_access_token({
            "email": user['email'],
            "name": user['name']
        })
        
        return {
            "success": True,
            "message": "Login successful!",
            "user": {
                "name": user['name'],
                "email": user['email']
            },
            "token": token
        }
        
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Chat Agent ====================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with AI travel assistant
    """
    try:
        response = get_chat_response(request.message, request.history)
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Flight Services ====================

@app.post("/api/flights/search")
async def search_flights_endpoint(request: FlightSearchRequest):
    """
    Search for flights between cities
    """
    try:
        result = search_flights(
            request.from_city,
            request.to_city,
            request.date,
            request.passengers
        )
        
        # If API fails, provide mock data
        if "error" in result or not result.get("flights"):
            mock_flights = get_mock_flights(request.from_city, request.to_city, request.date)
            return {
                "success": True,
                "flights": mock_flights,
                "is_mock": True,
                "message": "Using demo data (API unavailable)"
            }
        
        return {
            "success": True,
            "flights": result["flights"],
            "is_mock": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/flights/links")
async def get_flight_links(request: FlightSearchRequest):
    """
    Get flight booking links from various providers
    """
    try:
        return {
            "success": True,
            "links": {
                "google_flights": get_google_flights_link(request.from_city, request.to_city, request.date),
                "skyscanner": get_skyscanner_link(request.from_city, request.to_city, request.date),
                "kayak": get_kayak_link(request.from_city, request.to_city, request.date)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Weather Service ====================

@app.post("/api/weather")
async def get_weather_endpoint(request: WeatherRequest):
    """
    Get weather information for a city
    """
    try:
        weather_data = get_weather(request.city)
        
        if "error" in weather_data:
            raise HTTPException(status_code=404, detail=weather_data["error"])
        
        return {
            "success": True,
            "data": weather_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Budget & Currency ====================

@app.post("/api/budget/estimate")
async def estimate_budget_endpoint(request: BudgetRequest):
    """
    Estimate travel budget for destination
    """
    try:
        budget_data = estimate_budget(request.destination, request.days, request.budget_level)
        return {
            "success": True,
            "data": budget_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/currency/convert")
async def convert_currency_endpoint(request: CurrencyRequest):
    """
    Convert currency between two currencies
    """
    try:
        result = convert_currency(request.amount, request.from_currency, request.to_currency)
        # currency_converter already returns {"success": bool, "data": {...}}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Activities & Itinerary ====================

@app.post("/api/activities/recommend")
async def recommend_activities_endpoint(request: ActivityRequest):
    """
    Get activity recommendations for destination
    """
    try:
        result = get_activities_and_food(request.destination)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/itinerary/generate")
async def generate_itinerary_endpoint(request: ItineraryRequest):
    """
    Generate travel itinerary using AI
    """
    try:
        # Create a simple itinerary based on activities
        activities = get_activities_and_food(request.destination)
        itinerary = {
            "destination": request.destination,
            "days": request.days,
            "activities": activities.get("activities", []),
            "food": activities.get("food", [])
        }
        return {
            "success": True,
            "itinerary": itinerary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Hotels ====================

@app.post("/api/hotels/search")
async def search_hotels_endpoint(request: HotelRequest):
    """
    Search for hotels in a city with enriched data (ratings, offers, images)
    """
    try:
        hotels = search_hotels(request.city, radius=10000, limit=10)
        
        # If no hotels found, return helpful message
        if not hotels or len(hotels) == 0:
            return {
                "success": False,
                "hotels": [],
                "message": f"No hotels found in {request.city}. Try popular cities like Paris, London, or Tokyo."
            }
        
        return {
            "success": True,
            "hotels": hotels,
            "is_mock": not bool(os.getenv("OPENTRIP_API_KEY"))
        }
    except Exception as e:
        print(f"Hotel search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Shopping Places ====================

class ShoppingRequest(BaseModel):
    city: str
    radius_km: int = 5
    limit: int = 30

@app.post("/api/shopping/places")
async def search_shopping_places_endpoint(request: ShoppingRequest):
    """
    Search for shopping places in a city with images from Pexels/Unsplash
    """
    try:
        from agents.shopping_places import ShoppingPlacesFinder
        
        api_key = os.getenv("GEOAPIFY_API_KEY")
        if not api_key:
            # Return mock data if no API key
            return {
                "success": True,
                "places": {
                    "shopping_malls": [
                        {
                            "name": f"{request.city} Mall",
                            "address": f"Central {request.city}",
                            "distance": 2.5,
                            "image_url": "https://source.unsplash.com/400x300/?shopping,mall"
                        }
                    ],
                    "local_markets": [
                        {
                            "name": f"{request.city} Market",
                            "address": f"Old Town, {request.city}",
                            "distance": 1.8,
                            "image_url": "https://source.unsplash.com/400x300/?market,shopping"
                        }
                    ],
                    "retail_areas": []
                }
            }
        
        finder = ShoppingPlacesFinder(api_key)
        results = finder.find_shopping_places(
            location=request.city,
            radius_km=request.radius_km,
            limit=request.limit
        )
       
        if "error" in results:
            return {
                "success": False,
                "places": {},
                "message": results["error"]
            }
        
        # Add images to each place
        for category in ["shopping_malls", "local_markets", "retail_areas"]:
            places = results.get(category, [])
            for place in places:
                if "image_url" not in place or not place.get("image_url"):
                    # Fetch image using the get_place_image method
                    place["image_url"] = finder.get_place_image(place.get("name", "shopping"))
                # Rename distance_km to distance for frontend compatibility
                if "distance_km" in place:
                    place["distance"] = place["distance_km"]
        
        return {
            "success": True,
            "places": results
        }
    except Exception as e:
        print(f"Shopping places error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Travel Resources ====================

@app.post("/api/resources/useful-links")
async def get_useful_links_endpoint(request: WeatherRequest):
    """
    Get useful travel links for destination
    """
    try:
        # Return some default useful links
        links = [
            {"title": "TripAdvisor", "url": f"https://www.tripadvisor.com/Search?q={request.city}"},
            {"title": "Lonely Planet", "url": f"https://www.lonelyplanet.com/search?q={request.city}"},
            {"title": "Google Maps", "url": f"https://www.google.com/maps/search/{request.city}"}
        ]
        return {
            "success": True,
            "links": links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resources/packing-list")
async def generate_packing_list_endpoint(request: PackingListRequest):
    """
    Generate AI-powered packing list for trip
    """
    try:
        from langchain_core.messages import HumanMessage
        from langchain_groq import ChatGroq
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not groq_api_key:
            # Fallback to basic list
            return {
                "success": True,
                "packing_list": {
                    "essentials": ["Passport", "Travel documents", "Phone charger", "Medications", "Toiletries", "Cash/Cards"],
                    "clothing": ["Comfortable shoes", "Weather-appropriate clothes", "Sunglasses", "Hat", "Jacket"],
                    "electronics": ["Phone charger", "Camera", "Power adapter"],
                    "destination": request.destination,
                    "days": request.days
                }
            }
        
        # Use AI to generate smart packing list
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3, api_key=groq_api_key)
        prompt = f"""Generate a comprehensive packing list for a {request.days}-day trip to {request.destination} during {request.season}.

Organize items into these categories:
1. Essentials (travel documents, money, health items)
2. Clothing (based on weather and activities)
3. Electronics (gadgets and chargers)

Return ONLY items relevant to this specific destination and season.
Format each category as a simple list. Include 5-8 items per category.
Be practical and specific to {request.destination}'s climate and culture."""

        try:
            result = llm.invoke([HumanMessage(content=prompt)]).content
            
            # Parse the AI response
            lines = result.split('\n')
            essentials = []
            clothing = []
            electronics = []
            current_category = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Detect category
                if 'essential' in line.lower() and ':' in line:
                    current_category = 'essentials'
                    continue
                elif 'clothing' in line.lower() and ':' in line:
                    current_category = 'clothing'
                    continue
                elif 'electronic' in line.lower() and ':' in line:
                    current_category = 'electronics'
                    continue
                
                # Extract items
                item = line.lstrip('- *•1234567890.').strip()
                if len(item) > 3:
                    if current_category == 'essentials':
                        essentials.append(item)
                    elif current_category == 'clothing':
                        clothing.append(item)
                    elif current_category == 'electronics':
                        electronics.append(item)
            
            # Ensure we have items
            if not essentials:
                essentials = ["Passport", "Travel insurance", "Medications", "Cash/Cards", "Phone"]
            if not clothing:
                clothing = ["Comfortable shoes", "Weather-appropriate outfits", "Jacket", "Sunglasses"]
            if not electronics:
                electronics = ["Phone charger", "Camera", "Power adapter"]
            
            return {
                "success": True,
                "packing_list": {
                    "essentials": essentials[:8],
                    "clothing": clothing[:8],
                    "electronics": electronics[:6],
                    "destination": request.destination,
                    "days": request.days
                }
            }
        except Exception as ai_error:
            print(f"AI packing list error: {ai_error}")
            # Fallback to basic list
            return {
                "success": True,
                "packing_list": {
                    "essentials": ["Passport", "Travel documents", "Phone charger", "Medications", "Toiletries", "Cash/Cards"],
                    "clothing": ["Comfortable shoes", "Weather-appropriate clothes", "Sunglasses", "Hat", "Jacket"],
                    "electronics": ["Phone charger", "Camera", "Power adapter"],
                    "destination": request.destination,
                    "days": request.days
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resources/cuisine")
async def recommend_cuisine_endpoint(request: CuisineRequest):
    """
    Get cuisine recommendations for destination
    """
    try:
        cuisines = get_cuisines(request.destination, radius=5000, limit=10)
        return {
            "success": True,
            "cuisines": cuisines
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resources/attractions")
async def find_attractions_endpoint(request: AttractionsRequest):
    """
    Find tourist attractions in destination
    """
    try:
        result = get_attractions(request.destination)
        # get_attractions returns {"success": bool, "attractions": string}
        if result.get("success"):
            return {
                "success": True,
                "attractions": result.get("attractions", "")
            }
        else:
            return {
                "success": False,
                "attractions": result.get("attractions", "No information available")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== New Enhanced Endpoints ====================

@app.post("/api/youtube/videos")
async def get_youtube_videos(request: WeatherRequest):
    """
    Get YouTube travel videos for destination
    """
    try:
        videos = get_destination_video_data(
            destination=request.city,
            max_results=6,
            prefer_with_captions=True
        )
        return {
            "success": True,
            "videos": videos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/events/search")
async def search_events(request: WeatherRequest):
    """
    Find festivals and events at destination
    """
    try:
        events = fetch_festivals_and_events(
            location=request.city,
            days_ahead=30,
            keyword="festival"
        )
        return {
            "success": True,
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/travel")
async def get_travel_news(request: WeatherRequest):
    """
    Get latest travel news for destination
    """
    try:
        news = fetch_travel_news(
            destination=request.city,
            max_results=10
        )
        return {
            "success": True,
            "news": news
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/food/culture")
async def get_food_culture(request: CuisineRequest):
    """
    Get food and culture recommendations
    """
    try:
        state = {
            "preferences": {
                "destination": request.destination,
                "budget_type": "mid-range"
            }
        }
        result = food_culture_recommender(state)
        return {
            "success": True,
            "data": result.get("food_culture_info", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/packages/list")
async def get_packages(request: WeatherRequest):
    """
    Get travel packages for destination
    """
    try:
        packages = generate_packages(request.city)
        return {
            "success": True,
            "packages": packages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/itinerary/enhanced")
async def generate_enhanced_itinerary(request: ItineraryRequest):
    """
    Generate AI-powered travel itinerary
    """
    try:
        result = generate_itinerary(
            destination=request.destination,
            days=request.days,
            budget=request.budget_level,
            interests=request.interests
        )
        return {
            "success": True,
            "itinerary": result.get("itinerary", ""),
            "warning": result.get("warning")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Run Server ====================

if __name__ == "__main__":
    print("🚀 Starting AI Travel Agent API Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Alternative docs: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

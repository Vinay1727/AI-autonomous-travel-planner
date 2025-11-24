# AI Travel Agent API Documentation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_v2.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here
OPENTRIP_API_KEY=your_opentrip_api_key_here
OPENTRIPMAP_KEY=your_opentripmap_key_here
```

### 3. Run the Server
```bash
python main.py
```

The API will be available at: **http://localhost:8000**

### 4. View API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed service status

### Chat Agent
- **POST** `/api/chat`
  ```json
  {
    "message": "I want to visit Paris",
    "history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"}
    ]
  }
  ```

### Flight Services
- **POST** `/api/flights/search`
  ```json
  {
    "from_city": "New York",
    "to_city": "Paris",
    "date": "2024-12-25",
    "passengers": 2
  }
  ```

- **POST** `/api/flights/links`
  ```json
  {
    "from_city": "New York",
    "to_city": "Paris",
    "date": "2024-12-25"
  }
  ```

### Weather
- **POST** `/api/weather`
  ```json
  {
    "city": "Paris"
  }
  ```

### Budget & Currency
- **POST** `/api/budget/estimate`
  ```json
  {
    "destination": "Paris",
    "days": 7,
    "budget_level": "Moderate"
  }
  ```

- **POST** `/api/currency/convert`
  ```json
  {
    "amount": 100,
    "from_currency": "USD",
    "to_currency": "EUR"
  }
  ```

### Activities & Itinerary
- **POST** `/api/activities/recommend`
  ```json
  {
    "destination": "Paris",
    "interests": ["museums", "food"]
  }
  ```

- **POST** `/api/itinerary/generate`
  ```json
  {
    "destination": "Paris",
    "days": 5,
    "interests": ["culture", "food"],
    "budget_level": "Moderate"
  }
  ```

### Hotels
- **POST** `/api/hotels/search`
  ```json
  {
    "city": "Paris",
    "checkin": "2024-12-20",
    "checkout": "2024-12-27",
    "guests": 2
  }
  ```

### Travel Resources
- **POST** `/api/resources/useful-links`
  ```json
  {
    "city": "Paris"
  }
  ```

- **POST** `/api/resources/packing-list`
  ```json
  {
    "destination": "Paris",
    "days": 7,
    "season": "winter"
  }
  ```

- **POST** `/api/resources/cuisine`
  ```json
  {
    "destination": "Paris"
  }
  ```

- **POST** `/api/resources/attractions`
  ```json
  {
    "destination": "Paris"
  }
  ```

---

## 🔧 Frontend Integration

### Using Fetch API (JavaScript)
```javascript
// Example: Search flights
async function searchFlights() {
  const response = await fetch('http://localhost:8000/api/flights/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from_city: 'New York',
      to_city: 'Paris',
      date: '2024-12-25',
      passengers: 2
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

### Using Axios (JavaScript)
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Example: Get weather
async function getWeather(city) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/weather`, {
      city: city
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Using Python Requests
```python
import requests

API_BASE_URL = 'http://localhost:8000'

# Example: Chat with AI
def chat_with_ai(message, history=[]):
    response = requests.post(
        f'{API_BASE_URL}/api/chat',
        json={
            'message': message,
            'history': history
        }
    )
    return response.json()
```

---

## 🌐 CORS Configuration

The API is configured to accept requests from any origin (`*`). For production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 Response Format

All endpoints return a consistent JSON format:

### Success Response
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

## 🧪 Testing the API

### Using cURL
```bash
# Health check
curl http://localhost:8000/

# Search flights
curl -X POST http://localhost:8000/api/flights/search \
  -H "Content-Type: application/json" \
  -d '{
    "from_city": "New York",
    "to_city": "Paris",
    "date": "2024-12-25",
    "passengers": 2
  }'
```

### Using Postman
1. Import the API documentation from http://localhost:8000/docs
2. Create a new collection
3. Add requests for each endpoint
4. Test with sample data

---

## 🔐 Security Notes

1. **API Keys**: Never commit `.env` file to version control
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Consider adding rate limiting for production
4. **Authentication**: Add JWT or OAuth for user authentication if needed

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in main.py
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### Module Import Errors
```bash
# Make sure you're in the project directory
cd c:\Users\DELL\OneDrive\Desktop\AI_travel_agent
python main.py
```

### API Key Errors
- Check if `.env` file exists
- Verify API keys are correct
- Some agents will return mock data if API keys are missing

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🤝 Support

For issues or questions, check the API documentation at http://localhost:8000/docs

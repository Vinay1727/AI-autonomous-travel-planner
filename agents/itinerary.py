import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_itinerary(destination, days, budget, interests):
    """
    Generates a travel itinerary using Groq Llama3.
    """
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_itinerary(destination, days, budget, interests):
    """
    Generates a travel itinerary using Groq Llama3.
    """
    if not GROQ_API_KEY:
        return {
            "itinerary": f"**Mock Itinerary for {destination} ({days} days)**\n\n*Day 1*: Arrival and City Tour.\n*Day 2*: Visit main attractions.\n*Day 3*: Shopping and Departure.\n\n(Add GROQ_API_KEY to .env for real AI generation)",
            "warning": "API Key missing"
        }

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=GROQ_API_KEY)
        
        prompt = f"""
        Create a detailed {days}-day travel itinerary for {destination}.
        Budget: {budget}
        Interests: {', '.join(interests)}
        
        Format the output as a structured markdown with:
        - Day-by-day breakdown
        - Morning, Afternoon, Evening activities
        - Dining suggestions
        - Practical tips
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"itinerary": response.content}
        
    except (ImportError, Exception) as e:
        return {
            "itinerary": f"**Mock Itinerary for {destination} ({days} days)**\n\n*Day 1*: Arrival and City Tour.\n*Day 2*: Visit main attractions.\n*Day 3*: Shopping and Departure.\n\n(AI Generation Failed: {str(e)})",
            "warning": "Dependency Error"
        }
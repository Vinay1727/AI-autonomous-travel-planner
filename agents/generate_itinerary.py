from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import json
import os
from dotenv import load_dotenv
#from agents.shopping_places import get_shopping_places   # ✅ import our new module

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_itinerary(state):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, api_key=groq_api_key)

    prompt = f"""
    Using the following preferences, create a detailed itinerary:
    {json.dumps(state['preferences'], indent=2)}

    Include sections for each day, dining options, and downtime.
    """
    try:
        # 1️⃣ Generate base itinerary with LLM
        result = llm.invoke([HumanMessage(content=prompt)]).content.strip()

        # 2️⃣ Try to get city/destination from preferences
        destination = state['preferences'].get("destination") or state['preferences'].get("city")

        

        # 3️⃣ Append shopping places to itinerary
        full_itinerary = result 

        return {"itinerary": full_itinerary}

    except Exception as e:
        return {"itinerary": "", "warning": str(e)}

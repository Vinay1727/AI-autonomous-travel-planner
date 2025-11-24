from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")    

def food_culture_recommender(state):
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1,  api_key=groq_api_key)
    prompt = f"""
    For a trip to {state['preferences'].get('destination', '')} with a {state['preferences'].get('budget_type', 'mid-range')} budget:
    1. Suggest popular local dishes and recommended dining options.
    2. Provide important cultural norms, etiquette tips, and things travelers should be aware of.
    Format the response with clear sections for 'Food & Dining' and 'Culture & Etiquette'.
    """
    try:
        result = llm.invoke([HumanMessage(content=prompt)]).content
        return {"food_culture_info": result.strip()}
    except Exception as e:
        return {"food_culture_info": "", "warning": str(e)}
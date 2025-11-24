import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_chat_response(message, history=[]):
    """
    Generates a response from the travel assistant.
    Uses LangChain/Groq if available, otherwise a mock response.
    """
    if not GROQ_API_KEY:
        return "I'm a demo travel assistant. (API Key missing). I can help you plan trips!"

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=GROQ_API_KEY
        )

        messages = [
            SystemMessage(
                content="You are a helpful, enthusiastic, and knowledgeable travel assistant. Help the user with travel planning, flight tips, and destination advice."
            )
        ]

        # Add chat history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=message))

        # Get response
        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        return f"AI Chat Unavailable (Dependency Error: {str(e)}). Please check your installed packages."

from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key="AIzaSyC9L4CFN-Fwl0ggviGOGWp3HyNjgviWKOM",
        temperature=0.2
    )
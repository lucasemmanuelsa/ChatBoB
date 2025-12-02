from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key="AIzaSyAfT9WjjW91cL_a_sSRuZolA3FDeJdgYrc",
        temperature=0.2
    )
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key="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",
        temperature=0.2
    )

'''
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key="AIzaSyC9L4CFN-Fwl0ggviGOGWp3HyNjgviWKOM",
        temperature=0.2
    )
'''
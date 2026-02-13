import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

API_KEY = st.secrets["OPENAI_API_KEY"]

def get_llm():
    return ChatOpenAI(
        model="gpt-4",
        openai_api_key=API_KEY,
        temperature=0.1,
        max_retries=5
    )

'''
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2
    )
'''
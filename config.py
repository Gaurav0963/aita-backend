''' LLM Configuration: Handles LLM initialization'''

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# Main reasoning model
main_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

# Lightweight model for routing + cleaning
small_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)
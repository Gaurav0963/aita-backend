''' LLM Configuration: Handles LLM initialization'''

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

main_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
)

small_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)
# ==========================================================
# Core AI & LangGraph Logic (Fully Async)
# ==========================================================

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

from config import main_llm, small_llm
from prompts import CLEANING_PROMPT, ROUTING_PROMPT
from helper import get_hash, extract_questions_from_html
from cache import LAB_CACHE
from logger import setup_logger

logger = setup_logger("ai_core")

# ---------------- LangGraph Setup ----------------

class State(TypedDict):
    messages: Annotated[list, add_messages]

async def chatbot_node(state: State):
    response = await main_llm.ainvoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

memory = MemorySaver()
app_graph = builder.compile(checkpointer=memory)

# ---------------- Cleaning ----------------

async def clean_question_content(raw_text: str) -> str:
    formatted_prompt = CLEANING_PROMPT.format(raw_text=raw_text[:6000])
    response = await small_llm.ainvoke([HumanMessage(content=formatted_prompt)])
    return response.content.strip()

# ---------------- Routing ----------------

async def detect_relevant_question(user_msg: str, questions: dict) -> str:
    question_summary = "\n".join(
        [f"{q_id}: {q_data['title']}" for q_id, q_data in questions.items()]
    )

    formatted_prompt = ROUTING_PROMPT.format(
        question_summary=question_summary,
        user_msg=user_msg
    )

    response = await small_llm.ainvoke([HumanMessage(content=formatted_prompt)])
    label = response.content.strip().lower()

    if label in questions:
        return label

    return list(questions.keys())[0]

# ---------------- Lab Loader ----------------

async def get_clean_lab_questions(lab_id: str) -> dict:

    raw_questions = extract_questions_from_html(lab_id)
    if not raw_questions:
        return {}

    combined_text = "".join([q["content"] for q in raw_questions.values()])
    current_hash = get_hash(combined_text)

    if lab_id in LAB_CACHE and LAB_CACHE[lab_id]["hash"] == current_hash:
        return LAB_CACHE[lab_id]["questions"]

    cleaned_questions = {}

    for q_id, q_data in raw_questions.items():
        cleaned_questions[q_id] = {
            "title": q_data["title"],
            "content": await clean_question_content(q_data["content"])
        }

    LAB_CACHE[lab_id] = {
        "hash": current_hash,
        "questions": cleaned_questions
    }

    logger.info(f"Cached lab: {lab_id}")
    return cleaned_questions
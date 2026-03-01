# ==========================================================
# AI Core Logic + Smart Lab Cache
# ==========================================================

from langchain_core.messages import HumanMessage
from config import main_llm, small_llm
from prompts import CLEANING_PROMPT, ROUTING_PROMPT
from helper import extract_questions_from_html

# -------------------------------
# Global Lab Cache (Safe)
# -------------------------------

LAB_CACHE = {}

# -------------------------------
# Cleaning
# -------------------------------

async def clean_question_content(raw_text: str) -> str:
    formatted_prompt = CLEANING_PROMPT.format(raw_text=raw_text[:6000])
    response = await small_llm.ainvoke(
        [HumanMessage(content=formatted_prompt)]
    )
    return response.content.strip()

# -------------------------------
# Question Routing
# -------------------------------

async def detect_relevant_question(user_msg: str, questions: dict) -> str:
    question_summary = "\n".join(
        [f"{q_id}: {q_data['title']}" for q_id, q_data in questions.items()]
    )

    formatted_prompt = ROUTING_PROMPT.format(
        question_summary=question_summary,
        user_msg=user_msg
    )

    response = await small_llm.ainvoke(
        [HumanMessage(content=formatted_prompt)]
    )

    label = response.content.strip().lower()

    if label in questions:
        return label

    return list(questions.keys())[0]

# -------------------------------
# Smart Lab Loader (RESTORED)
# -------------------------------

async def get_clean_lab_questions(lab_id: str) -> dict:
    """
    Fetches lab from Firebase only once.
    Cleans it once.
    Caches permanently in memory.
    """

    if lab_id in LAB_CACHE:
        return LAB_CACHE[lab_id]

    raw_questions = await extract_questions_from_html(lab_id)

    if not raw_questions:
        return {}

    cleaned_questions = {}

    for q_id, q_data in raw_questions.items():
        cleaned_questions[q_id] = {
            "title": q_data["title"],
            "content": await clean_question_content(q_data["content"])
        }

    LAB_CACHE[lab_id] = cleaned_questions

    return cleaned_questions
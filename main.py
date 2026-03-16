# ==========================================================
# AITA Production Backend - main.py
# ==========================================================

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from langchain_core.messages import SystemMessage, HumanMessage

from database import engine, Base
from memory import get_conversation, save_conversation
from config import main_llm
from prompts import BASE_PERSONA
from schemas import ChatRequest
from ai_core import (
    get_clean_lab_questions,
    detect_relevant_question
)
from logger import setup_logger

logger = setup_logger("main")

# ----------------------------------------------------------
# Rate Limiting (Load-Balancer Safe with proxy headers)
# ----------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="AITA Backend")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ----------------------------------------------------------
# CORS
# ----------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with Firebase domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# Startup: Ensure DB Tables Exist
# ----------------------------------------------------------

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")

# ----------------------------------------------------------
# Chat Endpoint
# ----------------------------------------------------------

@app.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, payload: ChatRequest):

    # 1. Load Conversation History (PostgreSQL)
    history = await get_conversation(payload.thread_id)

    # 2. Fetch & Cache Lab Context (Smart Cache)
    lab_context = ""

    if payload.lab_id:
        questions = await get_clean_lab_questions(payload.lab_id)

        if questions:
            selected_q = await detect_relevant_question(
                payload.message,
                questions
            )
            lab_context = questions[selected_q]["content"]

    # 3. Build System Prompt
    system_prompt = f"""
{BASE_PERSONA}

OFFICIAL CURRENT LAB CONTEXT:
{lab_context[:8000]}
"""

    messages = [SystemMessage(content=system_prompt)]

    # 4. Append Previous Conversation
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(SystemMessage(content=msg["content"]))

    # 5. Handle File Attachment
    user_input = payload.message

    if hasattr(payload, "file_content") and payload.file_content:
        user_input += f"\n\n[Attached File]\n{payload.file_content}"

    messages.append(HumanMessage(content=user_input))

    # 6. Call LLM
    try:
        response = await main_llm.ainvoke(messages)
        reply = response.content

        # 7. Persist Conversation
        history.append({"role": "user", "content": payload.message})
        history.append({"role": "assistant", "content": reply})

        await save_conversation(payload.thread_id, history)

        return {
            "reply": reply,
            "thread_id": payload.thread_id
        }

    except Exception as e:
        logger.error(f"LLM processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="LLM processing failed."
        )

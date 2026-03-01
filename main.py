# ==========================================================
# Main FastAPI Server (Fully Async)
# ==========================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from langchain_core.messages import SystemMessage, HumanMessage

from prompts import BASE_PERSONA
from schemas import ChatRequest
from ai_core import (
    get_clean_lab_questions,
    detect_relevant_question,
    app_graph,
)
from logger import setup_logger

logger = setup_logger("main")

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(title="AITA Backend API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"status": "ok", "service": "AITA Async Backend"}

@app.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, payload: ChatRequest):

    if len(payload.file_content) > 15000:
        raise HTTPException(status_code=400, detail="File too large.")

    questions = await get_clean_lab_questions(payload.lab_id)

    if questions:
        selected_q = await detect_relevant_question(payload.message, questions)
        relevant_context = questions[selected_q]["content"]
    else:
        relevant_context = ""

    system_prompt = f"""
{BASE_PERSONA}

OFFICIAL CURRENT LAB QUESTION:
{relevant_context[:8000]}
"""

    full_user_msg = payload.message

    if payload.file_content:
        full_user_msg += f"\n\n[Attached File: {payload.file_name}]\n```python\n{payload.file_content}\n```"

    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_user_msg)
        ]

        output_state = await app_graph.ainvoke({"messages": messages}, config)
        reply = output_state["messages"][-1].content

        return {"reply": reply, "thread_id": payload.thread_id}

    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail="LLM processing failed.")
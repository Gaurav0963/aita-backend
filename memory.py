import json
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Conversation
from logger import setup_logger

logger = setup_logger("memory")

async def get_conversation(thread_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.thread_id == thread_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            return json.loads(conversation.messages)

        return []

async def save_conversation(thread_id: str, messages: list):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.thread_id == thread_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.messages = json.dumps(messages)
        else:
            conversation = Conversation(
                thread_id=thread_id,
                messages=json.dumps(messages),
            )
            session.add(conversation)

        await session.commit()
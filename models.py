from sqlalchemy import Column, String, Text
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    thread_id = Column(String, primary_key=True)
    messages = Column(Text)
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    thread_id: str
    lab_id: str | None = None
    question_id: str | None = None
    question_detail: str | None = None  # <-- Added this so FastAPI accepts the context!
    file_content: str | None = None
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str = ""
    lab_id: str = "home"
    thread_id: str = "new_thread"
    file_name: str = ""
    file_content: str = ""
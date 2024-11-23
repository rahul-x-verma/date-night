import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from date_night_api.chatbot.chatbot import Chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],
)

@app.get("/")
def health():
    return None, 200


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.thread_id:
        thread_id = str(uuid.uuid4())
    else:
        thread_id = request.thread_id
    async with Chatbot() as chatbot:
        response = await chatbot.ainvoke(message=request.message, thread_id=thread_id)
        return {"response": response.content, "thread_id": thread_id}

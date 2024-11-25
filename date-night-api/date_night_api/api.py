import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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



@app.post("/chat")
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            thread_id = data.get("thread_id")

            if not thread_id:
                thread_id = str(uuid.uuid4())

            async with Chatbot() as chatbot:
                response = await chatbot.ainvoke(message=message, thread_id=thread_id)
                
                # Send response back to client
                await websocket.send_json({
                    "response": response,
                    "thread_id": thread_id
                })

                
    except WebSocketDisconnect:
        pass


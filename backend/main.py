from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import generate_answer


app = FastAPI()


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Structure of the message coming from React
class ChatRequest(BaseModel):
    message: str


# Simple test endpoint
@app.get("/")
def home():
    return {
        "message": "Sree Dattha Chatbot API is running"
    }


# Chat endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    answer = generate_answer(
        request.message
    )

    return {
        "answer": answer
    }
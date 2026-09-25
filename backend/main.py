from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import generate_answer


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://sreedattha-chatbot-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Sree Dattha Chatbot API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = generate_answer(
        request.message
    )

    return {
        "answer": answer
    }
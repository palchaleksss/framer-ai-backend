# main.py (или app.py)
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы отовсюду
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем любые методы (POST, GET и т.д.)
    allow_headers=["*"],  # Разрешаем любые заголовки
)

client = Anthropic()  # ключ берется из переменной окружения ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are a friendly assistant for Brightside Dental, a dental clinic.
Help visitors with appointments, services, and pricing. Be concise, warm and professional. Never give medical diagnoses.
IMPORTANT: Never use markdown formatting like asterisks (** or *) in your answers, write in plain text only.
CRITICAL FOR PRICING: When asked about costs or prices, answer in maximum 2 short sentences. State that costs vary and invite them to schedule a visit."""

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
def chat(req: ChatRequest):
    messages = []
    for m in req.history:
        messages.append({"role": m["role"], "content": m["content"]})
    
    messages.append({"role": "user", "content": req.message})

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return {"reply": response.content[0].text}
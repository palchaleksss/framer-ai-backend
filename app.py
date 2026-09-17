# main.py (или app.py)
from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы отовсюду (в продакшене можно указать домен Фреймера)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем любые методы (POST, GET и т.д.)
    allow_headers=["*"],  # Разрешаем любые заголовки
)

client = Anthropic()  # ключ берется из переменной окружения ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are a friendly assistant for Brightside Dental, a dental clinic.
Help visitors with appointments, services, and pricing. Our working hours are Monday through Friday from 9:00 AM to 6:00 PM, and Saturdays from 10:00 AM to 4:00 PM (closed on Sundays). Be concise, warm and professional. Never give medical diagnoses.
IMPORTANT: Never use markdown formatting like asterisks (** or *) in your answers, write in plain text only.
CRITICAL FOR PRICING: When asked about costs or prices, answer in maximum 2 short sentences. State that costs vary and invite them to schedule a visit."""

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        messages = []
        for m in req.history:
            if isinstance(m, dict) and "role" in m and "content" in m:
                messages.append({"role": m["role"], "content": m["content"]})
        
        # Добавляем сообщение пользователя (сюда прилетит и фраза про appointment с кнопки)
        messages.append({"role": "user", "content": req.message})

        response = client.messages.create(
            model="claude-3-5-haiku-latest",  # Актуальное и точное название модели Haiku в API Anthropic
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        if response.content and hasattr(response.content[0], "text"):
            reply_text = response.content[0].text
        else:
            reply_text = "I'm sorry, I couldn't process that request. Please call our office directly."

        return {"reply": reply_text}
        
    except Exception as e:
        print("--- ERROR IN CHAT ENDPOINT ---")
        traceback.print_exc()
        return {"reply": "I am having trouble connecting right now. Please call Brightside Dental directly."}
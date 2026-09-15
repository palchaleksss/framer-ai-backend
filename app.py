# main.py
from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI()

# Разрешаем запросы с домена сайта на Framer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем отовсюду
    allow_origin_regex=".*",  # Разрешаем любые регулярные выражения доменов (включая фреймы)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic()  # ключ берется из переменной окружения ANTHROPIC_API_KEY

SYSTEM_PROMPT = """You are a friendly assistant for Brightside Dental, a dental clinic.
Help visitors with appointments, services (check-up & cleaning, teeth whitening,
dental implants, emergency care), working hours (Mon–Fri 8:00–18:00, Sat 9:00–14:00)
and pricing. Be concise, warm and professional. Never give medical diagnoses —
always suggest booking a visit with a dentist instead."""

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
def chat(req: ChatRequest):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            *[{"role": m["role"], "content": m["content"]} for m in req.history],
            {"role": "user", "content": req.message},
        ],
    )
    return {"reply": response.content[0].text}
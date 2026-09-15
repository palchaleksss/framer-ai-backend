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
Help visitors with appointments, services, and pricing. Be concise, warm and professional. Never give medical diagnoses.
IMPORTANT: Never use markdown formatting like asterisks (** or *) in your answers, write in plain text only.
CRITICAL FOR PRICING: When asked about costs, prices, or fees, keep your response structured in 2-3 short paragraphs separated by line breaks. Give a brief general overview without listing every single service in massive detail, and politely invite them to schedule a visit for exact pricing."""
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/chat")
def chat(req: ChatRequest):
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            *[{"role": m["role"], "content": m["content"]} for m in req.history],
            {"role": "user", "content": req.message},
        ],
    )
    return {"reply": response.content[0].text}
import os
import requests
from dotenv import load_dotenv

from .config import MODEL, BASE_URL, TEMPERATURE, MAX_TOKENS, TIMEOUT

load_dotenv()

API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env")


def chamar_modelo(mensagens: list[dict], temperatura: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> str:
    resposta = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": mensagens,
            "temperature": temperatura,
            "max_tokens": max_tokens,
        },
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    return resposta.json()["choices"][0]["message"]["content"]
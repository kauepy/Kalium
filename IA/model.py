import os
import requests
from dotenv import load_dotenv

from .config import (
    MODEL,
    BASE_URL,
    TEMPERATURE,
    MAX_TOKENS,
    TIMEOUT,
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("OPENROUTER_API_KEY")


def chamar_modelo(messages):
    """
    Envia mensagens para o modelo através da OpenRouter
    e retorna somente o texto da resposta.
    """

    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY não encontrada no arquivo .env"
        )

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": TEMPERATURE,
                "max_tokens": MAX_TOKENS,
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            raise RuntimeError(
                f"OpenRouter retornou {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "A OpenRouter demorou muito para responder."
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Erro ao conectar com a OpenRouter: {error}"
        )

    except (KeyError, IndexError):
        raise RuntimeError(
            "A resposta da OpenRouter veio em um formato inesperado."
        )
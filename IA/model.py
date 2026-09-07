import logging
import os

import requests
from dotenv import load_dotenv

try:
    from .config import MODEL, BASE_URL, TEMPERATURE, MAX_TOKENS, TIMEOUT
    from .security import validar_resposta_ia
except ImportError:
    from config import MODEL, BASE_URL, TEMPERATURE, MAX_TOKENS, TIMEOUT
    from security import validar_resposta_ia

load_dotenv()

logger = logging.getLogger("kalium.model")

API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env")


class ErroModelo(Exception):
    pass


class ChaveInvalida(ErroModelo):
    pass


class ModeloIndisponivel(ErroModelo):
    pass


class TimeoutModelo(ErroModelo):
    pass


def chamar_modelo(mensagens: list[dict], temperatura: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> str:
    try:
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
    except requests.exceptions.Timeout as e:
        logger.exception("Timeout ao chamar o modelo")
        raise TimeoutModelo("O modelo demorou demais pra responder.") from e
    except requests.exceptions.RequestException as e:
        logger.exception("Falha de rede ao chamar o modelo")
        raise ModeloIndisponivel("Não foi possível conectar ao modelo agora.") from e

    if resposta.status_code == 401:
        logger.error("Chave da API do OpenRouter inválida ou expirada")
        raise ChaveInvalida("Chave de API inválida.")

    if resposta.status_code in (429, 503):
        logger.error("Modelo indisponível (status %s)", resposta.status_code)
        raise ModeloIndisponivel("O modelo está indisponível no momento.")

    try:
        resposta.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.exception("Erro HTTP inesperado do modelo")
        raise ModeloIndisponivel("O modelo retornou um erro inesperado.") from e

    dados = resposta.json()
    try:
        texto = dados["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        logger.exception("Resposta do modelo em formato inesperado")
        raise ModeloIndisponivel("O modelo retornou uma resposta em formato inesperado.") from e

    return validar_resposta_ia(texto)
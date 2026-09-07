import re
import unicodedata
from ipaddress import ip_address
from urllib.parse import urlparse

TAMANHO_MAX_PERGUNTA = 500
TAMANHO_MAX_CONTEXTO = 8000
TAMANHO_MAX_RESPOSTA = 4000
TAMANHO_MAX_TITULO = 200
TAMANHO_MAX_URL = 500
TAMANHO_MAX_TRECHO = 1000
MAX_FONTES = 5

ESQUEMAS_PERMITIDOS = {"http", "https"}


class PerguntaInvalida(Exception):
    pass


def normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKC", texto).strip()
    return re.sub(r"[\x00-\x1f\x7f]", "", texto)  # tira caractere de controle


def validar_pergunta(pergunta) -> str:
    if not isinstance(pergunta, str):
        raise PerguntaInvalida("A pergunta precisa ser texto.")

    pergunta = normalizar_texto(pergunta)

    if not pergunta:
        raise PerguntaInvalida("A pergunta não pode estar vazia.")

    if len(pergunta) > TAMANHO_MAX_PERGUNTA:
        raise PerguntaInvalida(f"Pergunta muito longa (máx {TAMANHO_MAX_PERGUNTA} caracteres).")

    return pergunta


def limitar_contexto(contexto: str) -> str:
    if len(contexto) > TAMANHO_MAX_CONTEXTO:
        return contexto[:TAMANHO_MAX_CONTEXTO] + "\n[...contexto truncado...]"
    return contexto


def limitar_fontes(fontes: list[dict]) -> list[dict]:
    return fontes[:MAX_FONTES]


def validar_url(url: str) -> bool:
    # URL passou do limite -> descarta (nunca corta uma URL no meio)
    if len(url) > TAMANHO_MAX_URL:
        return False

    try:
        partes = urlparse(url)
    except ValueError:
        return False

    if partes.scheme not in ESQUEMAS_PERMITIDOS or not partes.hostname:
        return False

    if partes.username or partes.password:
        return False  # bloqueia URL com credenciais embutidas (user:pass@host)

    host = partes.hostname
    try:
        ip = ip_address(host)
    except ValueError:
        return True  # não é IP literal, é domínio normal

    # primeira barreira de SSRF: bloqueia IP interno/reservado.
    # se um dia o assistente for baixar o conteúdo da página (e não só o
    # snippet da busca), o IP resolvido via DNS também precisa passar por
    # essa mesma checagem antes de conectar.
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
        return False

    return True


def validar_fonte(titulo: str, url: str, trecho: str) -> bool:
    titulo = normalizar_texto(titulo)
    trecho = normalizar_texto(trecho)

    if not titulo or not url or not trecho:
        return False
    if len(titulo) > TAMANHO_MAX_TITULO:
        return False
    if len(trecho) > TAMANHO_MAX_TRECHO:
        return False
    if not validar_url(url):
        return False

    return True


def validar_resposta_ia(resposta) -> str:
    if not isinstance(resposta, str) or not resposta.strip():
        raise PerguntaInvalida("A IA não retornou uma resposta válida.")

    if len(resposta) > TAMANHO_MAX_RESPOSTA:
        resposta = resposta[:TAMANHO_MAX_RESPOSTA] + "\n[...resposta truncada...]"

    return resposta
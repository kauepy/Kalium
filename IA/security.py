import re
import unicodedata
from ipaddress import ip_address
from urllib.parse import urlparse


# ============================================================
# LIMITES DE SEGURANÇA
# ============================================================

TAMANHO_MAX_PERGUNTA = 500
TAMANHO_MAX_CONTEXTO = 8000
TAMANHO_MAX_RESPOSTA = 4000
TAMANHO_MAX_FONTE = 4000

MAX_FONTES = 5

MODOS_VALIDOS = {"kalium", "internet"}
ESQUEMAS_PERMITIDOS = {"http", "https"}


# ============================================================
# EXCEÇÕES
# ============================================================

class PerguntaInvalida(Exception):
    pass


class ModoInvalido(Exception):
    pass


class URLInvalida(Exception):
    pass


class ContextoInvalido(Exception):
    pass


class FonteInvalida(Exception):
    pass


class RespostaInvalida(Exception):
    pass


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto: str) -> str:
    """
    Normaliza Unicode e remove caracteres de controle.
    """

    if not isinstance(texto, str):
        raise ValueError("A entrada precisa ser texto.")

    texto = unicodedata.normalize("NFKC", texto)

    # Substitui caracteres de controle por espaço.
    texto = re.sub(r"[\x00-\x1f\x7f]", " ", texto)

    # Remove espaços repetidos.
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# ============================================================
# PERGUNTA
# ============================================================

def validar_pergunta(pergunta: str) -> str:
    """
    Valida e normaliza a pergunta do usuário.
    """

    pergunta = normalizar_texto(pergunta)

    if not pergunta:
        raise PerguntaInvalida(
            "A pergunta não pode estar vazia."
        )

    if len(pergunta) > TAMANHO_MAX_PERGUNTA:
        raise PerguntaInvalida(
            f"Pergunta muito longa "
            f"(máx {TAMANHO_MAX_PERGUNTA} caracteres)."
        )

    return pergunta


# ============================================================
# MODO DA IA
# ============================================================

def validar_modo(modo: str) -> str:
    """
    Garante que somente os modos permitidos sejam utilizados.
    """

    if not isinstance(modo, str):
        raise ModoInvalido(
            "O modo precisa ser texto."
        )

    modo = unicodedata.normalize(
        "NFKC",
        modo
    ).strip().lower()

    if modo not in MODOS_VALIDOS:
        raise ModoInvalido(
            f"Modo inválido: {modo!r}."
        )

    return modo


# ============================================================
# CONTEXTO
# ============================================================

def limitar_contexto(contexto: str) -> str:
    """
    Limita o tamanho do contexto enviado ao modelo.
    """

    if not isinstance(contexto, str):
        raise ContextoInvalido(
            "O contexto precisa ser texto."
        )

    contexto = normalizar_texto(contexto)

    if len(contexto) > TAMANHO_MAX_CONTEXTO:
        return (
            contexto[:TAMANHO_MAX_CONTEXTO]
            + "\n[...contexto truncado...]"
        )

    return contexto


# ============================================================
# FONTES
# ============================================================

def limitar_fontes(fontes: list[dict]) -> list[dict]:
    """
    Limita a quantidade e o tamanho das fontes.
    """

    if not isinstance(fontes, list):
        raise FonteInvalida(
            "As fontes precisam ser uma lista."
        )

    fontes_validas = []

    for fonte in fontes[:MAX_FONTES]:

        if not isinstance(fonte, dict):
            continue

        fonte_processada = {}

        for chave, valor in fonte.items():

            if not isinstance(chave, str):
                continue

            if isinstance(valor, str):
                valor = normalizar_texto(valor)
                valor = valor[:TAMANHO_MAX_FONTE]

            fonte_processada[chave] = valor

        fontes_validas.append(fonte_processada)

    return fontes_validas


# ============================================================
# URL
# ============================================================

def validar_url(url: str) -> bool:
    """
    Valida URLs que poderão ser utilizadas pelo sistema.

    Permite apenas HTTP/HTTPS e bloqueia IPs
    privados, locais, reservados e de loopback.
    """

    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url:
        return False

    try:
        partes = urlparse(url)
    except ValueError:
        return False

    # Somente HTTP e HTTPS.
    if partes.scheme.lower() not in ESQUEMAS_PERMITIDOS:
        return False

    # A URL precisa possuir hostname.
    if not partes.hostname:
        return False

    host = partes.hostname

    # Bloqueia credenciais embutidas na URL.
    if partes.username is not None or partes.password is not None:
        return False

    # Verifica IP literal.
    try:
        ip = ip_address(host)
    except ValueError:
        # É um domínio.
        return True

    # Bloqueia endereços que não devem ser acessados.
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        return False

    return True


# ============================================================
# VALIDAÇÃO DE FONTE
# ============================================================

def validar_fonte(fonte: dict) -> dict:
    """
    Valida uma fonte individual.
    """

    if not isinstance(fonte, dict):
        raise FonteInvalida(
            "A fonte precisa ser um objeto."
        )

    fonte = fonte.copy()

    url = fonte.get("url")

    if url is not None:
        if not validar_url(url):
            raise URLInvalida(
                f"URL inválida ou não permitida: {url!r}"
            )

    # Limita campos textuais.
    for chave, valor in list(fonte.items()):

        if isinstance(valor, str):
            fonte[chave] = normalizar_texto(valor)[
                :TAMANHO_MAX_FONTE
            ]

    return fonte


# ============================================================
# RESPOSTA DA IA
# ============================================================

def validar_resposta_ia(resposta: str) -> str:
    """
    Valida a resposta retornada pelo modelo.
    """

    if not isinstance(resposta, str):
        raise RespostaInvalida(
            "A IA não retornou texto."
        )

    resposta = resposta.strip()

    if not resposta:
        raise RespostaInvalida(
            "A IA não retornou uma resposta válida."
        )

    if len(resposta) > TAMANHO_MAX_RESPOSTA:
        resposta = (
            resposta[:TAMANHO_MAX_RESPOSTA]
            + "\n[...resposta truncada...]"
        )

    return resposta
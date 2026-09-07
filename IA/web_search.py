import logging
import re

from ddgs import DDGS
from ddgs.exceptions import DDGSException

try:
    from .security import normalizar_texto, validar_fonte, validar_pergunta
except ImportError:
    from security import normalizar_texto, validar_fonte, validar_pergunta

logger = logging.getLogger("kalium.web_search")

MAX_RESULTADOS_PADRAO = 5
MAX_RESULTADOS_LIMITE = 10
TAMANHO_MAX_TOTAL = 6000  # soma de todos os trechos combinados, não só cada um
TIMEOUT_BUSCA = 10

# só pra ordenar o que aparece primeiro - nunca decide se uma fonte é confiável,
# isso continua sendo trabalho do validar_fonte()
SUFIXOS_PRIORITARIOS = (
    ".gov", ".gov.br", ".edu", ".edu.br", ".org.br",
    "scielo.br", "scholar.google", "nature.com", "sciencedirect.com",
    "ncbi.nlm.nih.gov", "embrapa.br",
)


def _chave_dedup(url: str) -> str:
    # ignora protocolo, www e barra final pra pegar duplicata disfarçada
    sem_protocolo = re.sub(r"^https?://(www\.)?", "", url.lower())
    return sem_protocolo.rstrip("/")


def _prioridade(url: str) -> int:
    url_lower = url.lower()
    return 0 if any(sufixo in url_lower for sufixo in SUFIXOS_PRIORITARIOS) else 1


def buscar_web(pergunta: str, max_resultados: int = MAX_RESULTADOS_PADRAO) -> list[dict]:
    pergunta = validar_pergunta(pergunta)
    max_resultados = min(max(max_resultados, 1), MAX_RESULTADOS_LIMITE)
    pedidos = min(max_resultados * 3, 30)  # pede mais pra sobrar o que priorizar depois

    resultados = []
    urls_vistas = set()
    tamanho_total = 0

    try:
        with DDGS(timeout=TIMEOUT_BUSCA) as ddgs:
            brutos = ddgs.text(pergunta, max_results=pedidos, region="br-pt")
    except DDGSException:
        # timeout, rate limit etc — loga o real e não deixa detalhe interno vazar
        logger.exception("Falha ao buscar no DuckDuckGo")
        return []

    for r in brutos:
        titulo = normalizar_texto(r.get("title") or "")
        url = (r.get("href") or "").strip()
        trecho = normalizar_texto(r.get("body") or "")

        if not validar_fonte(titulo, url, trecho):
            continue

        chave = _chave_dedup(url)
        if chave in urls_vistas:
            continue

        if tamanho_total + len(trecho) > TAMANHO_MAX_TOTAL:
            continue

        urls_vistas.add(chave)
        tamanho_total += len(trecho)
        resultados.append({"titulo": titulo, "url": url, "trecho": trecho})

    resultados.sort(key=lambda r: _prioridade(r["url"]))
    return resultados[:max_resultados]
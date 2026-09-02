# busca via DuckDuckGo, sem chave de API
# pip install ddgs
from ddgs import DDGS


def buscar_web(pergunta: str, max_resultados: int = 5) -> list[dict]:
    resultados = []
    with DDGS() as ddgs:
        for r in ddgs.text(pergunta, max_results=max_resultados, region="br-pt"):
            resultados.append({
                "titulo": r.get("title", ""),
                "url": r.get("href", ""),
                "trecho": r.get("body", ""),
            })
    return resultados
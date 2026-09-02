def formatar_fontes(resultados: list[dict]) -> list[dict]:
    # versão enxuta dos resultados só com o que o frontend precisa mostrar
    return [
        {"numero": i, "titulo": r["titulo"], "url": r["url"]}
        for i, r in enumerate(resultados, start=1)
    ]
def montar_contexto(resultados: list[dict]) -> str:
    # transforma os resultados da busca num bloco numerado
    # pra ir no prompt e o modelo poder citar [1], [2]...
    if not resultados:
        return "Nenhum resultado de busca encontrado."

    blocos = []
    for i, r in enumerate(resultados, start=1):
        blocos.append(
            f"[{i}] {r['titulo']}\n"
            f"URL: {r['url']}\n"
            f"Trecho: {r['trecho']}\n"
        )
    return "\n".join(blocos)
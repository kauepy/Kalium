import re

TAMANHO_MAX_PERGUNTA = 500


class PerguntaInvalida(Exception):
    pass


def validar_pergunta(pergunta: str) -> str:
    pergunta = pergunta.strip()

    if not pergunta:
        raise PerguntaInvalida("A pergunta não pode estar vazia.")

    if len(pergunta) > TAMANHO_MAX_PERGUNTA:
        raise PerguntaInvalida(f"Pergunta muito longa (máx {TAMANHO_MAX_PERGUNTA} caracteres).")

    pergunta = re.sub(r"[\x00-\x1f\x7f]", "", pergunta)  # tira caractere de controle

    return pergunta
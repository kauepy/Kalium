from .context import montar_contexto
from .model import chamar_modelo
from .prompts import WEB_SYSTEM_PROMPT, montar_prompt_usuario
from .security import validar_pergunta, PerguntaInvalida
from .sources import formatar_fontes
from .web_search import buscar_web


def responder(pergunta: str) -> dict:
    # valida -> busca -> monta contexto -> pergunta pro modelo -> devolve com fontes
    try:
        pergunta = validar_pergunta(pergunta)
    except PerguntaInvalida as e:
        return {"erro": str(e)}

    resultados = buscar_web(pergunta)
    contexto = montar_contexto(resultados)

    mensagens = [
        {"role": "system", "content": WEB_SYSTEM_PROMPT},
        {"role": "user", "content": montar_prompt_usuario(pergunta, contexto)},
    ]

    resposta = chamar_modelo(mensagens)
    fontes = formatar_fontes(resultados)

    return {"resposta": resposta, "fontes": fontes}
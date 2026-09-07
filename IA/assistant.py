import logging

try:
    from .context import montar_contexto
    from .model import chamar_modelo, ErroModelo
    from .prompts import WEB_SYSTEM_PROMPT, montar_prompt_usuario
    from .security import PerguntaInvalida, limitar_contexto, limitar_fontes, validar_pergunta
    from .sources import formatar_fontes
    from .web_search import buscar_web
except ImportError:
    from context import montar_contexto
    from model import chamar_modelo, ErroModelo
    from prompts import WEB_SYSTEM_PROMPT, montar_prompt_usuario
    from security import PerguntaInvalida, limitar_contexto, limitar_fontes, validar_pergunta
    from sources import formatar_fontes
    from web_search import buscar_web

logger = logging.getLogger("kalium.assistant")

# perguntas puramente sociais não precisam gastar uma busca na web
_SAUDACOES = {
    "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
    "obrigado", "obrigada", "valeu", "tchau", "eai", "e ai",
}


def _precisa_pesquisar(pergunta: str) -> bool:
    return pergunta.lower().strip(" .,!?") not in _SAUDACOES


def responder(pergunta: str) -> dict:
    try:
        pergunta = validar_pergunta(pergunta)
    except PerguntaInvalida as e:
        return {"erro": str(e)}

    resultados = buscar_web(pergunta) if _precisa_pesquisar(pergunta) else []
    contexto = limitar_contexto(montar_contexto(resultados))

    mensagens = [
        {"role": "system", "content": WEB_SYSTEM_PROMPT},
        {"role": "user", "content": montar_prompt_usuario(pergunta, contexto)},
    ]

    try:
        resposta = chamar_modelo(mensagens)
    except ErroModelo as e:
        # o usuário nunca vê o motivo técnico, só uma mensagem amigável
        logger.error("Falha ao chamar o modelo: %s", e)
        return {"erro": "Não foi possível gerar uma resposta agora. Tente novamente em instantes."}

    fontes = limitar_fontes(formatar_fontes(resultados))

    return {"resposta": resposta, "fontes": fontes}
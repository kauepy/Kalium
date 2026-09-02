from .model import chamar_modelo


messages = [
    {
        "role": "system",
        "content": (
            "Você é um assistente educacional especializado "
            "exclusivamente em potássio (K) e no ciclo do potássio."
        ),
    },
    {
        "role": "user",
        "content": "O que é o potássio?",
    },
]


try:
    resposta = chamar_modelo(messages)

    print("\n===== RESPOSTA DA IA =====\n")
    print(resposta)

except RuntimeError as error:
    print(f"\nErro: {error}")
"""Prompts do app.

TODO (Pessoa 1): trocar o PROMPT e os CAMPOS_OBRIGATORIOS pelo esquema da ideia do grupo.
Teste o prompt antes (notebook ou `python avaliar.py rodar`) e só depois leve para o app.
"""

# Prompt de sistema contra alucinação (Aula 09 · 3.7): autoriza o modelo a discordar.
SISTEMA = (
    "Você analisa imagens e responde em português. Responda somente com base no que está visível. "
    "Se algo não aparece ou não dá para ler, use null ou \"nao_identificado\" em vez de adivinhar. "
    "Se a pergunta assumir algo que não está na imagem, diga isso explicitamente. Nunca invente."
)

# Esquema de EXEMPLO (genérico), só para o app já rodar.
PROMPT = '''Analise a imagem. Responda APENAS com JSON neste formato:
{"legenda": "uma frase em português",
 "objetos": [{"nome": "string", "quantidade": 0}],
 "texto_visivel": "texto legível na imagem ou null",
 "confianca": "baixa, media ou alta"}'''

CAMPOS_OBRIGATORIOS = ["legenda", "objetos", "texto_visivel", "confianca"]

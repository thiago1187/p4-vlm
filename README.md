# TODO: nome do app

> Este README precisa ser escrito pelo grupo (regra da P4). Os tópicos abaixo são só o roteiro.

## Proposta
Para **TODO usuário**, que precisa **TODO tarefa**, o app recebe **TODO imagem** e devolve **TODO saída**.

## Problema e usuário
TODO: quem usa, qual problema real resolve.

## Por que um VLM (e não só YOLO ou CLIP)
TODO

## Modelo / API
- Modelo: `qwen/qwen3.8-27b` via Groq (TODO: confirmar o que foi usado)
- Prompt de sistema contra alucinação e saída em JSON (`json_mode`): ver `prompts.py`
- Esquema de saída: TODO colar o JSON

## Interface
Streamlit. TODO: justificar a escolha.

## Como rodar
```bash
pip install -r requirements.txt
cp .env.example .env   # e cole sua GROQ_API_KEY no .env
streamlit run app.py
```

## Testes e limitações
TODO: tabela de acurácia por campo (`python avaliar.py acuracia`), pelo menos 2 erros reais do modelo e o que foi feito para reduzir.

## Prints
TODO

## Integrantes
- TODO
- TODO
- TODO

## Declaração de uso de IA
- Código base (`vlm_client.py`, `app.py`, `avaliar.py`) gerado com ajuda do Claude Code, adaptado das funções do notebook da Aula 09.
- TODO: listar o que mais foi gerado com IA.

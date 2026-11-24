"""Cliente do VLM via Groq.

Adaptado de img_para_data_url / perguntar_vlm / extrair_json do notebook da Aula 09 (Parte 3).
A chave vem do .env (local) ou do st.secrets (Streamlit Cloud).
"""
import base64
import io
import json
import os
import re
import time

import groq
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

load_dotenv()

VISION_MODEL = os.getenv("VISION_MODEL", "qwen/qwen3.8-27b")

ULTIMO_USO = None              # tokens da última chamada (útil para mostrar custo)
USAR_PARAMS_RACIOCINIO = True  # vira False sozinho se o modelo não aceitar esses parâmetros
_client = None


def _pegar_chave():
    chave = os.getenv("GROQ_API_KEY")
    if not chave:
        try:
            import streamlit as st
            chave = st.secrets.get("GROQ_API_KEY")
        except Exception:
            chave = None
    if not chave:
        raise RuntimeError("GROQ_API_KEY não encontrada. Copie .env.example para .env e cole sua chave.")
    return chave


def _cliente():
    global _client
    if _client is None:
        _client = Groq(api_key=_pegar_chave())
    return _client


def img_para_data_url(img, lado_max=1024, qualidade=90):
    im = img.convert("RGB")  # PNG com transparência não pode ser salvo como JPEG
    im.thumbnail((lado_max, lado_max))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=qualidade)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def perguntar_vlm(prompt, imagens=(), sistema=None, json_mode=False,
                  max_tokens=600, temperature=0.2, tentativas=5):
    """Envia texto + imagens (0 a 3) ao VLM do Groq e devolve a resposta em texto."""
    global ULTIMO_USO, USAR_PARAMS_RACIOCINIO
    if isinstance(imagens, Image.Image):
        imagens = [imagens]
    conteudo = [{"type": "text", "text": prompt}]
    conteudo += [{"type": "image_url", "image_url": {"url": img_para_data_url(im)}} for im in imagens]
    mensagens = ([{"role": "system", "content": sistema}] if sistema else []) + \
                [{"role": "user", "content": conteudo}]

    kwargs = dict(model=VISION_MODEL, messages=mensagens, max_tokens=max_tokens, temperature=temperature)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for t in range(tentativas):
        extras = dict(reasoning_effort="none", reasoning_format="hidden") if USAR_PARAMS_RACIOCINIO else {}
        try:
            resp = _cliente().chat.completions.create(**kwargs, **extras)
            break
        except groq.BadRequestError as e:
            if extras and "reasoning" in str(e).lower():
                USAR_PARAMS_RACIOCINIO = False
                continue
            raise
        except groq.RateLimitError:
            espera = 20 * (t + 1)
            print(f"  (limite de taxa do plano gratuito: aguardando {espera}s...)")
            time.sleep(espera)
    else:
        raise RuntimeError("Não foi possível obter resposta após várias tentativas (limite de taxa).")

    ULTIMO_USO = resp.usage
    texto = resp.choices[0].message.content or ""
    return re.sub(r"<think>.*?</think>", "", texto, flags=re.S).strip()


def extrair_json(texto):
    """Lê JSON mesmo se vier dentro de ```json ... ```. Levanta ValueError se não for JSON."""
    texto = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    inicio, fim = texto.find("{"), texto.rfind("}")
    return json.loads(texto[inicio:fim + 1])


def campos_faltando(dados, campos):
    """Validação simples: quais campos obrigatórios o modelo não devolveu."""
    return [c for c in campos if c not in dados]

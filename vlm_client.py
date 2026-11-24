import base64
import io
import json
import math
import os
import re
import time
from pathlib import Path

import groq
from dotenv import dotenv_values
from groq import Groq
from PIL import Image, ImageOps


class ErroVLM(RuntimeError):
    pass


def _configuracao(nome, padrao=""):
    valor = os.getenv(nome) or dotenv_values(Path(__file__).with_name(".env")).get(nome)
    if not valor:
        try:
            import streamlit as st
            valor = st.secrets.get(nome)
        except (FileNotFoundError, KeyError):
            pass
    return str(valor or padrao).strip()


VISION_MODEL = _configuracao("VISION_MODEL", "qwen/qwen3.8-27b")

ULTIMO_USO = None
USAR_PARAMS_RACIOCINIO = VISION_MODEL == "qwen/qwen3.8-27b"
_client = None


def _pegar_chave():
    chave = _configuracao("GROQ_API_KEY")
    if not chave or chave == "cole_sua_chave_aqui":
        raise ErroVLM("A chave da Groq não foi configurada. Preencha GROQ_API_KEY no arquivo .env e tente novamente.")
    return chave


def verificar_configuracao():
    _pegar_chave()


def _cliente():
    global _client
    if _client is None:
        _client = Groq(api_key=_pegar_chave(), timeout=30.0, max_retries=0)
    return _client


def img_para_data_url(img, lado_max=1024, qualidade=90):
    im = ImageOps.exif_transpose(img).convert("RGBA")
    im.thumbnail((lado_max, lado_max))
    im = Image.alpha_composite(Image.new("RGBA", im.size, "white"), im).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=qualidade)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")


def perguntar_vlm(prompt, imagens=(), sistema=None, json_mode=False,
                  max_tokens=1800, temperature=0.2, tentativas=3):
    global ULTIMO_USO, USAR_PARAMS_RACIOCINIO
    ULTIMO_USO = None
    if tentativas < 1:
        raise ValueError("É necessária pelo menos uma tentativa.")
    if isinstance(imagens, Image.Image):
        imagens = [imagens]
    conteudo = [{"type": "text", "text": prompt}]
    conteudo += [{"type": "image_url", "image_url": {"url": img_para_data_url(im)}} for im in imagens]
    mensagens = ([{"role": "system", "content": sistema}] if sistema else []) + \
                [{"role": "user", "content": conteudo}]

    kwargs = dict(model=VISION_MODEL, messages=mensagens, max_completion_tokens=max_tokens, temperature=temperature)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    cliente = _cliente()
    for t in range(tentativas):
        extras = dict(reasoning_effort="none", reasoning_format="hidden") if USAR_PARAMS_RACIOCINIO else {}
        try:
            resp = cliente.chat.completions.create(**kwargs, **extras)
            break
        except groq.BadRequestError as e:
            if extras and "reasoning" in str(e).lower():
                USAR_PARAMS_RACIOCINIO = False
                return perguntar_vlm(prompt, imagens, sistema, json_mode, max_tokens, temperature, tentativas - t)
            raise ErroVLM("A Groq recusou a análise. Confira se VISION_MODEL aceita imagens e respostas em JSON.") from e
        except groq.RateLimitError as erro:
            if t == tentativas - 1:
                raise ErroVLM("O limite de uso da Groq foi atingido. Aguarde um pouco antes de tentar novamente.") from None
            espera = 3 * (t + 1)
            retry_after = erro.response.headers.get("retry-after")
            if retry_after is not None:
                try:
                    espera = float(retry_after)
                except ValueError:
                    raise ErroVLM("O limite de uso da Groq foi atingido. Aguarde antes de tentar novamente.") from None
            if not math.isfinite(espera) or espera > 20:
                raise ErroVLM("A Groq pediu uma pausa maior por limite de uso. Aguarde antes de analisar novamente.") from None
            time.sleep(max(1, espera))
        except groq.AuthenticationError:
            raise ErroVLM("A chave da Groq foi recusada. Confira GROQ_API_KEY no .env e reinicie o aplicativo.") from None
        except groq.PermissionDeniedError:
            raise ErroVLM("Esta conta não tem acesso ao modelo. Confira as permissões na Groq.") from None
        except groq.NotFoundError:
            raise ErroVLM("O modelo configurado não foi encontrado. Confira VISION_MODEL no .env e reinicie o aplicativo.") from None
        except groq.APITimeoutError:
            raise ErroVLM("A análise demorou mais que o esperado. Tente novamente em instantes.") from None
        except groq.APIConnectionError:
            raise ErroVLM("Não consegui conectar à Groq. Confira a internet e tente novamente.") from None
        except groq.APIStatusError:
            raise ErroVLM("O serviço de análise está indisponível no momento. Tente novamente em instantes.") from None

    ULTIMO_USO = resp.usage
    if not resp.choices or resp.choices[0].finish_reason == "length":
        raise ErroVLM("A resposta do modelo ficou incompleta. Tente novamente com uma foto mais simples.")
    texto = resp.choices[0].message.content or ""
    texto = re.sub(r"<think>.*?</think>", "", texto, flags=re.S).strip()
    if not texto:
        raise ErroVLM("O modelo não retornou uma análise. Tente outra foto.")
    return texto


def extrair_json(texto):
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.IGNORECASE).strip()
    dados = json.loads(texto)
    if not isinstance(dados, dict):
        raise ValueError("A resposta precisa ser um objeto JSON.")
    return dados


def campos_faltando(dados, campos):
    if not isinstance(dados, dict):
        return list(campos)
    return [c for c in campos if c not in dados]

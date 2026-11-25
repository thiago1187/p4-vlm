import io
import math

from PIL import Image, ImageOps, UnidentifiedImageError

from prompts import CAMPOS_OBRIGATORIOS, SISTEMA, montar_prompt
from vlm_client import extrair_json, perguntar_vlm

LIMITE_IMAGEM_MB = 10


def abrir_imagem(conteudo):
    if not conteudo:
        raise ValueError("O arquivo está vazio. Envie outra foto.")
    if len(conteudo) > LIMITE_IMAGEM_MB * 1024 * 1024:
        raise ValueError(f"A foto deve ter no máximo {LIMITE_IMAGEM_MB} MB.")
    try:
        with Image.open(io.BytesIO(conteudo)) as original:
            if original.format not in {"JPEG", "MPO", "PNG", "WEBP"}:
                raise ValueError("Use uma imagem JPG, PNG ou WebP.")
            if original.width * original.height > 25_000_000:
                raise ValueError("A imagem tem resolução muito alta. Reduza para até 25 megapixels.")
            imagem = ImageOps.exif_transpose(original)
            imagem.thumbnail((1024, 1024))
            rgba = imagem.convert("RGBA")
            fundo = Image.new("RGBA", rgba.size, "white")
            return Image.alpha_composite(fundo, rgba).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as erro:
        raise ValueError("Não consegui abrir essa foto. Confira o arquivo e tente outra imagem.") from erro


def _numero(valor, campo):
    if valor is None:
        return None
    if type(valor) not in (int, float) or not math.isfinite(valor) or valor < 0:
        raise ValueError(f"O campo {campo} deve ser um número não negativo ou null.")
    return round(valor, 1)


def validar_resultado(dados):
    if not isinstance(dados, dict) or set(dados) != set(CAMPOS_OBRIGATORIOS):
        raise ValueError("A resposta não contém o conjunto esperado de campos.")
    if dados["status"] not in ("ok", "parcial", "sem_alimentos", "imagem_inadequada"):
        raise ValueError("O status da análise é inválido.")
    if dados["confianca"] not in ("baixa", "media", "alta"):
        raise ValueError("O nível de confiança é inválido.")
    if not isinstance(dados["observacao"], str) or not dados["observacao"].strip():
        raise ValueError("Faltou a observação sobre a imagem.")
    if not isinstance(dados["nao_identificados"], list) or not all(
        isinstance(item, str) and item.strip() for item in dados["nao_identificados"]
    ):
        raise ValueError("A lista de alimentos não identificados é inválida.")
    if not isinstance(dados["alimentos"], list):
        raise ValueError("O campo alimentos deve ser uma lista.")

    resultado = dict(dados)
    resultado["observacao"] = dados["observacao"].strip()
    resultado["nao_identificados"] = list(dict.fromkeys(item.strip() for item in dados["nao_identificados"]))
    resultado["alimentos"] = []
    total_recebido = _numero(dados["kcal_total"], "kcal_total")
    for item in dados["alimentos"]:
        if not isinstance(item, dict) or set(item) != {"nome", "porcao_g", "kcal"}:
            raise ValueError("Cada alimento precisa de nome, porcao_g e kcal.")
        if not isinstance(item["nome"], str) or not item["nome"].strip():
            raise ValueError("O nome de um alimento está vazio ou inválido.")
        alimento = {
            "nome": item["nome"].strip(),
            "porcao_g": _numero(item["porcao_g"], "porcao_g"),
            "kcal": _numero(item["kcal"], "kcal"),
        }
        if alimento["nome"].lower().replace(" ", "_") in {"nao_identificado", "não_identificado"}:
            alimento.update(nome="nao_identificado", porcao_g=None, kcal=None)
            if not resultado["nao_identificados"]:
                resultado["nao_identificados"].append("Um dos alimentos visíveis não foi reconhecido.")
        resultado["alimentos"].append(alimento)

    if resultado["status"] in {"sem_alimentos", "imagem_inadequada"}:
        if resultado["alimentos"] or resultado["nao_identificados"] or total_recebido is not None:
            raise ValueError("A resposta inclui calorias ou alimentos em uma imagem sem análise possível.")
        resultado.update(kcal_total=None, confianca="baixa")
        return resultado

    if not resultado["alimentos"] and not resultado["nao_identificados"]:
        raise ValueError("A resposta indica uma refeição, mas não descreve nenhum alimento.")

    calorias_completas = bool(resultado["alimentos"]) and not resultado["nao_identificados"] and all(
        item["kcal"] is not None for item in resultado["alimentos"]
    )
    total = round(math.fsum(item["kcal"] for item in resultado["alimentos"]), 1) if calorias_completas else None
    resultado["kcal_total"] = total
    if total != total_recebido:
        ajuste = "O total foi recalculado pela soma dos itens." if total is not None else "O total não foi calculado porque faltam estimativas de alimentos."
        resultado["observacao"] += f" {ajuste}"
    if not calorias_completas or any(item["porcao_g"] is None for item in resultado["alimentos"]):
        resultado.update(status="parcial", confianca="baixa")
    return resultado


def analisar_prato(imagem, informacao_extra=""):
    resposta = perguntar_vlm(montar_prompt(informacao_extra), imagem, sistema=SISTEMA, json_mode=True)
    try:
        return validar_resultado(extrair_json(resposta))
    except (ValueError, TypeError, OverflowError) as erro:
        raise ValueError("O modelo devolveu uma resposta incompleta ou fora do formato esperado. Tente analisar novamente.") from erro

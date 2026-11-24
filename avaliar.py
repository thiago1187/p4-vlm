"""Avaliação (Parte 4 da P4).

1) Coloque as imagens de teste em exemplos/ (mínimo 5).
2) python avaliar.py rodar     -> roda o VLM em cada imagem e cria avaliacao.csv
3) Abra avaliacao.csv e preencha à mão as colunas "esperado" e "acertou" (1 ou 0).
4) python avaliar.py acuracia  -> mostra a acurácia por campo
"""
import json
import sys
from pathlib import Path

import pandas as pd
from PIL import Image

CSV = Path("avaliacao.csv")
PASTA = Path("exemplos")


def rodar():
    from prompts import CAMPOS_OBRIGATORIOS, PROMPT, SISTEMA
    from vlm_client import extrair_json, perguntar_vlm

    if CSV.exists() and len(pd.read_csv(CSV)) > 0:
        sys.exit("avaliacao.csv já tem dados. Apague ou renomeie antes de rodar de novo.")
    linhas = []
    for caminho in sorted(PASTA.glob("*")):
        if caminho.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        print("Analisando", caminho.name)
        dados = extrair_json(perguntar_vlm(PROMPT, Image.open(caminho), sistema=SISTEMA, json_mode=True))
        for campo in CAMPOS_OBRIGATORIOS:
            linhas.append({"imagem": caminho.name, "campo": campo,
                           "vlm": json.dumps(dados.get(campo), ensure_ascii=False),
                           "esperado": "", "acertou": ""})
    pd.DataFrame(linhas).to_csv(CSV, index=False)
    print(f"{CSV} criado com {len(linhas)} linhas. Agora preencha 'esperado' e 'acertou'.")


def acuracia():
    df = pd.read_csv(CSV)
    df["acertou"] = pd.to_numeric(df["acertou"], errors="coerce")
    tab = df.groupby("campo")["acertou"].agg(acertos="sum", imagens="count", acuracia="mean")
    print(tab.round(2))


if __name__ == "__main__":
    {"rodar": rodar, "acuracia": acuracia}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()

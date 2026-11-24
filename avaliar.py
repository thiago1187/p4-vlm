import json
import sys
import time
from pathlib import Path

import pandas as pd

AJUDA = """Avaliação (Parte 4 da P4).

1) Coloque as fotos de teste em exemplos/ (mínimo 5).
2) python avaliar.py rodar     -> analisa cada foto com o mesmo fluxo do app e cria avaliacao.csv
3) Abra avaliacao.csv e preencha à mão as colunas "esperado" e "acertou" (1 ou 0).
   - alimentos: acertou se reconheceu os principais itens do prato
   - kcal_total: acertou se ficou até ±30% do valor de referência
4) python avaliar.py acuracia  -> mostra a acurácia por campo
"""

CSV = Path("avaliacao.csv")
PASTA = Path("exemplos")
CAMPOS_AVALIADOS = ["alimentos", "kcal_total"]
PAUSA_S = 20  # evita o limite de tokens por minuto do plano gratuito


def analisar_com_pausa(imagem):
    from analise import analisar_prato
    from vlm_client import ErroVLM

    try:
        return analisar_prato(imagem)
    except ErroVLM as erro:
        if "limite" not in str(erro).lower():
            raise
        print("  limite de uso atingido, esperando 60 s e tentando de novo...")
        time.sleep(60)
        return analisar_prato(imagem)


def rodar():
    from analise import abrir_imagem

    if CSV.exists() and len(pd.read_csv(CSV)) > 0:
        sys.exit("avaliacao.csv já tem dados. Apague ou renomeie antes de rodar de novo.")
    fotos = [c for c in sorted(PASTA.glob("*")) if c.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    linhas = []
    for i, caminho in enumerate(fotos):
        if i:
            time.sleep(PAUSA_S)
        print(f"[{i + 1}/{len(fotos)}] Analisando {caminho.name}")
        try:
            dados = analisar_com_pausa(abrir_imagem(caminho.read_bytes()))
            valores = {
                "alimentos": json.dumps([a["nome"] for a in dados["alimentos"]], ensure_ascii=False),
                "kcal_total": dados["kcal_total"],
            }
        except Exception as erro:  # o erro também é um resultado: fica registrado no CSV
            valores = {campo: f"ERRO: {erro}" for campo in CAMPOS_AVALIADOS}
        for campo in CAMPOS_AVALIADOS:
            linhas.append({"imagem": caminho.name, "campo": campo, "vlm": valores[campo],
                           "esperado": "", "acertou": ""})
    pd.DataFrame(linhas).to_csv(CSV, index=False)
    print(f"{CSV} criado com {len(linhas)} linhas. Agora preencha 'esperado' e 'acertou'.")


def acuracia():
    df = pd.read_csv(CSV)
    df["acertou"] = pd.to_numeric(df["acertou"], errors="coerce")
    tab = df.groupby("campo")["acertou"].agg(acertos="sum", imagens="count", acuracia="mean")
    print(tab.round(2))


if __name__ == "__main__":
    {"rodar": rodar, "acuracia": acuracia}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(AJUDA))()

import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from analise import LIMITE_IMAGEM_MB, abrir_imagem, analisar_prato
from vlm_client import ErroVLM, VISION_MODEL, verificar_configuracao


def formatar_numero(valor):
    return f"{valor:,.1f}".rstrip("0").rstrip(".").replace(",", "_").replace(".", ",").replace("_", ".")


def mostrar_resultado(dados, chave):
    if dados["status"] in {"sem_alimentos", "imagem_inadequada"}:
        st.warning("Não encontrei alimentos para analisar." if dados["status"] == "sem_alimentos" else "Não foi possível analisar essa foto.")
        st.write(dados["observacao"])
    else:
        total, confianca = st.columns([2, 1])
        with total:
            valor = f"≈ {formatar_numero(dados['kcal_total'])} kcal" if dados["kcal_total"] is not None else "Não estimado"
            st.metric("Total estimado", valor, border=True)
        with confianca:
            st.metric("Confiança da análise", {"baixa": "Baixa", "media": "Média", "alta": "Alta"}[dados["confianca"]], border=True)
        st.caption("A confiança é informada pelo modelo e não representa uma taxa de acerto medida.")

        if dados["alimentos"]:
            tabela = pd.DataFrame([
                {
                    "Alimento": "Não identificado" if item["nome"] == "nao_identificado" else item["nome"],
                    "Porção estimada (g)": formatar_numero(item["porcao_g"]) if item["porcao_g"] is not None else "Não estimada",
                    "Calorias estimadas (kcal)": formatar_numero(item["kcal"]) if item["kcal"] is not None else "Não estimadas",
                }
                for item in dados["alimentos"]
            ])
            st.dataframe(tabela, hide_index=True, width="stretch")

        if dados["status"] == "parcial":
            st.warning("A análise ficou parcial: há alimentos ou quantidades que não foi possível estimar.")
        if dados["kcal_total"] is None:
            conhecidos = [item["kcal"] for item in dados["alimentos"] if item["kcal"] is not None]
            if conhecidos:
                st.caption(f"Subtotal dos itens com estimativa: ≈ {formatar_numero(sum(conhecidos))} kcal. Esse valor não representa o prato inteiro.")
        if dados["nao_identificados"]:
            st.markdown("**O que não foi identificado**")
            for item in dados["nao_identificados"]:
                st.write(f"• {item}")
        st.markdown("**Sobre esta estimativa**")
        st.write(dados["observacao"])

    with st.expander("Ver detalhes"):
        st.caption(f"Modelo: {VISION_MODEL} · Groq")
        st.json(dados)
        st.download_button(
            "Baixar resultado em JSON", json.dumps(dados, ensure_ascii=False, indent=2),
            file_name="analise-do-prato.json", mime="application/json", key=f"json_{chave}",
        )


st.set_page_config(page_title="Prato em Foco", page_icon="🍽️", layout="centered")
st.title("🍽️ Prato em Foco")
st.write("Uma foto do seu prato, uma estimativa do que você está comendo.")
st.caption("Identifique os alimentos e tenha uma noção das porções e calorias, sem registrar cada item manualmente.")

st.session_state.setdefault("historico", [])
st.session_state.setdefault("resultado_atual", None)
st.session_state.setdefault("entrada_atual", None)

erro_configuracao = None
try:
    verificar_configuracao()
except ErroVLM as erro:
    erro_configuracao = str(erro)
    st.error(erro_configuracao)

imagem = None
conteudo = b""
with st.container(border=True):
    foto, contexto = st.columns([1.1, 1], gap="medium")
    with foto:
        st.subheader("Seu prato")
        fonte = st.radio("Como enviar a foto?", ["Enviar arquivo", "Usar câmera"], horizontal=True)
        if fonte == "Enviar arquivo":
            arquivo = st.file_uploader(
                "Escolha uma foto", type=["jpg", "jpeg", "png", "webp"],
                max_upload_size=LIMITE_IMAGEM_MB, key="foto_arquivo",
            )
        else:
            arquivo = st.camera_input("Tire uma foto do prato", key="foto_camera")
        if arquivo is not None:
            conteudo = arquivo.getvalue()
            try:
                imagem = abrir_imagem(conteudo)
                st.image(imagem, caption="Foto selecionada", width="stretch")
            except ValueError as erro:
                st.error(str(erro))

    with contexto:
        st.subheader("Algum detalhe?")
        informacao_extra = st.text_area(
            "Informação extra (opcional)",
            placeholder="Ex.: o arroz é integral, o frango foi frito ou comi só metade.",
            max_chars=1000, height=140, key="informacao_extra",
        )
        st.caption("Informe o preparo ou a quantidade consumida. Isso ajuda a interpretar o que aparece na foto.")
        st.caption("Para uma foto melhor: mostre o prato inteiro, com boa luz, e evite cobrir os alimentos.")

    analisar = st.button("Analisar prato", type="primary", width="stretch", disabled=imagem is None or erro_configuracao is not None, key="analisar")
    st.caption("Ao analisar, a foto e a informação extra são enviadas à Groq para processamento.")

entrada = hashlib.sha256(conteudo + informacao_extra.strip().encode()).hexdigest() if imagem is not None else None
if entrada != st.session_state.entrada_atual:
    st.session_state.entrada_atual = entrada
    st.session_state.resultado_atual = None

if analisar and imagem is not None:
    st.session_state.resultado_atual = None
    with st.spinner("Identificando os alimentos e estimando as calorias..."):
        try:
            dados = analisar_prato(imagem, informacao_extra)
        except (ErroVLM, ValueError) as erro:
            st.error(str(erro))
        else:
            momento = datetime.now(ZoneInfo("America/Recife")).strftime("%d/%m · %H:%M:%S")
            registro = {
                "imagem": getattr(arquivo, "name", "Foto da câmera"),
                "momento": momento,
                "informacao_extra": informacao_extra.strip(),
                "resultado": dados,
            }
            st.session_state.resultado_atual = registro
            st.session_state.historico.append(registro)
            st.session_state.historico = st.session_state.historico[-10:]

if st.session_state.resultado_atual:
    st.subheader("Análise do prato")
    mostrar_resultado(st.session_state.resultado_atual["resultado"], "atual")
elif imagem is None and arquivo is None:
    st.info("Envie uma foto ou use a câmera para começar.")

st.info("Os valores são aproximados e não substituem a avaliação de um nutricionista. A foto não revela o peso exato nem todos os ingredientes do preparo.")

if st.session_state.historico:
    st.divider()
    titulo, limpar = st.columns([3, 1])
    titulo.subheader("Histórico da sessão")
    if limpar.button("Limpar histórico", key="limpar_historico"):
        st.session_state.historico = []
        st.session_state.resultado_atual = None
        st.rerun()
    st.caption("Até 10 análises ficam disponíveis enquanto esta sessão estiver aberta.")
    for indice, registro in enumerate(reversed(st.session_state.historico)):
        with st.expander(f"{registro['momento']} · {registro['imagem']}"):
            if registro["informacao_extra"]:
                st.write("Informação fornecida:", registro["informacao_extra"])
            mostrar_resultado(registro["resultado"], f"historico_{indice}")

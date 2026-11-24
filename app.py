"""Interface Streamlit. Rodar com: streamlit run app.py

TODO (Pessoa 2): nome do app, mostrar o resultado de forma legível (não só o JSON cru).
"""
import streamlit as st
from PIL import Image

from prompts import CAMPOS_OBRIGATORIOS, PROMPT, SISTEMA
from vlm_client import VISION_MODEL, campos_faltando, extrair_json, perguntar_vlm

st.set_page_config(page_title="P4 · App com VLM", page_icon="👁️")
st.title("P4 · App com VLM")
st.caption(f"Modelo: `{VISION_MODEL}` via Groq")

if "historico" not in st.session_state:
    st.session_state.historico = []

fonte = st.radio("Imagem", ["Enviar arquivo", "Câmera"], horizontal=True)
if fonte == "Enviar arquivo":
    arquivo = st.file_uploader("Envie uma imagem", type=["jpg", "jpeg", "png", "webp"])
else:
    arquivo = st.camera_input("Tire uma foto")

with st.expander("Ver prompt enviado ao modelo"):
    st.markdown("**Sistema**")
    st.code(SISTEMA, language=None)
    st.markdown("**Prompt + esquema JSON**")
    st.code(PROMPT, language="json")

if arquivo:
    img = Image.open(arquivo)
    st.image(img)

    if st.button("Analisar", type="primary"):
        with st.spinner("Consultando o VLM..."):
            try:
                resposta = perguntar_vlm(PROMPT, img, sistema=SISTEMA, json_mode=True)
            except Exception as e:
                st.error(f"Erro ao chamar a API: {e}")
                st.stop()

        try:
            dados = extrair_json(resposta)
        except ValueError:
            st.error("O modelo não devolveu um JSON válido. Tente de novo.")
            st.code(resposta, language=None)
            st.stop()

        faltando = campos_faltando(dados, CAMPOS_OBRIGATORIOS)
        if faltando:
            st.warning(f"Campos ausentes na resposta: {', '.join(faltando)}")

        st.subheader("Resultado")
        st.json(dados)
        st.session_state.historico.append({"imagem": getattr(arquivo, "name", "camera"), "resultado": dados})

if st.session_state.historico:
    st.divider()
    st.subheader("Histórico desta sessão")
    for item in reversed(st.session_state.historico):
        with st.expander(item["imagem"]):
            st.json(item["resultado"])

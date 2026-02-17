import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link direto para a sua foto do pôr do sol
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Estilo para colocar a foto no fundo e criar a caixa branca
st.markdown(f"""
<style>
.stApp {{
    background-image: url("{img}");
    background-size: cover;
    background-position: center;
}}
.stForm {{
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 10px;
}}
h1 {{
    color: white;
    text-shadow: 2px 2px 4px #000000;
}}
</style>
""", unsafe_content_allowed=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form("busca"):
        texto = st.text_input("Digite em Português:")
        btn = st.form_submit_button("🔍 PESQUISAR")

    if btn and texto:
        res = df[df['BUSCA'] == normalizar(texto)]
        if not res.empty:
            tic = res['TICUNA'].values[0]
            st.info(f"Português: {res['PORTUGUES'].values[0]}")
            st.success(f"### Ticuna: {tic}")
            gTTS(tic, lang='pt-br').save("a.mp3")
            st.audio("a.mp3")
        else:
            st.error("Palavra não encontrada.")
except Exception as e:
    st.error("Erro ao carregar a planilha.")

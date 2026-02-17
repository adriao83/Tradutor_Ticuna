import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link direto para sua imagem
img_url = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Estilo corrigido para evitar o erro TypeError
estilo = """
<style>
.stApp {{
    background-image: url("{0}");
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
    text-shadow: 2px 2px #000;
}}
</style>
""".format(img_url)

st.markdown(estilo, unsafe_content_allowed=True)

def limpar(txt):
    return re.sub(r'[^a-zA-Z0-9]', '', str(txt)).lower() if pd.notna(txt) else ""

st.title("🏹 Tradutor Ticuna v0.1")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(limpar)

    with st.form("busca"):
        palavra = st.text_input("Digite em Português:")
        enviar = st.form_submit_button("🔍 PESQUISAR")

    if enviar and palavra:
        res = df[df['BUSCA'] == limpar(palavra)]
        if not res.empty:
            ticuna_res = res['TICUNA'].values[0]
            st.info(f"Português: {res['PORTUGUES'].values[0]}")
            st.success(f"### Ticuna: {ticuna_res}")
            
            tts = gTTS(ticuna_res, lang='pt-br')
            tts.save("audio.mp3")
            st.audio("audio.mp3")
        else:
            st.error("Palavra não encontrada.")
except Exception as e:
    st.error("Erro ao carregar a planilha Tradutor_Ticuna.xlsx")

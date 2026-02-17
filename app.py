import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link limpo da sua imagem
img_url = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Estilo CSS sem espaços invisíveis
st.markdown(f"""
<style>
.stApp {{
    background-image: url("{img_url}");
    background-attachment: fixed;
    background-size: cover;
    background-position: center;
}}
.stForm {{
    background-color: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 15px;
    border: 2px solid #2e7d32;
}}
h1 {{
    color: white;
    text-shadow: 2px 2px 4px #000000;
    text-align: center;
    background-color: rgba(0, 0, 0, 0.4);
    padding: 10px;
    border-radius: 10px;
}}
</style>
""", unsafe_content_allowed=True)

def normalizar(texto):
    if pd.isna(texto): return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

st.title("🏹 Tradutor Ticuna v0.1")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['PORT_BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form(key="busca_tradutor"):
        palavra_usuario = st.text_input("Digite em Português:")
        submit_button = st.form_submit_button(label="🔍 PESQUISAR TRADUÇÃO")

    if submit_button:
        if palavra_usuario:
            busca = normalizar(palavra_usuario)
            resultado = df[df['PORT_BUSCA'] == busca]
            if not resultado.empty:
                ticuna = resultado['TICUNA'].values[0]
                port_orig = resultado['PORTUGUES'].values[0]
                st.info(f"**Português:** {port_orig}")
                st.success(f"### **Ticuna:** {ticuna}")
                tts = gTTS(text=ticuna, lang='pt-br')
                tts.save("audio.mp3")
                st.audio("audio.mp3")
            else:
                st.error("Palavra não encontrada.")
        else:
            st.warning("Digite uma palavra.")
except Exception as e:
    st.error("Erro ao carregar os dados.")

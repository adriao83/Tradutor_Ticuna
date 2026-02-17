import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link da sua foto de fundo
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# O segredo está no nome: unsafe_allow_html=True
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    .stForm {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}
    h1 {{
        color: white;
        text-shadow: 2px 2px 5px #000;
        text-align: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form("tradutor_form"):
        texto = st.text_input("Digite em Português:")
        if st.form_submit_button("🔍 TRADUZIR"):
            if texto:
                resultado = df[df['BUSCA'] == normalizar(texto)]
                if not resultado.empty:
                    ticuna = resultado['TICUNA'].values[0]
                    st.success(f"### Ticuna: {ticuna}")
                    
                    # Gera e toca o áudio
                    tts = gTTS(text=ticuna, lang='pt-br')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                else:
                    st.error("Palavra não encontrada.")
            else:
                st.warning("Por favor, digite uma palavra.")

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique a planilha no GitHub.")

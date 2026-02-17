import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
import os

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS AJUSTADO: REMOVIDA A CAIXA EXTRA E LUPA REPOSICIONADA
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    .texto-fixo-branco, h1, h3 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000000, 0px 0px 5px #000000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    .resultado-traducao {{
        color: white !important;
        text-shadow: 2px 2px 15px #000000, -2px -2px 15px #000000, 0px 0px 20px #000000 !important;
        font-size: 34px !important;
        text-align: center;
        padding: 20px;
        font-weight: 900 !important;
    }}

    /* BARRA DE TEXTO PADRÃO (Aumentei o padding na direita para a lupa) */
    .stTextInput input {{
        height: 50px !important;
        border-radius: 25px !important;
        padding-right: 55px !important;
        font-size: 18px !important;
    }}

    /* POSICIONAMENTO DA LUPA - ABAIXADA UM POUCO (margin-top ajustado) */
    div[data-testid="stVerticalBlock"] > div:has(button) {{
        position: absolute;
        right: 25px;
        margin-top: -42px; /* Abaixei de -46px para -42px para alinhar melhor */
        z-index: 999;
    }}

    /* ESTILO DA LUPA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 35px !important;
        box-shadow: none !important;
        filter: drop-shadow(2px 3px 4px rgba(0,0,0,0.4)) !important;
        padding: 0 !important;
    }}

    small {{ display: none !important; }}
    .stAlert {{ background: transparent !important; border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.markdown('<p class="texto-fixo-branco">Erro ao carregar planilha.</p>', unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# Interface limpa sem o container extra
texto_input = st.text_input("", placeholder="Pesquise uma palavra...", label_visibility="collapsed")
submit_botao = st.button("🔍")

# LÓGICA DE BUSCA
if submit_botao or (texto_input != ""):
    if texto_input:
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=trad, lang='pt-br')
                tts.save("voz_trad.mp3")
                st.audio("voz_trad.mp3", autoplay=True)
            except:
                pass
        elif submit_botao:
            st.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_input}" não foi encontrada.</p>', unsafe_allow_html=True)

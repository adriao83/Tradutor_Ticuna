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

# CSS REFINADO: LUPA GRANDE, COM SOMBRA E DENTRO DA BARRA
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
        text-shadow: 2px 2px 10px #000000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    .resultado-traducao {{
        color: white !important;
        text-shadow: 2px 2px 15px #000000 !important;
        font-size: 34px !important;
        text-align: center;
        padding: 20px;
        font-weight: 900 !important;
    }}

    /* CAIXA BRANCA ESTILO GOOGLE */
    .search-container {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 10px 25px;
        border-radius: 35px;
        border: 1px solid #dfe1e5;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}

    /* ESTILO DA BARRA DE TEXTO */
    .stTextInput input {{
        border: none !important;
        background: transparent !important;
        font-size: 20px !important;
        height: 55px !important;
        box-shadow: none !important;
    }}
    
    /* ESTILO DA LUPA: GRANDE E COM SOMBRA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 40px !important; /* Lupa bem grande */
        padding: 0 !important;
        margin-left: 10px !important;
        box-shadow: none !important;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.5)) !important; /* Sombra forte */
        transition: transform 0.2s;
    }}

    .stButton button:hover {{ transform: scale(1.1); }}
    
    /* Limpeza geral */
    small {{ display: none !important; }}
    [data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.write("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# BARRA DE BUSCA
with st.container():
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        texto_input = st.text_input("", placeholder="Pesquise uma palavra...", label_visibility="collapsed")
    with col2:
        submit_botao = st.button("🔍")

# LÓGICA
if submit_botao or (texto_input != ""):
    if texto_input:
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            tts = gTTS(text=trad, lang='pt-br')
            tts.save("voz_trad.mp3")
            st.audio("voz_trad.mp3", autoplay=True)
        elif submit_botao:
            st.markdown(f'<p class="texto-fixo-branco">Palavra não encontrada.</p>', unsafe_allow_html=True)

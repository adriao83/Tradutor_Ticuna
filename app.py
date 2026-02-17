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

# CSS PARA ENCAIXAR A LUPA DENTRO DA BARRA (MODELO GOOGLE)
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

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px;
        position: relative;
    }}

    /* BARRA DE TEXTO ESTILO GOOGLE */
    .stTextInput input {{
        padding-right: 50px !important; /* Espaço para a lupa */
        height: 50px !important;
        border-radius: 25px !important;
        border: 1px solid #dfe1e5 !important;
        font-size: 16px !important;
    }}
    
    .stTextInput input:focus {{
        box-shadow: 0 1px 6px rgba(32,33,36,0.28) !important;
        border-color: rgba(223,225,229,0) !important;
    }}

    /* POSICIONAMENTO DA LUPA - FIXO DENTRO DO INPUT */
    div[data-testid="stFormSubmitButton"] {{
        position: absolute;
        right: 40px;
        /* A mágica para centralizar verticalmente independente da tela */
        top: 68px; 
        z-index: 1000;
    }}

    /* ESTILO DO BOTÃO DA LUPA */
    div[data-testid="stFormSubmitButton"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #4285F4 !important; /* Azul Google */
        font-size: 24px !important;
        padding: 0 !important;
        width: auto !important;
    }}

    /* Limpeza de elementos extras do Streamlit que fazem a lupa sumir */
    [data-testid="stFormSubmitButton"] p {{ display: none !important; }}
    .stForm [data-testid="stVerticalBlock"] > div {{ border: none !important; }}

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

# --- ÁREA DE BUSCA ---
st.markdown("---")
with st.form("form_digitar"):
    st.markdown("### Digite para Traduzir:")
    
    texto_input = st.text_input("", placeholder="Pesquise uma palavra...", label_visibility="collapsed")
    
    # A lupa que será movida para dentro
    submit_botao = st.form_submit_button("🔍")

# LÓGICA DE BUSCA
if submit_botao and texto_input:
    t_norm = normalizar(texto_input)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        
        tts = gTTS(text=trad, lang='pt-br')
        tts.save("voz_trad.mp3")
        st.audio("voz_trad.mp3", autoplay=True)
    else:
        st.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_input}" não foi encontrada.</p>', unsafe_allow_html=True)

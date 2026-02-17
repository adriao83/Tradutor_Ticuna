import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS PARA LIMPAR CAMADAS SOBREPOSTAS E CENTRALIZAR O TEXTO
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

    /* LIMPANDO AS CAMADAS DA CAIXA DE TEXTO */
    [data-testid="stWidgetLabel"] {{ display: none !important; }} /* Remove o label invisível */
    
    .stTextInput {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important; /* Altura da caixa */
    }}

    .stTextInput input {{
        height: 55px !important; /* Mesma altura da div pai */
        background-color: transparent !important;
        border: none !important;
        padding: 0px 60px 0px 20px !important; /* Sem padding no topo/baixo para não empurrar */
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important; /* Centraliza o texto verticalmente */
        line-height: 55px !important; /* Alinha a linha do texto ao centro */
    }}

    /* ESCONDE AS INSTRUÇÕES "PRESS ENTER" */
    [data-testid="InputInstructions"] {{
        display: none !important;
    }}

    /* LUPA POSICIONADA DENTRO DA BARRA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 40px !important;
        color: black !important;
        padding: 0 !important;
        margin-top: -55px !important; /* Ajustado para a nova altura de 55px */
        margin-left: -65px !important; 
        filter: drop-shadow(2px 4px 5px rgba(0,0,0,0.4)) !important;
        z-index: 10;
    }}

    [data-testid="column"] {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    small {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.write("Erro na planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# ESTRUTURA DE COLUNAS
col_main, col_btn = st.columns([0.85, 0.15])

with col_main:
    texto_input = st.text_input("", placeholder="Pesquise uma palavra...", label_visibility="collapsed")

with col_btn:
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

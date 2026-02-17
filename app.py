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

# CSS PARA ENCAIXAR A LUPA DENTRO DA BARRA DE TEXTO (ESTILO GOOGLE)
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
        display: flex;
        flex-direction: column;
    }}

    /* CAIXA DE TEXTO */
    .stTextInput input {{
        padding-right: 45px !important; /* Abre espaço para a lupa */
        height: 45px !important;
        border: 1px solid red !important; /* Borda vermelha conforme sua imagem */
        border-radius: 25px !important;
    }}

    /* --- ALINHAMENTO DA LUPA ESTILO GOOGLE --- */
    div[data-testid="stFormSubmitButton"] {{
        position: absolute;
        right: 40px; /* Ajusta para ficar dentro da borda direita */
        margin-top: -46px; /* Sobe o botão para dentro da linha do input */
        z-index: 1000;
    }}

    /* Estilo do botão para ser invisível e sobrar só o ícone */
    div[data-testid="stFormSubmitButton"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #4285F4 !important; /* Azul estilo Google */
        font-size: 20px !important;
        padding: 0 !important;
    }}
    
    /* Remove textos automáticos do Streamlit que podem atrapalhar */
    [data-testid="stFormSubmitButton"] p {{ display: none !important; }}

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
    st.markdown('<p class="texto-fixo-branco">Erro ao carregar planilha no GitHub.</p>', unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- ÁREA DE BUSCA ---
st.markdown("---")
with st.form("form_digitar"):
    st.markdown("### Digite para Traduzir:")
    
    texto_input = st.text_input("", placeholder="Ex: Capivara", label_visibility="collapsed")
    
    # O botão da lupa que o CSS vai "puxar" para dentro da barra acima
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

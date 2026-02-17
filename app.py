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

# CSS REFINADO PARA O MODELO GOOGLE
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

    /* CAIXA BRANCA PRINCIPAL */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 20px; 
        border-radius: 30px; 
        border: 1px solid #dfe1e5 !important;
    }}

    /* ESTILO DA BARRA DE TEXTO */
    .stTextInput input {{
        border: none !important;
        background: transparent !important;
        font-size: 18px !important;
        height: 50px !important;
    }}
    
    /* ESTILO DO BOTÃO DA LUPA AUMENTADO E COM SOMBRA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 35px !important; /* Tamanho aumentado */
        padding: 0 !important;
        margin-top: 0px !important;
        box-shadow: none !important;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.4)) !important; /* Sombreamento para destaque */
    }}

    /* Centralização da lupa na coluna */
    [data-testid="column"] {{
        display: flex;
        align-items: center;
        justify-content: center;
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

# --- AREA DE TRADUÇÃO MODELO GOOGLE ---
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        texto_input = st.text_input("", placeholder="Pesquise no Tradutor Ticuna...", label_visibility="collapsed")
    
    with col2:
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

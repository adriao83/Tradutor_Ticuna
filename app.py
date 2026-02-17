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

# CSS PARA TRAVAR A LUPA DENTRO DA BARRA COM CONTORNO VERMELHO
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

    /* ESTRUTURA DA BARRA DE BUSCA */
    .search-box {{
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid red !important; /* CONTORNO VERMELHO PEDIDO */
        border-radius: 30px;
        padding: 5px 20px;
        display: flex;
        align-items: center;
        position: relative;
    }}

    /* AJUSTE DO CAMPO DE TEXTO */
    .stTextInput input {{
        border: none !important;
        background: transparent !important;
        font-size: 18px !important;
        height: 50px !important;
        padding-right: 60px !important; /* Espaço para a lupa */
        box-shadow: none !important;
    }}
    
    /* POSICIONAMENTO DA LUPA DENTRO DA CAIXA */
    div.element-container:has(button) {{
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 999;
        width: auto !important;
    }}

    /* ESTILO DA LUPA AUMENTADA E COM SOMBRA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 40px !important; /* Tamanho aumentado conforme pedido */
        padding: 0 !important;
        color: #444 !important;
        box-shadow: none !important;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.6)) !important; /* Sombreamento forte para destaque */
    }}

    .stButton button:hover {{ color: red !important; }}

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

# --- AREA DE BUSCA UNIFICADA ---
with st.container():
    # Esta div "search-box" no Markdown garante que os elementos fiquem presos juntos
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    
    col_txt, col_btn = st.columns([0.88, 0.12])
    
    with col_txt:
        texto_input = st.text_input("", placeholder="Pesquise no Tradutor Ticuna...", label_visibility="collapsed")
    
    with col_btn:
        submit_botao = st.button("🔍")
    
    st.markdown('</div>', unsafe_allow_html=True)

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

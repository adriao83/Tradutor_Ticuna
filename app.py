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

# CSS PARA FORÇAR A LUPA DENTRO DA BARRA
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

    /* A CAIXA QUE VOCÊ PEDIU COM CONTORNO VERMELHO */
    .custom-search-bar {{
        display: flex;
        align-items: center;
        background-color: white;
        border: 2px solid red !important;
        border-radius: 30px;
        padding: 5px 15px;
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* ESTILO DO INPUT (SEM BORDAS DO STREAMLIT) */
    .stTextInput div[data-baseweb="input"] {{
        background-color: transparent !important;
        border: none !important;
    }}
    
    .stTextInput input {{
        background-color: transparent !important;
        border: none !important;
        font-size: 20px !important;
        color: black !important;
    }}

    /* BOTÃO DA LUPA REALMENTE DENTRO E GRANDE */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 40px !important;
        color: black !important;
        padding: 0 !important;
        margin-left: -50px !important; /* Puxa a lupa para dentro da área branca */
        filter: drop-shadow(2px 4px 5px rgba(0,0,0,0.4)) !important;
        z-index: 10;
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

# ESTRUTURA UNIFICADA
col_main, col_btn = st.columns([0.9, 0.1])

with col_main:
    # A borda vermelha agora envolve o input e a lupa juntos
    st.markdown('<div class="custom-search-bar">', unsafe_allow_html=True)
    texto_input = st.text_input("", placeholder="Pesquise uma palavra...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col_btn:
    # A lupa agora aparece "por cima" do final do input
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

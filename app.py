import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

if 'texto' not in st.session_state:
    st.session_state.texto = ""

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS CORRIGIDO COM CHAVES DUPLAS
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* BARRA BRANCA */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
    }}

    /* ESTILO BRUTO PARA OS BOTÕES - SEM CAIXA, SEM BORDA, SEM FUNDO */
    div[data-testid="stVerticalBlock"] > div:has(button) {{
        background: transparent !important;
        border: none !important;
    }}

    /* A LUPA - AJUSTE AQUI */
    button[key="lupa_btn"], [data-testid="baseButton-secondary"]:has(div:contains("🔍")) {{
        position: fixed !important;
        top: 255px !important;    /* <--- MUDE ESSE PARA SUBIR/DESCER */
        left: 50% !important;
        margin-left: 210px !important; /* <--- MUDE ESSE PARA DIREITA/ESQUERDA */
        font-size: 40px !important;
        background: transparent !important;
        border: none !important;
        z-index: 999999 !important;
    }}

    /* O X - AJUSTE AQUI */
    button[key="x_btn"], [data-testid="baseButton-secondary"]:has(div:contains("✖")) {{
        position: fixed !important;
        top: 260px !important;    /* <--- MUDE ESSE PARA SUBIR/DESCER */
        left: 50% !important;
        margin-left: 170px !important; /* <--- MUDE ESSE PARA DIREITA/ESQUERDA */
        font-size: 30px !important;
        color: #888 !important;
        background: transparent !important;
        border: none !important;
        z-index: 999999 !important;
    }}

    /* LIMPEZA GERAL DE BORDAS DO STREAMLIT */
    button {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    </style>
    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco, h1, h3 {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

placeholder_text = "Digite uma palavra ou frase..." 
texto_input = st.text_input("", value=st.session_state.texto, placeholder=placeholder_text, label_visibility="collapsed")
st.session_state.texto = texto_input

st.markdown('<div class="lupa-custom">', unsafe_allow_html=True)
submit_botao = st.button("🔍", key="lupa_btn")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.texto:
    st.markdown('<div class="x-custom">', unsafe_allow_html=True)
    if st.button("✖", key="x_btn"):
        st.session_state.texto = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE TRADUÇÃO
if submit_botao or (st.session_state.texto != ""):
    if st.session_state.texto:
        t_norm = normalizar(st.session_state.texto)
        res = df[df['BUSCA_PT'] == t_norm]
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            tts = gTTS(text=trad, lang='pt-br')
            tts.save("voz_trad.mp3")
            st.audio("voz_trad.mp3", autoplay=True)

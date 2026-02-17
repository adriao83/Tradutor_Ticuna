import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# Lógica de limpeza
if 'texto' not in st.session_state:
    st.session_state.texto = ""

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS PARA COLOCAR ÍCONES DENTRO DA BARRA IGUAL AO DESENHO
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

    /* BARRA DE BUSCA */
    [data-testid="stWidgetLabel"] {{ display: none !important; }}
    
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        position: relative !important;
    }}

    .stTextInput input {{
        height: 55px !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0px 100px 0px 20px !important;
        font-size: 20px !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}

    /* ESTILO DOS BOTÕES (LUPA E X) */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        position: absolute !important;
        z-index: 100 !important;
    }}

    /* POSIÇÃO DA LUPA (IGUAL AO DESENHO) */
    .btn-lupa button {{
        font-size: 35px !important;
        color: #1E90FF !important; /* Cor azulada igual ao seu desenho */
        top: -48px !important; 
        right: 25px !important;
    }}

    /* POSIÇÃO DO X (IGUAL AO DESENHO) */
    .btn-x button {{
        font-size: 30px !important;
        color: #1E90FF !important;
        top: -45px !important;
        right: 70px !important;
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

# CAMPO DE TEXTO E BOTÕES JUNTOS
texto_input = st.text_input("", value=st.session_state.texto, placeholder="Pesquise uma palavra...", label_visibility="collapsed")
st.session_state.texto = texto_input

# Colocando os botões logo abaixo do input para o CSS "puxar" eles para dentro
st.markdown('<div class="btn-lupa">', unsafe_allow_html=True)
submit_botao = st.button("🔍", key="btn_lupa")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.texto:
    st.markdown('<div class="btn-x">', unsafe_allow_html=True)
    if st.button("✖", key="btn_limpar"):
        st.session_state.texto = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA
if submit_botao or (st.session_state.texto != ""):
    if st.session_state.texto:
        t_norm = normalizar(st.session_state.texto)
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

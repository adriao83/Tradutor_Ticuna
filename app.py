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

# Inicializa o estado do texto para permitir a limpeza pelo X
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

# CSS PARA POSICIONAR LUPA E O BOTÃO X
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
    [data-testid="stWidgetLabel"] {{ display: none !important; }}
    
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
    }}

    .stTextInput input {{
        height: 55px !important;
        background-color: transparent !important;
        border: none !important;
        padding: 0px 110px 0px 20px !important; /* Aumentado o recuo para não bater no X e na Lupa */
        font-size: 20px !important;
        line-height: 55px !important;
    }}

    /* ESCONDE AS INSTRUÇÕES "PRESS ENTER" */
    [data-testid="InputInstructions"] {{
        display: none !important;
    }}

    /* ESTILO GERAL DOS BOTÕES (LUPA E X) */
    .stButton button {{
        position: absolute !important;
        background: transparent !important;
        border: none !important;
        color: black !important;
        padding: 0 !important;
        filter: drop-shadow(2px 4px 5px rgba(0,0,0,0.4)) !important;
        z-index: 9999 !important;
    }}

    /* POSIÇÃO ESPECÍFICA DA LUPA */
    div[data-testid="column"]:nth-child(2) button {{
        font-size: 40px !important;
        top: 10px !important;
        right: 60px !important;
    }}

    /* POSIÇÃO ESPECÍFICA DO BOTÃO X */
    div.element-container:has(#botao_limpar) + div button {{
        font-size: 30px !important;
        top: 15px !important;
        right: 110px !important; /* Posicionado à esquerda da lupa */
        color: #555 !important;
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
    # O campo de texto usa o session_state para poder ser limpo
    texto_input = st.text_input("", value=st.session_state.texto_busca, placeholder="Pesquise uma palavra...", label_visibility="collapsed", key="input_principal")
    st.session_state.texto_busca = texto_input

    # Botão X de limpar (aparece apenas se houver texto)
    if st.session_state.texto_busca != "":
        st.markdown('<div id="botao_limpar"></div>', unsafe_allow_html=True)
        if st.button("✕", key="btn_clear"):
            st.session_state.texto_busca = ""
            st.rerun()

with col_btn:
    submit_botao = st.button("🔍")

# LÓGICA
if submit_botao or (st.session_state.texto_busca != ""):
    if st.session_state.texto_busca:
        t_norm = normalizar(st.session_state.texto_busca)
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

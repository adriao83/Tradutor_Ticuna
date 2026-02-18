import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'contador_limpar' not in st.session_state:
    st.session_state.contador_limpar = 0

def acao_limpar():
    st.session_state.contador_limpar += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS DEFINITIVO PARA MOBILE E PC (BOTÕES SOBREPOSTOS) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}

    /* ESTILO DA CAIXA DE TEXTO */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 50px !important;
        padding-right: 85px !important; /* Abre espaço para os botões internos */
        border: none !important;
    }}

    .stTextInput input {{
        color: #333 !important;
    }}

    /* CONTAINER DOS BOTÕES (X e Lupa) */
    /* Isso força eles a ficarem NA FRENTE da caixa, no final dela */
    .botoes-sobrepostos {{
        position: relative;
        float: right;
        margin-top: -42px; /* Sobe os botões para dentro da caixa */
        margin-right: 15px;
        display: flex;
        gap: 10px;
        z-index: 999;
    }}

    /* Estilo dos botões invisíveis (apenas ícones) */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #555 !important;
        font-size: 22px !important;
        padding: 0 !important;
        width: 30px !important;
        height: 30px !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 30px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- INTERFACE ---
# 1. Primeiro a caixa de texto (ela ocupa a largura toda)
texto_busca = st.text_input(
    "", 
    placeholder="Pesquise...", 
    label_visibility="collapsed", 
    key=f"input_{st.session_state.contador_limpar}"
)

# 2. Agora os botões que "flutuam" para dentro da caixa acima
# Criamos colunas bem pequenas só para os botões
st.markdown('<div class="botoes-sobrepostos">', unsafe_allow_html=True)
c_x, c_lupa = st.columns([1, 1])
with c_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar, key="btn_limpar")
with c_lupa:
    st.button("🔍", key="btn_lupa_search")
st.markdown('</div>', unsafe_allow_html=True)

# --- TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts.save("voz_trad.mp3")
            st.audio("voz_trad.mp3", autoplay=True)
        except:
            pass
    else:
        st.markdown('<div class="resultado-traducao">Não encontrado</div>', unsafe_allow_html=True)

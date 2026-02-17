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

# --- CSS TOTALMENTE LIMPO (SEM CILINDROS EXTRAS) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* ESTILO DO CAMPO DE TEXTO OFICIAL */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        padding-right: 95px !important; /* Espaço para X e Lupa */
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }}

    .stTextInput input {{
        color: #333 !important;
        font-size: 18px !important;
        background: transparent !important;
    }}

    /* POSICIONAMENTO DOS BOTÕES (X e LUPA) */
    .btn-container-interno {{
        position: relative;
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: -46px; /* Ajusta para encaixar dentro da barra */
        margin-right: 20px;
        z-index: 99;
    }}

    button[key="btn_x_clear"], button[key="btn_lupa_search"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 24px !important;
        padding: 0 !important;
        cursor: pointer !important;
        color: #555 !important;
        min-height: 0px !important;
        line-height: 1 !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro: Verifique o arquivo 'Tradutor_Ticuna.xlsx'.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- CAMPO DE BUSCA ÚNICO ---
texto_busca = st.text_input(
    "", 
    placeholder="Pesquise uma palavra...", 
    label_visibility="collapsed", 
    key=f"input_{st.session_state.contador_limpar}"
)

# BOTÕES SOBREPOSTOS NA BARRA
st.markdown('<div class="btn-container-interno">', unsafe_allow_html=True)
col_b1, col_b2 = st.columns([1, 1])
with col_b1:
    if texto_busca != "":
        st.button("✖", on_click=acao_limpar, key="btn_x_clear")
with col_b2:
    st.button("🔍", key="btn_lupa_search")
st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE TRADUÇÃO ---
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
        st.markdown('<div class="resultado-traducao">Palavra não encontrada</div>', unsafe_allow_html=True)

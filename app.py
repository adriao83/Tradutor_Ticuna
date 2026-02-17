import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

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

# --- CSS REFEITO PARA PROTEGER O TÍTULO ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* FORÇAR TÍTULO SEMPRE BRANCO */
    h1, h1 span, [data-testid="stMarkdownContainer"] h1 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000 !important;
    }}

    /* Barra Branca */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        padding-right: 85px !important;
    }}

  /* Container que sustenta os botões */
    .btn-overlay {
        position: relative;
        display: flex;
        justify-content: flex-end; /* Alinha os botões na direita */
        gap: 15px;                 /* Espaço entre o X e a Lupa */
        margin-top: -53px;         /* ESTE VALOR FAZ ELES SUBIREM. Tente -55px ou -60px se precisar subir mais */
        margin-right: 20px;        /* Afasta da ponta direita da barra branca */
        z-index: 9999;
    }

    /* Estilo individual para os botões ficarem limpos */
    button[key="btn_x_clear"], button[key="btn_lupa_search"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 28px !important; /* Tamanho dos ícones */
        padding: 0 !important;
        cursor: pointer !important;
        line-height: 1 !important;
    }
    
    button[key="btn_x_clear"]:hover, button[key="btn_lupa_search"]:hover {{
        color: #007bff !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

# Título 
st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# Campo de Busca
texto_busca = st.text_input(
    "", 
    placeholder="Pesquise uma palavra...", 
    label_visibility="collapsed", 
    key=f"input_{st.session_state.contador_limpar}"
)

# Botões
st.markdown('<div class="btn-overlay">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 1])
with c1:
    if texto_busca != "":
        st.button("✖", on_click=acao_limpar, key="btn_x_clear")
with c2:
    st.button("🔍", key="btn_lupa_search")
st.markdown('</div>', unsafe_allow_html=True)

# Resultado
if texto_busca:
    t_norm = normalizar(texto_busca)
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

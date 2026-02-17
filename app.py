import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# Inicializa o estado do texto
if 'texto' not in st.session_state:
    st.session_state.texto = ""

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS TOTALMENTE REFEITO E TESTADO
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Estilo da Barra de Busca */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        border: none !important;
        padding-right: 90px !important; /* Abre espaço para os botões não cobrirem o texto */
    }}

    /* Container dos Botões para ficarem DENTRO da barra */
    .button-container {{
        position: relative;
        height: 0px;
        top: -48px; /* Puxa os botões para dentro da barra branca */
        float: right;
        right: 20px;
        display: flex;
        gap: 10px;
        z-index: 999;
    }}

    /* Estilo dos Botões Invisíveis (apenas o ícone aparece) */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        color: #1E90FF !important;
        font-size: 25px !important;
        padding: 0 !important;
        box-shadow: none !important;
        height: auto !important;
        width: auto !important;
    }}

    /* Ajustes Gerais */
    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco, h1, h3 {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Carrega Planilha
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# LÓGICA DA BARRA E BOTÕES
placeholder_text = "Digite uma palavra ou frase..."

# Input de texto
texto_input = st.text_input("", value=st.session_state.texto, placeholder=placeholder_text, label_visibility="collapsed", key="input_text")

# Criamos um "container" visual para os botões subirem para a barra
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col_x, col_lupa = st.columns([1, 1])

with col_x:
    if st.session_state.texto != "":
        if st.button("✖", key="btn_limpar"):
            st.session_state.texto = ""
            st.rerun()

with col_lupa:
    # A lupa sempre visível ou só quando tem texto
    btn_buscar = st.button("🔍", key="btn_buscar")
st.markdown('</div>', unsafe_allow_html=True)

# Atualiza o estado
if texto_input != st.session_state.texto:
    st.session_state.texto = texto_input
    st.rerun()

# LÓGICA DE TRADUÇÃO
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

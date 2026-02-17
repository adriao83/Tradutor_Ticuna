import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# Lógica de limpeza (Session State)
if 'texto' not in st.session_state:
    st.session_state.texto = ""

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS BLINDADO PARA MANTER OS ÍCONES DENTRO DA BARRA
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

    /* BARRA DE TEXTO BRANCA */
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
        padding: 0px 140px 0px 20px !important; /* Espaço interno para os ícones */
        font-size: 20px !important;
        line-height: 55px !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}

    /* ESTILO DOS BOTÕES PARA NÃO CRIAREM CAIXAS QUADRADAS */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        min-height: 0px !important;
        width: auto !important;
    }}

    .stButton button:hover {{
        background: transparent !important;
        color: inherit !important;
    }}

    /* POSIÇÃO DA LUPA (Onde você já tinha validado) */
    .lupa-fixa button {{
        position: fixed !important;
        font-size: 40px !important;
        color: black !important;
        top: 218px !important; /* Ajuste aqui se ela subir/descer na sua tela */
        left: 50% !important;
        margin-left: 215px !important; /* Move para a direita da barra */
        z-index: 9999 !important;
    }}

    /* POSIÇÃO DO X (LIMPAR) */
    .x-fixo button {{
        position: fixed !important;
        font-size: 25px !important;
        color: #888 !important;
        top: 228px !important; /* Alinhado ao centro do texto */
        left: 50% !important;
        margin-left: 170px !important; /* Fica logo à esquerda da lupa */
        z-index: 10000 !important;
    }}

    [data-testid="column"] {{
        background: transparent !important;
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

# CAMPO DE BUSCA
texto_input = st.text_input("", value=st.session_state.texto, placeholder="Pesquise uma palavra...", label_visibility="collapsed", key="input_main")
st.session_state.texto = texto_input

# ÍCONES FIXOS
st.markdown('<div class="lupa-fixa">', unsafe_allow_html=True)
submit_botao = st.button("🔍", key="search")
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.texto:
    st.markdown('<div class="x-fixo">', unsafe_allow_html=True)
    if st.button("✖", key="clear"):
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
            try:
                tts = gTTS(text=trad, lang='pt-br')
                tts.save("voz_trad.mp3")
                st.audio("voz_trad.mp3", autoplay=True)
            except:
                pass

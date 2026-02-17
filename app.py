import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- LÓGICA DE ESTADO (Para o botão X funcionar) ---
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

def limpar_texto():
    st.session_state.texto_busca = ""
    # O rerun é essencial para limpar a caixa visualmente
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS ÚNICO E ORGANIZADO ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Barra Branca */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        padding-right: 80px !important;
    }}

    /* Container para posicionar os botões sobre a barra */
    .btn-overlay {{
        position: relative;
        height: 0px;
        top: -46px; /* Ajuste aqui se os ícones subirem ou descerem demais */
        float: right;
        right: 15px;
        z-index: 999;
        display: flex;
        gap: 5px;
    }}

    /* Estilo dos botões (Lupa e X) */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 24px !important;
        color: #555 !important;
        padding: 0px !important;
        cursor: pointer !important;
    }}
    
    .stButton button:hover {{ color: #1E90FF !important; }}

    /* Outros ajustes */
    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco, h1, h3 {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE TRADUÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# --- CAMPO DE BUSCA ---
# Usamos o session_state diretamente no value para o X funcionar
texto_input = st.text_input(
    "", 
    value=st.session_state.texto_busca, 
    placeholder="Pesquise uma palavra...", 
    label_visibility="collapsed", 
    key="input_principal"
)

# Atualiza o estado conforme o usuário digita
st.session_state.texto_busca = texto_input

# --- SOBREPOSIÇÃO DOS BOTÕES ---
st.markdown('<div class="btn-overlay">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    if st.session_state.texto_busca != "":
        # Botão X chama a função de limpar
        st.button("✖", on_click=limpar_texto, key="btn_x")

with col2:
    btn_lupa = st.button("🔍", key="btn_lupa")
st.markdown('</div>', unsafe_allow_html=True)

# --- RESULTADO ---
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

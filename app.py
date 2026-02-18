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

# --- CSS AJUSTADO PARA ALINHAMENTO ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* O Campo de texto com a borda vermelha que você gosta */
    .stTextInput > div {{
        background-color: #f0f2f6 !important;
        border-radius: 10px !important;
    }}

    /* Estilo da Lupa */
    .stButton button {{
        background-color: white !important;
        border-radius: 8px !important;
        height: 44px !important; /* Altura aproximada do input */
        width: 44px !important;
        border: 1px solid #ccc !important;
        margin-top: -5px; /* AJUSTE FINO PARA SUBIR A LUPA */
    }}

    /* Remove instruções extras */
    [data-testid="InputInstructions"] {{ display: none !important; }}
    
    .resultado-traducao {{ 
        color: white !important; 
        text-align: center; 
        font-size: 34px; 
        font-weight: 900; 
        text-shadow: 2px 2px 15px #000; 
        padding: 20px; 
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- INTERFACE ALINHADA ---
# Usamos colunas para colocar um do lado do outro
col_texto, col_lupa = st.columns([0.88, 0.12])

with col_texto:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise uma palavra...", 
        label_visibility="collapsed", 
        key=f"input_{st.session_state.contador_limpar}"
    )

with col_lupa:
    # O botão da lupa agora está alinhado via CSS (margin-top negativo)
    st.button("🔍", key="btn_lupa_search")

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
        st.markdown('<div class="resultado-traducao">Não encontrado</div>', unsafe_allow_html=True)

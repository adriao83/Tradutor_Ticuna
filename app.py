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

# --- CSS LIMPO (MANTÉM APENAS O INPUT E A LUPA) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* Removemos qualquer fundo branco ou 'cilindro' que estava por trás */
    .stTextInput > div {{
        background-color: #f0f2f6 !important; /* Cor clara padrão para o input */
        border-radius: 10px !important;
        border: 1px solid transparent !important;
    }}

    /* Estilo para quando você clica dentro (Borda Vermelha) */
    .stTextInput > div:focus-within {{
        border: 1px solid red !important;
        box-shadow: 0 0 0 0.2rem rgba(255, 0, 0, 0.25) !important;
    }}

    /* Alinhamento da Lupa ao lado do Input */
    .container-busca {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 20px;
    }}

    .stButton button {{
        background-color: white !important;
        border-radius: 8px !important;
        height: 45px !important;
        width: 45px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #ccc !important;
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
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- INTERFACE: APENAS O QUE VOCÊ PRECISA ---
# Criamos um container simples para alinhar o input e a lupa lado a lado
col_texto, col_lupa = st.columns([0.9, 0.1])

with col_texto:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise uma palavra...", 
        label_visibility="collapsed", 
        key=f"input_{st.session_state.contador_limpar}"
    )

with col_lupa:
    st.write("<div style='margin-top: 0px;'>", unsafe_allow_html=True)
    st.button("🔍", key="btn_lupa_search")
    st.write("</div>", unsafe_allow_html=True)

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

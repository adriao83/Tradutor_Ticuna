import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    # Remove espaços extras e caracteres especiais
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

# Configuração da IA (Opcional)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    pass

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS DEFINITIVO ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; font-size: 2rem !important; }}

    /* FORÇAR ALINHAMENTO EM LINHA PARA MOBILE */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px !important;
    }}

    /* CAIXA DE TEXTO */
    .stTextInput > div > div > input {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 45px !important;
    }}

    /* BOTÕES */
    .stButton button {{
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
        height: 45px !important;
        width: 45px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #ccc !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 28px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    # Carrega a planilha
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    # Cria coluna de busca normalizada para evitar erros com maiúsculas/acentos
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro: Certifique-se que o arquivo 'Tradutor_Ticuna.xlsx' está na mesma pasta do código.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa = st.columns([0.7, 0.15, 0.15])

with col_txt:
    texto_busca = st.text_input("", placeholder="Digite aqui...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar)

with col_lupa:
    st.button("🔍")

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            # Gera o áudio da tradução
            tts = gTTS(text=str(trad), lang='pt-br')
            tts.save("voz.mp3")
            st.audio("voz.mp3", autoplay=True)
        except:
            pass
    else:
        st.markdown('<div class="resultado-traducao">Palavra não encontrada</div>', unsafe_allow_html=True)

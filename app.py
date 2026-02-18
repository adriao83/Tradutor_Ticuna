import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Configuração da IA (verifique se sua chave está correta em secrets)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro na chave da API.")

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

def acao_limpar():
    st.session_state.texto_busca = ""
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS DEFINITIVO (BLOQUEIA QUEBRA NO MOBILE) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Título Responsivo */
    h1, h1 span {{ 
        color: white !important; 
        text-shadow: 2px 2px 10px #000 !important; 
        text-align: center;
        font-size: 28px !important;
    }}

    /* ESTILO DA BARRA ÚNICA: Nada escapa dela */
    .search-container {{
        display: flex;
        align-items: center;
        background-color: white;
        border-radius: 30px;
        padding: 5px 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        margin: 10px 0;
    }}

    /* Estilizando o input interno do Streamlit */
    .stTextInput > div > div > input {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 16px !important;
        color: #333 !important;
    }}
    
    .stTextInput {{ margin-bottom: 0px !important; width: 100%; }}
    [data-testid="stHorizontalBlock"] {{ align-items: center !important; gap: 0px !important; }}

    /* Estilo dos Botões dentro da linha */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        padding: 0px 5px !important;
        font-size: 20px !important;
        color: #555 !important;
        box-shadow: none !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 26px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 15px; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA (SEM COLUNAS QUE QUEBRAM) ---
# Usamos um container de fundo branco e colocamos os widgets dentro
with st.container():
    # Aqui a mágica: forçamos a largura dos botões para serem pequenos
    c1, c2, c3 = st.columns([0.8, 0.1, 0.1])
    
    with c1:
        texto_busca = st.text_input("", placeholder="Pesquise...", label_visibility="collapsed", key="main_input")
    with c2:
        if texto_busca:
            st.button("✖", on_click=acao_limpar, key="clear_btn")
    with c3:
        st.button("🔍", key="search_btn")

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    pass # Silencia o erro visual na tela

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
        # Se não achar na planilha, a IA pode tentar ajudar (opcional)
        st.markdown('<div class="resultado-traducao">Palavra não encontrada na base.</div>', unsafe_allow_html=True)

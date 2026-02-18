import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Configuração da IA
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    pass

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

def acao_limpar():
    st.session_state.texto_busca = ""

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS "BLINDADO" PARA MOBILE ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Título */
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}

    /* CAIXA DE TEXTO (O INPUT REAL) */
    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.9) !important; /* Branco levemente transparente */
        color: #000000 !important; /* TEXTO PRETO PARA APARECER BEM */
        border-radius: 25px !important;
        height: 50px !important;
        padding-left: 20px !important;
        padding-right: 80px !important; /* Espaço para os botões */
        border: 2px solid transparent !important;
        font-size: 18px !important;
    }}

    /* Borda vermelha ao clicar */
    .stTextInput > div > div > input:focus {{
        border: 2px solid red !important;
    }}

    /* POSICIONAMENTO DOS BOTÕES (X e Lupa) DENTRO DA CAIXA */
    .element-container:has(#btn_x_div), .element-container:has(#btn_lupa_div) {{
        position: absolute;
        z-index: 1000;
    }}

    /* Força os botões para a mesma linha da caixa no mobile */
    div[data-testid="column"] {{
        width: fit-content !important;
        flex: unset !important;
        min-width: unset !important;
    }}

    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
    }}

    .stButton button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 20px !important;
        color: #333 !important;
        margin-top: -10px !important; /* Ajuste fino para alinhar com o centro da caixa */
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 28px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 15px; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    df = pd.DataFrame(columns=['PORTUGUES', 'TICUNA', 'BUSCA_PT'])

# --- INTERFACE ---
# Criamos uma linha que NÃO quebra no celular
col_main, col_x, col_lupa = st.columns([0.7, 0.1, 0.1])

with col_main:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise...", 
        label_visibility="collapsed", 
        key="main_input"
    )

with col_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar, key="btn_x")

with col_lupa:
    st.button("🔍", key="btn_lupa")

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca:
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
    elif df is not None:
        st.markdown('<div class="resultado-traducao">Não encontrado</div>', unsafe_allow_html=True)

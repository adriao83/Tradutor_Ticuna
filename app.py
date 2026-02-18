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

# --- CSS REFEITO PARA MANTER O ALINHAMENTO DA LUPA ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* Remove qualquer borda ou caixa extra do Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] > div:has(.custom-search-bar) {{
        background: transparent !important;
    }}

    /* ESTE É O MODELO QUE VOCÊ QUER: A BARRA ÚNICA */
    .custom-search-bar {{
        display: flex;
        align-items: center;
        background-color: white;
        border-radius: 25px;
        height: 55px;
        padding: 0 15px;
        margin-top: 30px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }}

    .custom-search-bar .stTextInput {{
        flex-grow: 1;
        margin-bottom: 0px !important;
    }}
    
    .custom-search-bar .stTextInput > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    
    .custom-search-bar .stTextInput input {{
        background: transparent !important;
        border: none !important;
        height: 55px !important;
        font-size: 18px !important;
        color: #333 !important;
    }}

    /* Estilo dos botões alinhados na direita */
    .custom-search-bar button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 24px !important;
        color: #555 !important;
        padding: 0 5px !important;
        cursor: pointer !important;
        height: 55px !important;
        display: flex;
        align-items: center;
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

# --- A ESTRUTURA ALINHADA QUE VOCÊ PEDIU ---
st.markdown('<div class="custom-search-bar">', unsafe_allow_html=True)

# Colunas internas para manter tudo na mesma linha (Input + Botões)
col_input, col_botoes = st.columns([0.85, 0.15])

with col_input:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise uma palavra...", 
        label_visibility="collapsed", 
        key=f"input_{st.session_state.contador_limpar}"
    )

with col_botoes:
    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        if texto_busca != "":
            st.button("✖", on_click=acao_limpar, key="btn_x_clear")
    with sub_c2:
        st.button("🔍", key="btn_lupa_search")

st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE RESULTADO ---
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

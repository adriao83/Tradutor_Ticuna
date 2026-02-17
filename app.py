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

# --- O TRUQUE DO CSS PARA FUNDIR OS BOTÕES NA BARRA ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Mantém o título branco */
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* Remove as bordas padrão do Streamlit para podermos criar a nossa */
    [data-testid="stVerticalBlockBorderWrapper"] > div:has(.custom-search-bar) {{
        background: transparent !important;
    }}

    /* ESTE É O CONTAINER QUE PARECE UMA CAIXA DE TEXTO */
    .custom-search-bar {{
        display: flex;
        align-items: center;
        background-color: white;
        border-radius: 25px;
        height: 55px;
        padding: 0 15px;
        margin-bottom: 20px;
    }}

    /* Estilo do input dentro da nossa barra fake */
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
    }}

    /* Estilo dos botões que agora estão 'presos' na barra */
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

    .custom-search-bar button:hover {{ color: #007bff !important; }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# --- A ESTRUTURA UNIFICADA ---
# Criamos uma div que segura tudo junto
st.markdown('<div class="custom-search-bar">', unsafe_allow_html=True)

# Usamos colunas internas para organizar o input e os botões LADO A LADO dentro da barra branca
col_input, col_botoes = st.columns([0.85, 0.15])

with col_input:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise uma palavra...", 
        label_visibility="collapsed", 
        key=f"input_{st.session_state.contador_limpar}"
    )

with col_botoes:
    # Usamos uma sub-coluna para alinhar X e Lupa um ao lado do outro na ponta direita
    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        if texto_busca != "":
            st.button("✖", on_click=acao_limpar, key="btn_x_clear")
    with sub_c2:
        st.button("🔍", key="btn_lupa_search")

st.markdown('</div>', unsafe_allow_html=True)

# --- LÓGICA DE RESULTADO ---
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

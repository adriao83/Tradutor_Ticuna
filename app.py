import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import os

# Tenta carregar a planilha primeiro para evitar o erro da seta verde
nome_arquivo = "Tradutor_Ticuna.xlsx"
df = None

if os.path.exists(nome_arquivo):
    try:
        df = pd.read_excel(nome_arquivo)
        def normalizar(t):
            return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""
        df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
else:
    st.warning("⚠️ Arquivo 'Tradutor_Ticuna.xlsx' não encontrado. Verifique se ele está na mesma pasta do código.")

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'contador_limpar' not in st.session_state:
    st.session_state.contador_limpar = 0

def acao_limpar():
    st.session_state.contador_limpar += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS REFINADO (SEM CAIXA EXTRA) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    /* Título Branco */
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; }}

    /* BARRA DE BUSCA - ÚNICA */
    .stTextInput > div {{
        background-color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        padding-right: 90px !important; /* Espaço para os botões internos */
        border: none !important;
    }}

    .stTextInput input {{
        color: #333 !important;
        font-size: 18px !important;
    }}

    /* CONTAINER DOS BOTÕES (DENTRO DA BARRA) */
    .btn-container-interno {{
        position: relative;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: -48px; /* Puxa os botões para dentro da barra */
        margin-right: 20px;
        z-index: 99;
    }}

    /* Estilo dos Botões */
    button[key="btn_x_clear"], button[key="btn_lupa_search"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 24px !important;
        padding: 0 !important;
        cursor: pointer !important;
        color: #555 !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    .texto-fixo-branco {{ color: white !important; text-align: center; text-shadow: 2px 2px 10px #000; }}
    .resultado-traducao {{ color: white !important; text-align: center; font-size: 34px; font-weight: 900; text-shadow: 2px 2px 15px #000; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# 1. O Campo de Texto (Único agora)
texto_busca = st.text_input(
    "", 
    placeholder="Pesquise uma palavra...", 
    label_visibility="collapsed", 
    key=f"input_{st.session_state.contador_limpar}"
)

# 2. Os Botões (Injetados via CSS dentro da barra acima)
st.markdown('<div class="btn-container-interno">', unsafe_allow_html=True)
col_b1, col_b2 = st.columns([1, 1])
with col_b1:
    if texto_busca != "":
        st.button("✖", on_click=acao_limpar, key="btn_x_clear")
with col_b2:
    st.button("🔍", key="btn_lupa_search")
st.markdown('</div>', unsafe_allow_html=True)

# 3. Lógica de Tradução
if texto_busca and df is not None:
    def normalizar(t):
        return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""
    
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

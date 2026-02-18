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

# --- CSS PARA LAYOUT RESPONSIVO (MOBILE + PC) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}

    h1, h1 span {{ 
        color: white !important; 
        text-shadow: 2px 2px 10px #000 !important; 
        font-size: 2.2rem !important;
        text-align: center;
    }}

    /* Container que força tudo a ficar na mesma linha no celular */
    .flex-container {{
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        margin-top: 10px;
    }}

    /* Ajuste da caixa de texto */
    .stTextInput {{
        flex-grow: 1; /* Faz a caixa ocupar o máximo de espaço */
    }}

    .stTextInput > div {{
        background-color: #f0f2f6 !important;
        border-radius: 10px !important;
    }}

    /* Botões X e Lupa pequenos e alinhados */
    .stButton button {{
        background-color: white !important;
        border-radius: 8px !important;
        height: 44px !important;
        width: 44px !important;
        border: 1px solid #ccc !important;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 !important;
    }}

    [data-testid="InputInstructions"] {{ display: none !important; }}
    
    .resultado-traducao {{ 
        color: white !important; 
        text-align: center; 
        font-size: 28px; 
        font-weight: 900; 
        text-shadow: 2px 2px 15px #000; 
        padding: 20px; 
    }}

    /* Ajuste para o player de áudio não sumir no mobile */
    audio {{
        width: 100%;
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

# --- INTERFACE RESPONSIVA ---
# Usamos HTML puro para criar o container flexível que o Streamlit não quebra no mobile
st.markdown('<div class="flex-container">', unsafe_allow_html=True)

# Criamos colunas com larguras proporcionais para manter a linha única
c_text, c_x, c_lupa = st.columns([0.7, 0.15, 0.15])

with c_text:
    texto_busca = st.text_input(
        "", 
        placeholder="Pesquise...", 
        label_visibility="collapsed", 
        key=f"input_{st.session_state.contador_limpar}"
    )

with c_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar, key="btn_limpar")

with c_lupa:
    st.button("🔍", key="btn_lupa_search")

st.markdown('</div>', unsafe_allow_html=True)

# --- TRADUÇÃO ---
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

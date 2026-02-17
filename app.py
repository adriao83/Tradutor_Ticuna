import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
import os

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS REFINADO PARA O MODELO GOOGLE
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    .texto-fixo-branco, h1, h3 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000000, 0px 0px 5px #000000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    .resultado-traducao {{
        color: white !important;
        text-shadow: 2px 2px 15px #000000, -2px -2px 15px #000000, 0px 0px 20px #000000 !important;
        font-size: 34px !important;
        text-align: center;
        padding: 20px;
        font-weight: 900 !important;
    }}

    /* CAIXA BRANCA PRINCIPAL */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 20px; 
        border-radius: 30px; /* Bordas bem arredondadas estilo Google */
        border: 1px solid #dfe1e5 !important;
    }}

    /* REMOVE BORDAS PADRÃO DO STREAMLIT DENTRO DO FORM */
    [data-testid="stForm"] {{ border: none !important; box-shadow: none !important; }}

    /* ESTILO DA BARRA DE TEXTO */
    .stTextInput input {{
        border: none !important;
        background: transparent !important;
        font-size: 18px !important;
        height: 45px !important;
    }}
    
    /* ESTILO DO BOTÃO DA LUPA */
    .stButton button {{
        background: transparent !important;
        border: none !important;
        font-size: 24px !important;
        padding: 0 !important;
        margin-top: 5px !important;
        box-shadow: none !important;
    }}

    /* Tira o texto "Press Enter to submit" */
    small {{ display: none !important; }}
    
    .stAlert {{ background: transparent !important; border: none !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.markdown('<p class="texto-fixo-branco">Erro ao carregar planilha.</p>', unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- AREA DE TRADUÇÃO MODELO GOOGLE ---
st.markdown('<h3 class="texto-fixo-branco">Digite para Traduzir:</h3>', unsafe_allow_html=True)

# Criamos o container branco
with st.container():
    # Usamos colunas para colocar o texto e a lupa lado a lado na mesma linha
    col1, col2 = st.columns([0.9, 0.1])
    
    with col1:
        # Campo de texto sem bordas (as bordas são do container)
        texto_input = st.text_input("", placeholder="Pesquise no Tradutor Ticuna...", label_visibility="collapsed")
    
    with col2:
        # Botão que funciona como a lupa
        submit_botao = st.button("🔍")

# LÓGICA DE BUSCA (Acionada por Enter ou Clique na Lupa)
if submit_botao or (texto_input != ""):
    if texto_input:
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # Gera o áudio
            try:
                tts = gTTS(text=trad, lang='pt-br')
                tts.save("voz_trad.mp3")
                st.audio("voz_trad.mp3", autoplay=True)
            except:
                pass
        elif submit_botao: # Só mostra erro se o usuário realmente tentou buscar
            st.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_input}" não foi encontrada.</p>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS PARA INTEGRAR O MICROFONE DENTRO DA CAIXA
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

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px;
        position: relative;
    }}
    
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; text-shadow: none !important; }}

    /* TRUQUE PARA COLOCAR O MIC DENTRO DA CAIXA */
    div[data-testid="stVerticalBlock"] > div:has(#mic_unificado) {{
        position: absolute;
        right: 45px; /* Ajusta a posição lateral */
        margin-top: -62px; /* Puxa o botão para dentro da linha do input */
        z-index: 999;
    }}

    /* Estilo do botão do microfone para parecer um ícone interno */
    button[title="Clique para falar 🎤"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 20px !important;
    }}

    .stTextInput input {{
        padding-right: 50px !important; /* Abre espaço para o ícone não cobrir o texto */
    }}
    
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
    st.markdown('<p class="texto-fixo-branco">Erro ao carregar planilha no GitHub.</p>', unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- ÁREA DE TRADUÇÃO UNIFICADA ---
st.markdown("---")
with st.form("form_digitar"):
    texto_input = st.text_input("Digite uma palavra:", placeholder="Ex: Capivara")
    
    # O microfone é colocado logo abaixo no código, mas o CSS "puxa" ele para dentro do input acima
    audio_data = mic_recorder(
        start_prompt="🎤", 
        stop_prompt="⏹️", 
        key='mic_unificado'
    )
    
    submit_botao = st.form_submit_button("🔍 TRADUZIR")

# LÓGICA DE PROCESSAMENTO
palavra_final = ""

if audio_data:
    status_msg = st.empty()
    status_msg.markdown('<p class="texto-fixo-branco">Identificando sua voz...</p>', unsafe_allow_html=True)
    try:
        audio_part = {"mime_type": "audio/wav", "data": audio_data['bytes']}
        response = model.generate_content([
            "Transcreva apenas a palavra ou frase dita neste áudio.",
            audio_part
        ])
        palavra_final = response.text.strip().replace(".", "").replace("!", "")
        status_msg.empty()
    except:
        status_msg.empty()
        st.markdown('<p class="texto-fixo-branco">Erro ao processar voz.</p>', unsafe_allow_html=True)

if submit_botao:
    palavra_final = texto_input

# BUSCA E EXIBIÇÃO
if palavra_final:
    t_norm = normalizar(palavra_final)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        gTTS(text=trad, lang='pt-br').save("voz_trad.mp3")
        st.audio("voz_trad.mp3", autoplay=True)
    else:
        st.markdown(f'<p class="texto-fixo-branco">A palavra "{palavra_final}" não está na planilha.</p>', unsafe_allow_html=True)

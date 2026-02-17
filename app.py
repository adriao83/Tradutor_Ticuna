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

# CSS: MENSAGENS EM BRANCO COM SOMBREAMENTO PRETO
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* Estilo para frases de status e avisos (Branco com Sombra) */
    .texto-branco-sombra {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    /* Resultado da Tradução: Ticuna Nacü com sombreamento preto forte */
    .resultado-traducao {{
        color: white !important;
        text-shadow: 0px 0px 15px #000000, 2px 2px 5px #000000, -2px -2px 5px #000000 !important;
        font-size: 32px !important;
        text-align: center;
        padding: 20px;
        font-weight: 900 !important;
    }}

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; border-radius: 15px; 
    }}
    
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.markdown('<p class="texto-branco-sombra">Erro ao carregar planilha no GitHub.</p>', unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- CENTRAL DE COMANDO UNIFICADA ---
st.markdown("### 🎤 Fale ou Digite para Traduzir")

# Variável para guardar o texto que será traduzido
texto_para_processar = ""

# 1. PARTE DA VOZ
audio_data = mic_recorder(
    start_prompt="Falar 🎤", 
    stop_prompt="Processar Voz ⏹️", 
    key='gravador_unificado'
)

if audio_data:
    try:
        # Transcreve o áudio para texto
        response = model.generate_content([
            "Transcreva apenas a palavra falada, sem pontuação.", 
            {"mime_type": "audio/wav", "data": audio_data['bytes']}
        ])
        texto_para_processar = response.text.strip()
    except:
        st.markdown('<p class="texto-branco-sombra">IA de voz ocupada. Tente digitar abaixo.</p>', unsafe_allow_html=True)

# 2. PARTE DA DIGITAÇÃO (O formulário que você gosta)
with st.form("form_unificado"):
    texto_input = st.text_input("Palavra:", value=texto_para_processar, placeholder="Ex: Capivara")
    submit = st.form_submit_button("🔍 TRADUZIR AGORA")
    
    # Se clicar no botão ou se a voz trouxer um texto, processamos
    palavra_final = texto_input if submit else texto_para_processar

    if palavra_final:
        t_norm = normalizar(palavra_final)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            # Exibe com o sombreamento preto
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # Gera e toca o áudio (Voz Sintética)
            tts = gTTS(text=trad, lang='pt-br')
            tts.save("traducao.mp3")
            st.audio("traducao.mp3", autoplay=True)
        else:
            st.markdown(f'<p class="texto-branco-sombra">"{palavra_final}" não encontrada na planilha.</p>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p class="texto-branco-sombra">Dica: Ao usar a voz, clique em "Processar Voz" e depois em "Traduzir".</p>', unsafe_allow_html=True)

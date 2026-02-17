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

# CSS REFINADO: FOCO NO SOMBREAMENTO PRETO
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* Estilo para as mensagens de status e frases de erro em BRANCO */
    .texto-fixo-branco, .stAlert p, h1, h3 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000000 !important;
        text-align: center;
        font-weight: bold !important;
        background: transparent !important;
    }}

    /* Estilo para o resultado da tradução com SOMBREAMENTO PRETO (Glow/Shadow) */
    .resultado-traducao {{
        color: white !important;
        text-shadow: 0px 0px 15px #000000, 0px 0px 10px #000000, 2px 2px 5px #000000 !important;
        font-size: 30px !important;
        text-align: center;
        padding: 20px;
        font-weight: 800 !important;
    }}

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px; 
    }}
    
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; text-shadow: none !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# 1. CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar a planilha Tradutor_Ticuna.xlsx no GitHub.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ ---
st.markdown("### 🎤 Fale para Traduzir")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    audio_data = mic_recorder(
        start_prompt="Clique para falar 🎤", 
        stop_prompt="Traduzir fala ⏹️", 
        key='gravador'
    )

if audio_data:
    status = st.empty()
    status.markdown('<p class="texto-fixo-branco">Identificando sua voz...</p>', unsafe_allow_html=True)
    
    try:
        # Envio do áudio para transcrição
        prompt = "Transcreva apenas a palavra falada, sem pontuação."
        response = model.generate_content([
            prompt, 
            {"mime_type": "audio/wav", "data": audio_data['bytes']}
        ])
        
        texto_falado = response.text.strip()
        t_norm = normalizar(texto_falado)
        
        # BUSCA NA PLANILHA
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            status.empty()
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # GERA ÁUDIO SINTÉTICO
            gTTS(text=trad, lang='pt-br').save("voz_fala.mp3")
            st.audio("voz_fala.mp3", autoplay=True)
        else:
            status.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_falado}" não está na planilha.</p>', unsafe_allow_html=True)

    except Exception as e:
        status.markdown('<p class="texto-fixo-branco">Erro ao processar voz. Tente digitar ou verifique a chave API.</p>', unsafe_allow_html=True)

# --- SEÇÃO DE DIGITAÇÃO ---
st.markdown("---")
with st.form("form_digitar"):
    texto_input = st.text_input("Ou digite uma palavra:", placeholder="Ex: Capivara")
    if st.form_submit_button("🔍 TRADUZIR"):
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            # Resultado com SOMBREAMENTO PRETO para destaque total
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            gTTS(text=trad, lang='pt-br').save("voz_digito.mp3")
            st.audio("voz_digito.mp3", autoplay=True)
        else:
            st.markdown('<p class="texto-fixo-branco">Palavra não encontrada na planilha.</p>', unsafe_allow_html=True)

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

# CSS REFINADO: FOCO NO SOMBREAMENTO E MENSAGENS BRANCAS
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* MENSAGENS DE STATUS E ERRO: SEMPRE BRANCO COM SOMBRA */
    .texto-fixo-branco, h1, h3 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000000, 0px 0px 5px #000000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    /* RESULTADO DA TRADUÇÃO COM SOMBREAMENTO PRETO FORTE (Efeito Neon Reverso) */
    .resultado-traducao {{
        color: white !important;
        text-shadow: 
            2px 2px 0px #000, 
            -2px -2px 0px #000, 
            2px -2px 0px #000, 
            -2px 2px 0px #000,
            0px 0px 15px #000 !important;
        font-size: 34px !important;
        text-align: center;
        padding: 20px;
        font-weight: 900 !important;
    }}

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px; 
    }}
    
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; text-shadow: none !important; }}
    
    /* Força o sumiço das caixas coloridas do Streamlit */
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
    status_msg = st.empty()
    status_msg.markdown('<p class="texto-fixo-branco">Identificando sua voz...</p>', unsafe_allow_html=True)
    
    try:
        # TENTATIVA DE TRANSCRIÇÃO CORRIGIDA
        audio_part = [{"mime_type": "audio/wav", "data": audio_data['bytes']}]
        
        # Chamada simplificada para evitar o erro de processamento
        response = model.generate_content([
            "Transcreva apenas a palavra dita, sem pontuação.",
            audio_part[0]
        ])
        
        texto_falado = response.text.strip().lower()
        t_norm = normalizar(texto_falado)
        
        # BUSCA NA PLANILHA
        res = df[df['BUSCA_PT'] == t_norm]
        
        status_msg.empty()

        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<p class="texto-fixo-branco">Você disse: "{texto_falado}"</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # GERA VOZ SINTÉTICA (Retornando o áudio igual ao comando de digitação)
            tts = gTTS(text=trad, lang='pt-br')
            tts.save("voz_fala.mp3")
            st.audio("voz_fala.mp3", autoplay=True)
        else:
            st.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_falado}" não está na planilha.</p>', unsafe_allow_html=True)

    except Exception as e:
        status_msg.empty()
        st.markdown('<p class="texto-fixo-branco">Erro ao processar voz. Tente falar novamente ou digite.</p>', unsafe_allow_html=True)

# --- SEÇÃO DE DIGITAÇÃO (MANTIDA EXATAMENTE IGUAL) ---
st.markdown("---")
with st.form("form_digitar"):
    texto_input = st.text_input("Ou digite uma palavra:", placeholder="Ex: Capivara")
    if st.form_submit_button("🔍 TRADUZIR"):
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            gTTS(text=trad, lang='pt-br').save("voz_digito.mp3")
            st.audio("voz_digito.mp3", autoplay=True)
        else:
            st.markdown('<p class="texto-fixo-branco">Palavra não encontrada na planilha.</p>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Configuração da IA (Para tradução de texto caso não esteja na planilha)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS: MENSAGENS EM BRANCO E SOMBREAMENTO PRETO
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* Estilo para frases de status e erros: BRANCO COM SOMBRA PRETA */
    .texto-fixo-branco, .stAlert p, h1, h3 {{
        color: white !important;
        text-shadow: 2px 2px 10px #000000, 1px 1px 2px #000000 !important;
        text-align: center;
        font-weight: bold !important;
        background: transparent !important;
    }}

    /* RESULTADO DA TRADUÇÃO: SOMBREAMENTO PRETO FORTE */
    .resultado-traducao {{
        color: white !important;
        text-shadow: 0px 0px 20px #000000, 0px 0px 10px #000000, 4px 4px 5px #000000 !important;
        font-size: 32px !important;
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
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# CARREGAR PLANILHA
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar a planilha no GitHub.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ REFORMULADA ---
st.markdown("### 🎤 Fale para Traduzir")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    # Usando mic_recorder para capturar áudio
    audio_data = mic_recorder(
        start_prompt="Falar agora 🎤", 
        stop_prompt="Parar e Traduzir ⏹️", 
        key='gravador_v3'
    )

if audio_data:
    status = st.empty()
    status.markdown('<p class="texto-fixo-branco">Processando sua fala...</p>', unsafe_allow_html=True)
    
    try:
        # Envio direto para transcrição (Tentativa com tratamento de erro)
        audio_blob = {"mime_type": "audio/wav", "data": audio_data['bytes']}
        response = model.generate_content(["Transcreva apenas a palavra ou frase dita neste áudio:", audio_blob])
        
        texto_falado = response.text.strip()
        t_norm = normalizar(texto_falado)
        
        # BUSCA NA PLANILHA
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            status.empty()
            st.markdown(f'<p class="texto-fixo-branco">Você disse: "{texto_falado}"</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # VOZ SINTÉTICA
            gTTS(text=trad, lang='pt-br').save("voz_output.mp3")
            st.audio("voz_output.mp3", autoplay=True)
        else:
            status.markdown(f'<p class="texto-fixo-branco">A palavra "{texto_falado}" não está na planilha. Tentando IA...</p>', unsafe_allow_html=True)
            res_ia = model.generate_content(f"Traduza '{texto_falado}' para a língua Ticuna. Responda apenas a tradução.")
            st.markdown(f'<div class="resultado-traducao">IA: {res_ia.text}</div>', unsafe_allow_html=True)
            gTTS(text=res_ia.text, lang='pt-br').save("voz_ia.mp3")
            st.audio("voz_ia.mp3", autoplay=True)

    except Exception as e:
        status.markdown('<p class="texto-fixo-branco">Erro ao processar voz. Por favor, use a digitação abaixo enquanto ajustamos o servidor.</p>', unsafe_allow_html=True)

# --- SEÇÃO DE DIGITAÇÃO ---
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
            st.markdown('<p class="texto-fixo-branco">Buscando na IA...</p>', unsafe_allow_html=True)
            res_ia_txt = model.generate_content(f"Traduza '{texto_input}' para Ticuna.")
            st.markdown(f'<div class="resultado-traducao">Ticuna: {res_ia_txt.text}</div>', unsafe_allow_html=True)
            gTTS(text=res_ia_txt.text, lang='pt-br').save("voz_ia_txt.mp3")
            st.audio("voz_ia_txt.mp3", autoplay=True)

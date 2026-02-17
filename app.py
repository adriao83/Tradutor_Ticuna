import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import base64
import time
import io

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS REFINADO
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-attachment: fixed !important;
    }}
    h1, h3, .texto-branco-fixo {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        text-align: center;
        font-weight: bold !important;
    }}
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px; 
    }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Carregar Planilha
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar banco de dados.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ (SÓ RECONHECIMENTO) ---
st.markdown("### 🎤 Fale a palavra para traduzir")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    audio_gravado = mic_recorder(
        start_prompt="Falar (Português/Ticuna) 🎤", 
        stop_prompt="Traduzir Agora ⏹️", 
        key='gravador'
    )

if audio_gravado:
    status_placeholder = st.empty()
    status_placeholder.markdown('<p class="texto-branco-fixo">Interpretando sua fala...</p>', unsafe_allow_html=True)
    
    try:
        # 1. Transcrever o áudio (Transformar sua voz em texto)
        # Enviando o áudio corretamente para o Gemini 1.5 Flash
        audio_data = audio_gravado['bytes']
        prompt_transcricao = "Transcreva apenas a palavra falada, sem pontuação."
        
        response_ia = model.generate_content([
            prompt_transcricao,
            {"mime_type": "audio/wav", "data": audio_data}
        ])
        
        palavra_dita = response_ia.text.strip()
        palavra_norm = normalizar(palavra_dita)
        
        status_placeholder.empty()
        st.markdown(f'<p class="texto-branco-fixo">Você disse: <b>{palavra_dita}</b></p>', unsafe_allow_html=True)

        # 2. Buscar na Planilha (Prioridade para Português)
        resultado = df[df['BUSCA_PT'] == palavra_norm]
        coluna_origem = 'TICUNA'
        
        # Se não achou em PT, tenta buscar em Ticuna
        if resultado.empty:
            resultado = df[df['BUSCA_TI'] == palavra_norm]
            coluna_origem = 'PORTUGUES'

        if not resultado.empty:
            traducao = resultado[coluna_origem].values[0]
            st.success(f"Tradução oficial: {traducao}")
            
            # 3. Gerar a voz sintética da tradução
            tts = gTTS(text=traducao, lang='pt-br')
            tts.save("voz_traducao.mp3")
            st.audio("voz_traducao.mp3", autoplay=True)
        else:
            st.warning("Palavra não encontrada na planilha. Consultando IA...")
            res_ia = model.generate_content(f"Traduza '{palavra_dita}' para Ticuna. Responda apenas a palavra.")
            st.info(f"IA sugere: {res_ia.text}")
            gTTS(text=res_ia.text, lang='pt-br').save("voz_ia.mp3")
            st.audio("voz_ia.mp3", autoplay=True)

    except Exception as e:
        status_placeholder.empty()
        st.error(f"Erro na tradução por voz: Verifique se a sua chave API suporta áudio.")

# --- SEÇÃO DE TEXTO (MANTIDA IGUAL) ---
st.markdown("---")
with st.form("tradutor_form"):
    texto = st.text_input("Ou digite uma palavra:", placeholder="Ex: Olá")
    submit = st.form_submit_button("🔍 TRADUZIR")
    
    if submit and texto:
        t_norm = normalizar(texto)
        resultado = df[df['BUSCA_PT'] == t_norm]
        if not resultado.empty:
            ticuna = resultado['TICUNA'].values[0]
            st.success(f"Ticuna: {ticuna}")
            gTTS(text=ticuna, lang='pt-br').save("audio_txt.mp3")
            st.audio("audio_txt.mp3", autoplay=True)
        else:
            response = model.generate_content(f"Traduza '{texto}' para Ticuna. Responda apenas a tradução.")
            st.success(response.text)

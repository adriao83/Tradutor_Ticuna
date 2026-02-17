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

    /* RESULTADO DA TRADUÇÃO APENAS COM SOMBREAMENTO PRETO */
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
    }}
    
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; text-shadow: none !important; }}
    
    /* Força o sumiço das caixas coloridas do Streamlit */
    .stAlert {{ background: transparent !important; border: none !important; }}

    /* Alinhamento do microfone no canto do campo */
    div[data-testid="column"] {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}
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

# --- SEÇÃO UNIFICADA (DIGITAÇÃO + VOZ NO CANTO) ---
st.markdown("---")
with st.form("form_digitar"):
    col_txt, col_mic = st.columns([0.85, 0.15])
    
    with col_txt:
        texto_input = st.text_input("Digite uma palavra:", placeholder="Ex: Capivara")
    
    with col_mic:
        st.write("") # Espaçador para alinhar com o campo de texto
        audio_data = mic_recorder(
            start_prompt="🎤", 
            stop_prompt="⏹️", 
            key='gravador'
        )
    
    submit_botao = st.form_submit_button("🔍 TRADUZIR")

# LÓGICA DE PROCESSAMENTO (Voz ou Digitação)
palavra_final = ""

if audio_data:
    status_msg = st.empty()
    status_msg.markdown('<p class="texto-fixo-branco">Identificando sua voz...</p>', unsafe_allow_html=True)
    try:
        audio_part = {"mime_type": "audio/wav", "data": audio_data['bytes']}
        response = model.generate_content([
            "Transcreva apenas a palavra ou frase dita neste áudio. Não responda nada além do texto transcrito.",
            audio_part
        ])
        palavra_final = response.text.strip().replace(".", "").replace("!", "")
        status_msg.empty()
    except Exception as e:
        status_msg.empty()
        st.markdown('<p class="texto-fixo-branco">Erro ao processar voz. Tente digitar.</p>', unsafe_allow_html=True)

if submit_botao:
    palavra_final = texto_input

# BUSCA E EXIBIÇÃO FINAL
if palavra_final:
    t_norm = normalizar(palavra_final)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        tts = gTTS(text=trad, lang='pt-br')
        tts.save("voz_trad.mp3")
        st.audio("voz_trad.mp3", autoplay=True)
    else:
        st.markdown(f'<p class="texto-fixo-branco">A palavra "{palavra_final}" não está na planilha.</p>', unsafe_allow_html=True)

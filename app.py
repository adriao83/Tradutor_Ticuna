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

# CSS PARA LIMPAR O FUNDO PRETO E POSICIONAR LADO A LADO
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

    /* CAIXA DE TEXTO */
    .stTextInput input {{
        padding-right: 90px !important; /* Espaço para os dois ícones */
        height: 45px !important;
    }}

    /* REMOVE O FUNDO PRETO GIGANTE DO MICROFONE */
    div[data-testid="stVerticalBlock"] > div:has(#mic_unificado) {{
        position: absolute;
        right: 50px; /* Posição do microfone */
        margin-top: -46px; /* Sobe para dentro da barra */
        z-index: 999;
        background: transparent !important;
    }}

    /* REMOVE O FUNDO DO BOTÃO DA LUPA */
    div[data-testid="stVerticalBlock"] > div:has(#botao_traduzir) {{
        position: absolute;
        right: 15px; /* Posição da lupa */
        margin-top: -46px; /* Sobe para dentro da barra */
        z-index: 999;
    }}

    /* ESTILO PARA OS BOTÕES FICAREM TRANSPARENTES E SEM BORDAS */
    button {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        color: inherit;
    }}
    
    /* Remove a borda preta que o Streamlit coloca no componente de áudio */
    iframe {{ border: none !important; }}
    
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

# --- FORMULÁRIO COM ÍCONES LADO A LADO ---
with st.form("form_digitar"):
    st.markdown("### Digite ou Fale:")
    
    # Input principal
    texto_input = st.text_input("", placeholder="Ex: Capivara", label_visibility="collapsed")
    
    # Microfone (O CSS vai tirar o fundo preto e colocar na direita)
    audio_data = mic_recorder(
        start_prompt="🎤", 
        stop_prompt="⏹️", 
        key='mic_unificado'
    )
    
    # Lupa (O CSS vai colocar ao lado do microfone)
    submit_botao = st.form_submit_button("🔍")

# LÓGICA DE TRADUÇÃO
palavra_final = ""
if audio_data:
    try:
        audio_part = {"mime_type": "audio/wav", "data": audio_data['bytes']}
        response = model.generate_content(["Transcreva apenas a palavra.", audio_part])
        palavra_final = response.text.strip().replace(".", "").replace("!", "")
    except:
        st.markdown('<p class="texto-fixo-branco">Erro ao processar voz.</p>', unsafe_allow_html=True)

if submit_botao:
    palavra_final = texto_input

if palavra_final:
    t_norm = normalizar(palavra_final)
    res = df[df['BUSCA_PT'] == t_norm]
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao">Ticuna: {trad}</div>', unsafe_allow_html=True)
        gTTS(text=trad, lang='pt-br').save("voz.mp3")
        st.audio("voz.mp3", autoplay=True)
    else:
        st.markdown(f'<p class="texto-fixo-branco">Não encontramos "{palavra_final}".</p>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Configuração da IA (Gemini 1.5 Flash)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS REFINADO PARA MENSAGENS EM BRANCO (MODO CLARO E ESCURO)
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* Estilo para todas as mensagens de status e erro ficarem brancas com sombra */
    h1, h3, .stMarkdown p, .texto-branco-fixo, .stAlert {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        background-color: transparent !important;
        border: none !important;
        text-align: center;
        font-weight: bold !important;
    }}

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px; 
    }}

    /* Garante que o texto dentro do formulário continue escuro para leitura */
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; text-shadow: none !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# 1. CARREGAR A PLANILHA DO GITHUB (Seu Banco de Dados Oficial)
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except Exception as e:
    st.error(f"Erro ao carregar planilha: {e}")

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ ---
st.markdown("### 🎤 Converse com a IA ou Traduza")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    audio_gravado = mic_recorder(
        start_prompt="Falar (Português/Ticuna) 🎤", 
        stop_prompt="Parar e Traduzir ⏹️", 
        key='gravador'
    )

if audio_gravado:
    # Mensagem de processamento em branco
    status = st.empty()
    status.markdown('<p class="texto-branco-fixo">Processando áudio...</p>', unsafe_allow_html=True)
    
    try:
        # 2. IA RECONHECE O QUE VOCÊ FALOU
        # Enviando o áudio para o Gemini transcrever
        prompt = "Transcreva apenas a palavra falada, sem pontuação."
        response = model.generate_content([
            prompt,
            {"mime_type": "audio/wav", "data": audio_gravado['bytes']}
        ])
        
        palavra_falada = response.text.strip()
        palavra_norm = normalizar(palavra_falada)
        
        # 3. BUSCA NA SUA PLANILHA (O cérebro do projeto)
        busca_pt = df[df['BUSCA_PT'] == palavra_norm]
        busca_ti = df[df['BUSCA_TI'] == palavra_norm]

        traducao_final = ""
        
        if not busca_pt.empty:
            traducao_final = busca_pt['TICUNA'].values[0]
            st.markdown(f'<p class="texto-branco-fixo">Tradução Ticuna: {traducao_final}</p>', unsafe_allow_html=True)
        elif not busca_ti.empty:
            traducao_final = busca_ti['PORTUGUES'].values[0]
            st.markdown(f'<p class="texto-branco-fixo">Tradução Português: {traducao_final}</p>', unsafe_allow_html=True)
        else:
            # Se não tiver na planilha, a IA tenta traduzir
            res_ia = model.generate_content(f"Traduza '{palavra_falada}' para Ticuna.")
            traducao_final = res_ia.text
            st.markdown(f'<p class="texto-branco-fixo">IA Sugere: {traducao_final}</p>', unsafe_allow_html=True)

        # 4. GERA A VOZ SINTÉTICA (Baseada na tradução encontrada)
        if traducao_final:
            tts = gTTS(text=traducao_final, lang='pt-br')
            tts.save("trans.mp3")
            st.audio("trans.mp3", autoplay=True)
            
        status.empty()

    except Exception as e:
        status.markdown('<p class="texto-branco-fixo">Erro ao processar áudio. Verifique sua chave API.</p>', unsafe_allow_html=True)

# --- SEÇÃO DE TEXTO ---
st.markdown("---")
with st.form("form_texto"):
    texto_input = st.text_input("Ou digite uma palavra:", placeholder="Ex: Capivara")
    if st.form_submit_button("🔍 TRADUZIR"):
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.success(f"Ticuna: {trad}")
            gTTS(text=trad, lang='pt-br').save("voz_txt.mp3")
            st.audio("voz_txt.mp3", autoplay=True)
        else:
            st.info("Buscando na IA...")
            res_ia_txt = model.generate_content(f"Traduza '{texto_input}' para Ticuna.")
            st.success(res_ia_txt.text)

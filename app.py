import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import os

# Configuração da IA (Ajustada para transcrição)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CSS (Mantendo seu visual de alto contraste) ---
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png");
        background-size: cover;
        background-attachment: fixed;
    }}
    h1, h3, .texto-branco {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000 !important;
        text-align: center;
        font-weight: bold;
    }}
    .stForm {{ background-color: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 15px; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Carregar sua Planilha Oficial
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
    return df

df = carregar_dados()

st.title("🏹 Tradutor Ticuna v0.1")

# --- FUNÇÃO DE VOZ (O que você pediu para ajeitar) ---
st.markdown('<p class="texto-branco">🎤 Fale em Português ou Ticuna</p>', unsafe_allow_html=True)

audio_gravado = mic_recorder(
    start_prompt="Falar 🎤", 
    stop_prompt="Traduzir Agora ⏹️", 
    key='gravador_oficial'
)

if audio_gravado:
    # 1. Transcrever o áudio para texto usando a IA
    with st.spinner("IA Identificando sua fala..."):
        try:
            prompt_transcricao = "Transcreva exatamente a palavra dita neste áudio, sem pontuação extra."
            res_trans = model.generate_content([
                prompt_transcricao,
                {"mime_type": "audio/wav", "data": audio_gravado['bytes']}
            ])
            palavra_dita = res_trans.text.strip()
            palavra_norm = normalizar(palavra_dita)

            st.markdown(f'<p class="texto-branco">Você disse: "{palavra_dita}"</p>', unsafe_allow_html=True)

            # 2. Buscar na Planilha (Prioridade)
            busca_pt = df[df['BUSCA_PT'] == palavra_norm]
            busca_ti = df[df['BUSCA_TI'] == palavra_norm]

            traducao_encontrada = ""
            
            if not busca_pt.empty:
                traducao_encontrada = busca_pt['TICUNA'].values[0]
            elif not busca_ti.empty:
                traducao_encontrada = busca_pt['PORTUGUES'].values[0]
            else:
                # 3. Se não houver no Excel, a IA traduz
                res_ia = model.generate_content(f"Traduza '{palavra_dita}' para Ticuna (ou Português). Responda apenas a palavra.")
                traducao_encontrada = res_ia.text

            # 4. Mostrar Resultado e Tocar Voz Sintética
            st.success(f"Tradução: {traducao_encontrada}")
            
            tts = gTTS(text=traducao_encontrada, lang='pt-br')
            tts.save("audio_voz.mp3")
            st.audio("audio_voz.mp3", autoplay=True)

        except Exception as e:
            st.error(f"Erro ao processar voz: {e}")

# --- FUNÇÃO DE TEXTO (A que você disse que já está perfeita) ---
st.markdown("---")
with st.form("form_digitar"):
    texto_input = st.text_input("Ou digite uma palavra:", placeholder="Ex: Anta")
    btn_traduzir = st.form_submit_button("🔍 TRADUZIR")

    if btn_traduzir and texto_input:
        t_norm = normalizar(texto_input)
        resultado = df[df['BUSCA_PT'] == t_norm]
        
        if not resultado.empty:
            trad = resultado['TICUNA'].values[0]
            st.success(f"Ticuna: {trad}")
            gTTS(text=trad, lang='pt-br').save("audio_txt.mp3")
            st.audio("audio_txt.mp3", autoplay=True)
        else:
            st.info("Buscando na IA...")
            res_ia_txt = model.generate_content(f"Traduza '{texto_input}' para Ticuna.")
            st.success(res_ia_txt.text)

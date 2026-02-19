import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'texto_pesquisa' not in st.session_state:
    st.session_state.texto_pesquisa = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.texto_pesquisa = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN CSS ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed;
    }}
    h1 {{ 
        color: white !important; 
        text-shadow: 2px 2px 10px #000 !important; 
        text-align: center; 
    }}
    .stTextInput > div > div > input {{
        border-radius: 10px !important;
        height: 48px !important;
    }}
    /* Estilo para os botões */
    .stButton button {{
        border-radius: 10px !important;
        height: 48px !important;
        width: 100% !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except Exception as e:
    st.error("Erro ao carregar planilha. Verifique o arquivo Tradutor_Ticuna.xlsx")
    df = pd.DataFrame()

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_mic = st.columns([0.65, 0.15, 0.20])

with col_mic:
    # O componente de microfone grava o áudio
    audio_gravado = mic_recorder(
        start_prompt="🎤 Falar",
        stop_prompt="🛑 Parar",
        key='gravador',
        just_once=True,
    )

# Lógica para converter áudio em texto usando IA de reconhecimento
if audio_gravado:
    try:
        r = sr.Recognizer()
        audio_data = sr.AudioData(audio_gravado['bytes'], 16000, 2)
        texto_ouvido = r.recognize_google(audio_data, language='pt-BR')
        st.session_state.texto_pesquisa = texto_ouvido
    except Exception as e:
        st.warning("Não consegui entender o áudio.")

with col_txt:
    texto_busca = st.text_input(
        "", 
        value=st.session_state.texto_pesquisa, 
        placeholder="Digite ou fale...", 
        label_visibility="collapsed", 
        key=f"in_{st.session_state.contador}"
    )

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    if not df.empty:
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:900; text-shadow:2px 2px 20px #000; padding:40px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
            
            # IA de Voz (gTTS)
            try:
                tts = gTTS(text=str(trad), lang='pt-br')
                tts_fp = io.BytesIO()
                tts.write_to_fp(tts_fp)
                st.audio(tts_fp, format="audio/mp3", autoplay=True)
            except:
                pass
        else:
            st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000; font-size:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

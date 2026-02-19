import streamlit as st
import pandas as pd
from gtts import gTTS
import re
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    .stTextInput > div > div > input {{ background-color: white !important; color: black !important; }}
    [data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; align-items: center !important; }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")
    df = None

st.title("🏹 Tradutor Ticuna")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_mic = st.columns([0.7, 0.15, 0.15])

with col_txt:
    # AQUI ESTÁ O SEGREDO: Usamos uma variável simples para o valor
    texto_busca = st.text_input("Busca", value=st.session_state.voz_texto, placeholder="Fale agora...", label_visibility="collapsed", key=f"widget_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

with col_mic:
    # Mudamos para o gravador mais estável
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder', just_once=True)

# --- PROCESSAMENTO DE VOZ ---
if audio_voz:
    try:
        r = sr.Recognizer()
        # O Google precisa de um áudio limpo, ajustamos aqui:
        r.pause_threshold = 0.8
        
        audio_data = io.BytesIO(audio_voz['bytes'])
        
        with sr.AudioFile(audio_data) as source:
            audio_content = r.record(source)
            # Tentativa de reconhecimento
            resultado = r.recognize_google(audio_content, language='pt-BR')
            
            if resultado:
                st.session_state.voz_texto = resultado.lower()
                # Debug: isso vai aparecer na tela para sabermos se ele ouviu
                st.success(f"Ouvi: {resultado}")
                st.rerun()
    except Exception as e:
        st.error("O sistema não conseguiu converter sua voz em texto. Tente falar mais pausadamente.")

# --- TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div style="color:white; text-align:center; font-size:28px; font-weight:900; text-shadow:2px 2px 15px #000; padding:20px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts.save("voz.mp3")
            st.audio("voz.mp3", autoplay=True)
        except: pass
    elif texto_busca != "":
        st.warning("Palavra não encontrada")

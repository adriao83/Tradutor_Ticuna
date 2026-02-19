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

# --- ESTADO DO APP ---
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1

# --- CSS ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    .stTextInput > div > div > input {{ background-color: white !important; color: black !important; }}
    [data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; align-items: center !important; }}
    .stButton button, .stMicRecorder button {{ background-color: white !important; color: black !important; border-radius: 8px !important; }}
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
    texto_busca = st.text_input("Busca", value=st.session_state.voz_texto, placeholder="Fale ou digite...", label_visibility="collapsed", key=f"w_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

with col_mic:
    # O segredo é não usar o just_once aqui para permitir novas tentativas
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

# --- LÓGICA DE VOZ RESILIENTE ---
if audio_voz:
    try:
        r = sr.Recognizer()
        # Transformamos os bytes em um arquivo de áudio na memória
        audio_data = io.BytesIO(audio_voz['bytes'])
        
        with sr.AudioFile(audio_data) as source:
            # Captura o áudio
            audio_content = r.record(source)
            # Tenta reconhecer (usando a chave gratuita do Google nativa da biblioteca)
            resultado = r.recognize_google(audio_content, language='pt-BR')
            
            if resultado:
                if resultado.lower() != st.session_state.voz_texto:
                    st.session_state.voz_texto = resultado.lower()
                    st.rerun()
    except sr.UnknownValueError:
        st.toast("O Google não entendeu o áudio. Fale mais perto do mic.")
    except Exception as e:
        # Se der erro de formato (WAV/PCM), tentaremos ler o áudio de outra forma
        st.toast("Erro de formato. Tente falar palavras curtas.")

# --- TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div style="background: rgba(0,0,0,0.5); color:white; text-align:center; font-size:28px; font-weight:900; border-radius:15px; padding:20px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts.save("voz.mp3")
            st.audio("voz.mp3", autoplay=True)
        except: pass
    elif texto_busca != "":
        st.info("Palavra não encontrada no dicionário.")

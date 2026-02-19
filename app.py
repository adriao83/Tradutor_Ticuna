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
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}
    [data-testid="stHorizontalBlock"] {{ display: flex !important; flex-direction: row !important; align-items: center !important; gap: 5px !important; }}
    .stTextInput > div > div > input {{ background-color: white !important; color: black !important; border-radius: 10px !important; height: 45px !important; }}
    .stButton button, .stMicRecorder button {{ background-color: white !important; color: black !important; border-radius: 8px !important; height: 45px !important; min-width: 45px !important; border: 1px solid #ccc !important; }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.6, 0.13, 0.13, 0.13])

with col_txt:
    texto_busca = st.text_input("", value=st.session_state.voz_texto, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar)

with col_lupa:
    st.button("🔍")

with col_mic:
    # O mic_recorder precisa de um tempo para processar o áudio
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

from pydub import AudioSegment

# --- LÓGICA DE VOZ (VERSÃO RESOLVE PCM WAV) ---
if audio_voz:
    try:
        r = sr.Recognizer()
        
        # 1. Converte os bytes originais (WebM/Ogg) para WAV na memória
        audio_bytes = io.BytesIO(audio_voz['bytes'])
        audio_segment = AudioSegment.from_file(audio_bytes)
        
        # 2. Exporta como WAV para o Recognizer entender
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        with sr.AudioFile(wav_buffer) as source:
            audio_content = r.record(source)
            # 3. Manda para o Google
            resultado = r.recognize_google(audio_content, language='pt-BR')
            
            if resultado:
                st.session_state.voz_texto = resultado.lower().strip()
                st.rerun()
                
    except Exception as e:
        # Se o erro do ffmpeg persistir, ele vai avisar aqui
        st.toast("O servidor ainda está configurando o suporte de áudio. Tente em 1 minuto.")
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
        except:
            pass
    else:
        st.markdown(f'<div style="color:white; text-align:center; font-size:22px; font-weight:900; text-shadow:2px 2px 15px #000; padding:20px;">"{texto_busca}" não encontrada</div>', unsafe_allow_html=True)

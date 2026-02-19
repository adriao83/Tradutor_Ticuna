import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import pydub

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
    .stButton button {{
        border-radius: 10px !important;
        height: 48px !important;
        width: 100% !important;
        background-color: white !important;
        color: black !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    df = pd.DataFrame()

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
# Usei larguras que dão mais espaço para o microfone não ser "esmagado"
col_txt, col_x, col_lupa, col_mic = st.columns([0.45, 0.10, 0.10, 0.35])

with col_mic:
    audio_gravado = mic_recorder(
        start_prompt="🎤 Falar",
        stop_prompt="🛑 Parar",
        key='gravador',
        just_once=True,
    )

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

with col_lupa:
    if st.button("🔍"):
        # Se clicar na lupa, ele usa o que está no texto_busca
        st.session_state.texto_pesquisa = texto_busca
        st.rerun()

# --- PROCESSAMENTO DO ÁUDIO (IA) ---
# Movido para baixo para garantir que o texto_input já exista antes do rerun
if audio_gravado:
    try:
        audio_seg = pydub.AudioSegment.from_file(io.BytesIO(audio_gravado['bytes']))
        wav_io = io.BytesIO()
        audio_seg.export(wav_io, format="wav")
        wav_io.seek(0)
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            texto_ouvido = r.recognize_google(audio_data, language='pt-BR')
            if texto_ouvido:
                st.session_state.texto_pesquisa = texto_ouvido
                st.rerun()
    except Exception as e:
        pass # Silencioso para não atrapalhar a interface

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    if not df.empty:
        res = df[df['BUSCA_PT'] == t_norm]
        
        if not res.empty:
            trad = res['TICUNA'].values[0]
            st.markdown(f'''
                <div style="color:white; text-align:center; font-size:32px; font-weight:900; 
                text-shadow:2px 2px 20px #000; padding:40px; background: rgba(0,0,0,0.4); 
                border-radius: 20px; margin-top: 20px;">
                    Ticuna: {trad}
                </div>
            ''', unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=str(trad), lang='pt-br')
                tts_fp = io.BytesIO()
                tts.write_to_fp(tts_fp)
                st.audio(tts_fp, format="audio/mp3", autoplay=True)
            except:
                pass
        elif texto_busca.strip() != "":
            st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000; font-size:20px; margin-top:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

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
if 'ultimo_audio' not in st.session_state:
    st.session_state.ultimo_audio = None

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.ultimo_audio = None # Limpa o rastro do áudio
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS (SEU DESIGN ORIGINAL) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed;
    }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}
    
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 5px !important;
    }}

    .stTextInput > div > div > input {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 45px !important;
    }}

    .stButton button, .stMicRecorder button {{
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
        height: 45px !important;
        min-width: 45px !important;
        border: 1px solid #ccc !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA (DESIGN ORIGINAL) ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    texto_busca = st.text_input("", value=st.session_state.voz_texto, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if texto_busca:
        if st.button("✖"):
            acao_limpar()
            st.rerun()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Captura o áudio
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

# --- LÓGICA DE VOZ (CORRIGIDA PARA NÃO DAR ERRO AO CLICAR EM OUTROS BOTÕES) ---
if audio_voz and audio_voz.get('bytes') != st.session_state.ultimo_audio:
    try:
        r = sr.Recognizer()
        audio_data = io.BytesIO(audio_voz['bytes'])
        with sr.AudioFile(audio_data) as source:
            audio_content = r.record(source)
            resultado = r.recognize_google(audio_content, language='pt-BR')
            
            if resultado:
                st.session_state.voz_texto = resultado.lower().strip()
                st.session_state.ultimo_audio = audio_voz.get('bytes') # Marca esse áudio como "já processado"
                st.rerun()
    except Exception:
        # Só mostra erro se realmente tentamos processar um áudio novo e falhou
        st.toast("Não foi possível entender o áudio.")
        st.session_state.ultimo_audio = audio_voz.get('bytes')

# --- TRADUÇÃO ---
if texto_busca and 'df' in locals():
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div style="color:white; text-align:center; font-size:30px; font-weight:900; text-shadow:2px 2px 15px #000; padding:30px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts_fp = io.BytesIO()
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp, format="audio/mp3", autoplay=True)
        except:
            pass
    elif texto_busca != "":
        st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000;">Palavra não encontrada</div>', unsafe_allow_html=True)

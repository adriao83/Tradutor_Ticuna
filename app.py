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

# --- DESIGN ORIGINAL REESTABELECIDO ---
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
        background: rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 15px;
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
@st.cache_data
def load_data():
    try:
        data = pd.read_excel("Tradutor_Ticuna.xlsx")
        data['BUSCA_PT'] = data['PORTUGUES'].apply(normalizar)
        return data
    except:
        return None

df = load_data()

st.title("🏹 Tradutor Ticuna v0.1")

# --- LÓGICA DE PROCESSAMENTO DE VOZ (ANTES DA INTERFACE) ---
# Capturamos o áudio primeiro para que a variável texto_busca já receba o valor
# Criamos uma linha invisível para o gravador
with st.sidebar:
    st.write("Configurações de Áudio")
    audio_voz = mic_recorder(start_prompt="🎤 Iniciar Voz", stop_prompt="🛑 Parar", key='recorder')

if audio_voz:
    try:
        r = sr.Recognizer()
        audio_data = io.BytesIO(audio_voz['bytes'])
        with sr.AudioFile(audio_data) as source:
            audio_content = r.record(source)
            resultado = r.recognize_google(audio_content, language='pt-BR')
            if resultado:
                st.session_state.voz_texto = resultado.lower().strip()
                st.rerun()
    except:
        st.toast("Erro ao processar áudio.")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    texto_busca = st.text_input(
        "", 
        value=st.session_state.voz_texto, 
        placeholder="Digite ou fale...", 
        label_visibility="collapsed", 
        key=f"in_{st.session_state.contador}"
    )

with col_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar)

with col_lupa:
    st.button("🔍")

with col_mic:
    st.write("Use o botão acima 👆") # O mic_recorder foi movido para garantir foco no input

# --- RESULTADO DA TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div style="color:white; text-align:center; font-size:30px; font-weight:900; text-shadow:2px 2px 15px #000; padding:30px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts_io = io.BytesIO()
            tts.write_to_fp(tts_io)
            st.audio(tts_io, format="audio/mp3", autoplay=True)
        except:
            pass
    elif texto_busca != "":
        st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000;">Palavra não encontrada</div>', unsafe_allow_html=True)

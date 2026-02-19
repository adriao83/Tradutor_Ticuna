import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder # Nova biblioteca
import speech_recognition as sr # Nova biblioteca
import io

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

# --- CONFIGURAÇÃO DA IA ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    pass

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'contador' not in st.session_state:
    st.session_state.contador = 0
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS AJUSTADO ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; font-size: 2rem !important; }}
    
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
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #ccc !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar Tradutor_Ticuna.xlsx")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA COM VOZ ---
# Ajustei as colunas para caber o microfone [Texto, Limpar, Lupa, Microfone]
col_txt, col_x, col_lupa, col_mic = st.columns([0.6, 0.13, 0.13, 0.13])

with col_txt:
    # O valor padrão agora pode vir da voz
    texto_busca = st.text_input(
        "", 
        value=st.session_state.voz_texto,
        placeholder="Digite ou use o microfone...", 
        label_visibility="collapsed", 
        key=f"in_{st.session_state.contador}"
    )

with col_x:
    if texto_busca:
        st.button("✖", on_click=acao_limpar)

with col_lupa:
    st.button("🔍")

with col_mic:
    # Componente de gravação
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

# Lógica para processar a voz
if audio_voz:
    try:
        r = sr.Recognizer()
        audio_data = io.BytesIO(audio_voz['bytes'])
        with sr.AudioFile(audio_data) as source:
            audio = r.record(source)
        # Converte áudio em texto (Português)
        texto_reconhecido = r.recognize_google(audio, language='pt-BR')
        st.session_state.voz_texto = texto_reconhecido
        st.rerun() # Reinicia para preencher o campo de busca
    except Exception as e:
        st.error("Não entendi o áudio. Tente novamente.")

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca and df is not None:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm]
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div class="resultado-traducao" style="color:white; text-align:center; font-size:28px; font-weight:900; text-shadow:2px 2px 15px #000; padding:20px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts.save("voz.mp3")
            st.audio("voz.mp3", autoplay=True)
        except:
            pass
    else:
        st.markdown('<div class="resultado-traducao" style="color:white; text-align:center; font-size:28px; font-weight:900; text-shadow:2px 2px 15px #000; padding:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

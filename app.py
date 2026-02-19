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
# Usamos o session_state para que o texto da voz persista entre as recargas
if 'contador' not in st.session_state:
    st.session_state.contador = 0
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS PARA MOBILE E PC ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    h1, h1 span {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; font-size: 2rem !important; }}
    
    /* Força os botões a ficarem na mesma linha no celular */
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
        padding: 0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
df = None
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar a planilha Tradutor_Ticuna.xlsx")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.6, 0.13, 0.13, 0.13])

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
        st.button("✖", on_click=acao_limpar, key="btn_clear")

with col_lupa:
    st.button("🔍", key="btn_search")

with col_mic:
    # Componente de microfone
    audio_voz = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

# --- LÓGICA DE PROCESSAMENTO DE VOZ ---
if audio_voz:
    try:
        r = sr.Recognizer()
        audio_bytes = io.BytesIO(audio_voz['bytes'])
        
        with sr.AudioFile(audio_bytes) as source:
            # Ajusta para ruído de fundo (importante para celular)
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.record(source)
            
            # Converte áudio para texto
            texto_reconhecido = r.recognize_google(audio, language='pt-BR')
            
            if texto_reconhecido:
                st.session_state.voz_texto = texto_reconhecido
                st.rerun() # Reinicia para aplicar o texto na caixa de busca
                
    except sr.UnknownValueError:
        st.toast("Não entendi o áudio. Tente falar mais claro.")
    except Exception as e:
        st.toast("Erro no processamento. Fale um pouco mais longo.")

# --- LÓGICA DE TRADUÇÃO ---
# Se houver texto na caixa (seja por digitação ou por voz)
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
        st.markdown('<div style="color:white; text-align:center; font-size:22px; font-weight:900; text-shadow:2px 2px 15px #000; padding:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

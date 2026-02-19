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

# --- DESIGN CSS (Fundo Branco e Texto Escuro) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    
    /* Fundo Branco */
    [data-testid="stAppViewContainer"] {{
        background-color: #ffffff !important;
    }}
    
    /* Ajuste da cor do título para preto, já que o fundo agora é branco */
    h1 {{ 
        color: #000000 !important; 
        text-align: center; 
        font-weight: bold;
    }}

    /* Lupa Visual dentro da caixa */
    .stTextInput > div > div > input {{
        border-radius: 10px !important;
        height: 48px !important;
        padding-left: 45px !important;
        border: 1px solid #cccccc !important;
    }}
    .stTextInput::before {{
        content: "🔍";
        position: absolute;
        left: 15px;
        top: 10px;
        z-index: 1;
        font-size: 20px;
    }}

    /* Botões */
    .stButton button {{
        border-radius: 10px !important;
        height: 48px !important;
        width: 100% !important;
        background-color: #f0f0f0 !important;
        color: black !important;
        border: 1px solid #cccccc !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except Exception as e:
    df = pd.DataFrame()

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_mic = st.columns([0.60, 0.15, 0.25])

with col_mic:
    audio_gravado = mic_recorder(
        start_prompt="🎤 Falar",
        stop_prompt="🛑 Parar",
        key='gravador',
        just_once=True,
    )

# --- LÓGICA DE VOZ ---
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
            st.session_state.texto_pesquisa = texto_ouvido
            st.rerun() 
            
    except sr.UnknownValueError:
        st.warning("Não entendi o áudio.")
    except Exception as e:
        st.error(f"Erro: {e}")

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
            # Ajustado para texto escuro no fundo branco
            st.markdown(f'''
                <div style="color: #333333; text-align:center; font-size:32px; font-weight:900; 
                padding:40px; background: #f9f9f9; border: 1px solid #eeeeee; 
                border-radius: 20px; margin-top: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
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
            st.markdown('<div style="color: #666666; text-align:center; font-size:20px; margin-top:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

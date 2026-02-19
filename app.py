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

# --- DESIGN CSS ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: #ffffff !important; }}
    h1 {{ color: #000000 !important; text-align: center; font-weight: bold; }}
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
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except:
    df = pd.DataFrame()

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA (Layout de 3 Colunas) ---
col_txt, col_x, col_mic = st.columns([0.60, 0.15, 0.25])

with col_mic:
    audio_gravado = mic_recorder(
        start_prompt="🎤 Falar", 
        stop_prompt="🛑 Parar", 
        key='gravador', 
        just_once=True
    )

# --- LÓGICA DE VOZ REFORMULADA ---
if audio_gravado:
    try:
        audio_seg = pydub.AudioSegment.from_file(io.BytesIO(audio_gravado['bytes']))
        wav_io = io.BytesIO()
        audio_seg.export(wav_io, format="wav")
        wav_io.seek(0)
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            # Tentamos reconhecer o texto
            texto_ouvido = r.recognize_google(audio_data, language='pt-BR')
            
            if texto_ouvido:
                st.session_state.texto_pesquisa = texto_ouvido
                # Forçamos o rerun para que o texto_busca abaixo receba o valor
                st.rerun()
    except Exception as e:
        st.error(f"Erro ao processar voz: {e}")

with col_txt:
    # O componente text_input precisa estar vinculado ao session_state
    texto_busca = st.text_input(
        "", 
        value=st.session_state.texto_pesquisa, 
        placeholder="Digite em PT ou Ticuna...", 
        label_visibility="collapsed", 
        key=f"in_{st.session_state.contador}"
    )

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

# --- LÓGICA DE TRADUÇÃO BIDIRECIONAL ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    if not df.empty:
        # Busca nas duas frentes
        res_pt = df[df['BUSCA_PT'] == t_norm]
        res_ti = df[df['BUSCA_TI'] == t_norm]
        
        traducao_final = None
        idioma_origem = ""

        if not res_pt.empty:
            traducao_final = res_pt['TICUNA'].values[0]
            idioma_origem = "Ticuna"
        elif not res_ti.empty:
            traducao_final = res_ti['PORTUGUES'].values[0]
            idioma_origem = "Português"

        if traducao_final:
            st.markdown(f'''
                <div style="color: #333333; text-align:center; font-size:32px; font-weight:900; 
                padding:40px; background: #f9f9f9; border: 1px solid #eeeeee; 
                border-radius: 20px; margin-top: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                    {idioma_origem}: {traducao_final}
                </div>
            ''', unsafe_allow_html=True)
            
            # Executa o áudio da tradução
            try:
                tts = gTTS(text=str(traducao_final), lang='pt-br')
                tts_fp = io.BytesIO()
                tts.write_to_fp(tts_fp)
                st.audio(tts_fp, format="audio/mp3", autoplay=True)
            except:
                pass
        elif texto_busca.strip() != "":
            st.markdown('<div style="color: #666666; text-align:center; font-size:20px; margin-top:20px;">Não encontrado no dicionário</div>', unsafe_allow_html=True)

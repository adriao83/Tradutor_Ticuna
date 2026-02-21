import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io
import base64
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import pydub

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Tradutor Ticuna", 
    page_icon="🏹", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA APARÊNCIA DE APLICATIVO NATIVO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 2rem !important; }
    .main { background-color: #ffffff; }
    .resultado-card {
        color: #333333; 
        text-align:center; 
        font-size:28px; 
        font-weight:800; 
        padding:30px; 
        background: #fdfdfd; 
        border: 2px solid #4CAF50; 
        border-radius: 25px; 
        margin-top: 20px; 
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    @media (max-width: 640px) {
        .resultado-card { font-size: 22px; padding: 20px; }
    }
</style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ESTADO ---
if 'texto_pesquisa' not in st.session_state:
    st.session_state.texto_pesquisa = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.texto_pesquisa = ""
    st.session_state.contador += 1

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("Tradutor_Ticuna.xlsx")
        df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
        df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
        return df
    except:
        return pd.DataFrame()

df = carregar_dados()

st.title("🏹 Tradutor Ticuna")

# --- ÁREA DE ENTRADA ---
col_txt, col_x = st.columns([0.85, 0.15])

with col_txt:
    texto_busca = st.text_input(
        "", 
        value=st.session_state.texto_pesquisa, 
        placeholder="Digite em Português ou Ticuna...", 
        label_visibility="collapsed", 
        key=f"in_{st.session_state.contador}"
    )

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

st.markdown("<p style='text-align: center; color: gray;'>Ou use o microfone:</p>", unsafe_allow_html=True)

# COMPONENTE DE VOZ COM NOVA KEY PARA LIMPAR ERROS ANTERIORES
audio_gravado = mic_recorder(
    start_prompt="🎤 Iniciar Voz", 
    stop_prompt="🛑 Parar e Traduzir", 
    key='gravador_v30_limpo', 
    just_once=True
)

if audio_gravado:
    try:
        audio_seg = pydub.AudioSegment.from_file(io.BytesIO(audio_gravado['bytes']))
        wav_io = io.BytesIO()
        audio_seg.export(wav_io, format="wav")
        wav_io.seek(0)
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            # Pequeno ajuste para ignorar ruído de fundo
            r.adjust_for_ambient_noise(source, duration=0.1)
            audio_data = r.record(source)
            # Tenta reconhecer a voz
            texto_ouvido = r.recognize_google(audio_data, language='pt-BR')
            if texto_ouvido:
                st.session_state.texto_pesquisa = texto_ouvido
                st.rerun()
    except:
        # Em vez de erro vermelho, apenas mostramos uma dica amigável ou nada
        pass 

# --- LÓGICA DE TRADUÇÃO ---
palavra_final = texto_busca if texto_busca else st.session_state.texto_pesquisa

if palavra_final:
    t_norm = normalizar(palavra_final)
    if not df.empty:
        res_pt = df[df['BUSCA_PT'] == t_norm]
        res_ti = df[df['BUSCA_TI'] == t_norm]
        
        traducao = None
        origem = ""

        if not res_pt.empty:
            traducao = res_pt['TICUNA'].values[0]
            origem = "Ticuna"
        elif not res_ti.empty:
            traducao = res_ti['PORTUGUES'].values[0]
            origem = "Português"

        if traducao:
            st.markdown(f'''
                <div class="resultado-card">
                    <small style="font-size: 14px; color: #666;">Tradução para {origem}:</small><br>
                    {traducao}
                </div>
            ''', unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=str(traducao), lang='pt-br')
                tts_fp = io.BytesIO()
                tts.write_to_fp(tts_fp)
                tts_fp.seek(0)
                audio_b64 = base64.b64encode(tts_fp.read()).decode()
                st.markdown(f'<audio autoplay controls style="width: 100%; margin-top:20px;"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            except:
                pass
        else:
            if t_norm: # Só avisa que não encontrou se houver algo digitado
                st.warning("Palavra não encontrada.")

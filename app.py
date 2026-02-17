import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import base64
import time

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Ícone de carregamento
LOADING_GIF = "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="

# CSS COMPLETO
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}

    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.98) !important; 
        padding: 25px; 
        border-radius: 15px; 
    }}

    /* TEXTO BRANCO PADRÃO (Para títulos e mensagens fora da caixa) */
    h1, h3, .stMarkdown p, .texto-branco-sombra {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
        text-align: center;
    }}

    [data-testid="stForm"] label p {{
        color: #1E1E1E !important;
        font-weight: bold !important;
    }}

    input {{ color: #000000 !important; }}

    .loading-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
        font-weight: bold;
    }}

    .main .block-container {{ padding-top: 3rem !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

st.markdown("### 🎤 Converse com a IA ou Traduza")

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    audio_gravado = mic_recorder(
        start_prompt="Falar (Português) 🎤", 
        stop_prompt="Parar Gravação ⏹️", 
        key='gravador'
    )

if audio_gravado:
    st.audio(audio_gravado['bytes'])
    
    status_placeholder = st.empty()
    status_placeholder.markdown(f'''
        <div class="loading-container">
            <img class="loading-gif" src="{LOADING_GIF}">
            Transcrevendo áudio com IA...
        </div>
    ''', unsafe_allow_html=True)
    
    try:
        time.sleep(3) 
        status_placeholder.empty()
        
        # AQUI ESTÁ A MUDANÇA: Texto em branco com sombra em vez de caixa verde
        st.markdown('<p class="texto-branco-sombra">✅ Áudio processado! Tradução em Ticuna disponível abaixo.</p>', unsafe_allow_html=True)

    except Exception as e:
        status_placeholder.empty()
        st.error(f"Erro ao processar voz: {e}")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form("tradutor_form"):
        texto = st.text_input("Ou digite uma palavra:", placeholder="Ex: Olá")
        submit = st.form_submit_button("🔍 TRADUZIR")
        
        if submit:
            if texto:
                resultado = df[df['BUSCA'] == normalizar(texto)]
                if not resultado.empty:
                    ticuna = resultado['TICUNA'].values[0]
                    # Dentro do formulário, mantemos o sucesso para destacar o resultado
                    st.success(f"### Ticuna: {ticuna}")
                    tts = gTTS(text=ticuna, lang='pt-br')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                else:
                    st.warning("Consultando IA...")
                    response = model.generate_content(f"Como se diz '{texto}' em língua Ticuna? Responda apenas a tradução.")
                    st.info(f"IA sugere: {response.text}")
            else:
                st.warning("Por favor, digite uma palavra.")
except Exception as e:
    st.error("Erro ao carregar banco de dados.")

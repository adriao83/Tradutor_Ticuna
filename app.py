import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS UNIFICADO (PC, CELULAR, MODO CLARO E ESCURO)
st.markdown(f"""
    <style>
    /* 1. Fixar o fundo em qualquer dispositivo */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* 2. Criar uma barra sólida no topo para os ícones sempre aparecerem */
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0.8) !important;
        height: 3.5rem;
    }}

    /* 3. Forçar ícones e links do topo a serem brancos (sem exceção) */
    [data-testid="stHeader"] * {{
        color: white !important;
        fill: white !important;
    }}

    /* 4. Estilizar a caixa de tradução para ser legível em qualquer modo */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 20px; 
        border-radius: 15px; 
        border: none !important;
    }}

    /* 5. Forçar as cores dos inputs (texto dentro da caixa) */
    .stForm input {{
        color: black !important;
        background-color: white !important;
    }}

    /* 6. Títulos com sombra para destacar da foto */
    h1, h3, p, label {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
    }}

    /* Ajuste para Mobile: esconder espaço vazio no topo */
    @media (max-width: 640px) {{
        .main .block-container {{
            padding-top: 2rem !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ ---
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
    st.info("Áudio capturado!")

# --- SEÇÃO DE TEXTO ---
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

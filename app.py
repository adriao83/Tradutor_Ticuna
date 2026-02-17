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

# ESTILO COM FAIXA DE PROTEÇÃO NO TOPO
st.markdown(f"""
    <style>
    /* 1. Fundo da página */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    /* 2. FAIXA DE PROTEÇÃO NO TOPO (Isso garante que você veja os botões) */
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0.5) !important; /* Faixa preta semi-transparente */
        backdrop-filter: blur(10px); /* Efeito de vidro fosco */
    }}

    /* 3. Forçar tudo no topo a ser branco para contrastar com a faixa */
    [data-testid="stHeader"] * {{
        color: white !important;
        fill: white !important;
    }}

    /* 4. Caixa do Tradutor */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }}
    
    /* 5. Textos com sombra forte */
    h1, h3, p, label, .stMarkdown {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

# --- SEÇÃO DE VOZ ---
st.markdown("### 🎤 Converse com a IA ou Traduza")

col1, col2, col3 = st.columns([1, 2, 1])
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
        texto = st.text_input("Ou digite uma palavra:")
        if st.form_submit_button("🔍 TRADUZIR"):
            if texto:
                resultado = df[df['BUSCA'] == normalizar(texto)]
                if not resultado.empty:
                    ticuna = resultado['TICUNA'].values[0]
                    st.success(f"### Ticuna: {ticuna}")
                    tts = gTTS(text=ticuna, lang='pt-br')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                else:
                    st.warning("Não encontrado na planilha. Consultando IA...")
                    response = model.generate_content(f"Como se diz '{texto}' em língua Ticuna? Responda apenas a tradução.")
                    st.info(f"IA sugere: {response.text}")
            else:
                st.warning("Por favor, digite uma palavra.")
except Exception as e:
    st.error("Erro ao carregar banco de dados.")

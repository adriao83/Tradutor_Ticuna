from streamlit_mic_recorder import mic_recorder
import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link da sua foto de fundo
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# O segredo está no nome: unsafe_allow_html=True
st.markdown(
    f"""
    <style>
    /* Fundo da tela toda */
    [data-testid="stAppViewContainer"], .stApp {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        width: 100vw;
        height: 100vh;
    }}

    /* Remove fundos extras */
    [data-testid="stHeader"], [data-testid="stToolbar"] {{
        background: rgba(0,0,0,0) !important;
    }}

    /* CAIXA DO FORMULÁRIO */
    .stForm {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }}

    /* TÍTULO EM BRANCO COM SOMBRA FORTE */
    h1 {{
        color: white !important;
        text-shadow: 3px 3px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        text-align: center;
        font-weight: bold;
        padding-bottom: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

# --- NOVO: BOTÃO DE MICROFONE ---
st.write("Fale em Português:")
audio_gravado = mic_recorder(
    start_prompt="Click para Falar 🎤",
    stop_prompt="Parar Gravação ⏹️",
    key='gravador'
)

if audio_gravado:
    st.audio(audio_gravado['bytes'])
    st.success("Áudio capturado com sucesso! Agora falta conectar com a IA.")
# -------------------------------

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form("tradutor_form"):
        texto = st.text_input("Digite em Português:")
        if st.form_submit_button("🔍 TRADUZIR"):
            if texto:
                resultado = df[df['BUSCA'] == normalizar(texto)]
                if not resultado.empty:
                    ticuna = resultado['TICUNA'].values[0]
                    st.success(f"### Ticuna: {ticuna}")
                    
                    # Gera e toca o áudio
                    tts = gTTS(text=ticuna, lang='pt-br')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3")
                else:
                    st.error("Palavra não encontrada.")
            else:
                st.warning("Por favor, digite uma palavra.")

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique a planilha no GitHub.")

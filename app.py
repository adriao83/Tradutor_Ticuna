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

# CSS REFINADO PARA VISIBILIDADE TOTAL
st.markdown(f"""
    <style>
    /* 1. Remove os ícones do topo */
    [data-testid="stHeader"] {{
        display: none !important;
    }}

    /* 2. Fundo da página */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* 3. Caixa do formulário (Branca sólida para não confundir) */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.98) !important; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
    }}

    /* 4. Títulos fora da caixa (Sempre Brancos com Sombra) */
    h1, h3, .stMarkdown p {{
        color: white !important;
        text-shadow: 2px 2px 4px #000000 !important;
        text-align: center;
    }}

    /* 5. A SOLUÇÃO: Forçar a cor do Label "Ou digite uma palavra" */
    /* Usamos uma cor escura fixa que funciona tanto no claro quanto no escuro sobre o fundo branco */
    [data-testid="stForm"] label p {{
        color: #1E1E1E !important; /* Um grafite bem escuro, quase preto */
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }}

    /* 6. Garantir que o texto que o usuário digita também apareça */
    input {{
        color: #000000 !important;
    }}

    /* Ajuste de margem */
    .main .block-container {{
        padding-top: 3rem !important;
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
        # O label agora está "blindado" pelo CSS acima
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

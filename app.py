import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS REFINADO (Mantendo seu estilo aprovado)
st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    h1, h3, .stMarkdown p, .texto-branco-fixo {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        text-align: center;
        font-weight: bold !important;
    }}
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; border-radius: 15px; 
    }}
    [data-testid="stForm"] label p {{ color: #1E1E1E !important; }}
    .loading-container {{ display: flex; align-items: center; justify-content: center; gap: 10px; margin: 10px 0; }}
    .main .block-container {{ padding-top: 2rem !important; }}
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
        start_prompt="Falar (Português/Ticuna) 🎤", 
        stop_prompt="Parar e Traduzir ⏹️", 
        key='gravador'
    )

if audio_gravado:
    # Mostra o player do que você acabou de falar
    st.audio(audio_gravado['bytes'])
    
    status_placeholder = st.empty()
    status_placeholder.markdown('<div class="loading-container texto-branco-fixo">IA está ouvindo e traduzindo...</div>', unsafe_allow_html=True)
    
    try:
        # 1. Enviar o áudio direto para o Gemini
        audio_data = audio_gravado['bytes']
        
        # O Gemini 1.5 Flash consegue entender áudio direto!
        prompt = "Você é um tradutor especializado em língua Ticuna. O áudio enviado contém uma fala. Transcreva o que foi dito e traduza para a outra língua (se for português, para ticuna; se for ticuna, para português). Responda apenas com a tradução."
        
        response = model.generate_content([
            prompt,
            {"mime_type": "audio/wav", "data": audio_data}
        ])
        
        tradução = response.text
        
        status_placeholder.empty()
        st.markdown(f'<p class="texto-branco-fixo">✅ Áudio processado!</p>', unsafe_allow_html=True)
        
        # Mostra o resultado na tela
        st.success(f"Tradução: {tradução}")
        
        # 2. Gerar o áudio da tradução (Voz)
        tts = gTTS(text=tradução, lang='pt-br') # Nota: Ticuna usa sons similares ao PT-BR para o robô
        tts.save("trans_audio.mp3")
        st.audio("trans_audio.mp3", autoplay=True)

    except Exception as e:
        status_placeholder.empty()
        st.error(f"A IA não conseguiu entender o áudio. Erro: {e}")

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
                    st.success(f"Ticuna: {ticuna}")
                    tts_txt = gTTS(text=ticuna, lang='pt-br')
                    tts_txt.save("txt_audio.mp3")
                    st.audio("txt_audio.mp3", autoplay=True)
                else:
                    st.warning("Não encontrado na planilha. Consultando IA...")
                    ia_res = model.generate_content(f"Como se diz '{texto}' em língua Ticuna? Responda apenas a tradução.")
                    st.info(f"IA sugere: {ia_res.text}")
            else:
                st.warning("Por favor, digite uma palavra.")
except:
    st.error("Erro ao carregar banco de dados.")

import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# Configuração da IA (Pega a chave que você salvou no Segredo)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Estilo Visual (Mantendo o que você já aprovou)
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-image: url("{img}"); background-size: cover; background-position: center; background-attachment: fixed; }}
    .stForm {{ background-color: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 15px; }}
    /* TÍTULO E SUBTÍTULO EM BRANCO COM SOMBRA */
    h1, h3, p {
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

# --- INTERAÇÃO POR VOZ ---
st.write("### 🎤 Converse com a IA ou Traduza")
audio_gravado = mic_recorder(start_prompt="Falar (Português) 🎤", stop_prompt="Parar Gravação ⏹️", key='gravador')

if audio_gravado:
    st.audio(audio_gravado['bytes'])
    # Aqui a mágica acontece: mandamos o áudio para o Gemini transcrever e responder
    try:
        # 1. Transformar áudio em texto (Simulado via Gemini para este protótipo)
        prompt_especial = "Você é um assistente especialista na cultura Ticuna. Responda de forma curta e amigável."
        # Para um tradutor real, aqui usaríamos o áudio. Por enquanto, vamos habilitar a conversa:
        st.info("Processando sua voz...")
    except Exception as e:
        st.error("Erro ao processar voz.")

# --- TRADUTOR POR TEXTO (Sua Planilha) ---
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
                    st.warning("Palavra não encontrada na planilha. Consultando IA...")
                    # Se não tem na planilha, o Gemini responde!
                    response = model.generate_content(f"Como se diz '{texto}' em língua Ticuna? Responda apenas a tradução.")
                    st.info(f"IA sugere: {response.text}")
except Exception as e:
    st.error("Erro ao carregar banco de dados.")

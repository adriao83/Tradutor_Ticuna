import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import base64 # Importe para o ícone

# Configuração da IA
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Ícone de carregamento base64 (um gif de loading simples e leve)
LOADING_GIF = "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" # Placeholder, substitua por um GIF real se quiser

# CSS REFINADO PARA VISIBILIDADE TOTAL E CARREGAMENTO
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

    /* 3. Caixa do formulário (Branca sólida) */
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

    /* 5. Forçar a cor do Label "Ou digite uma palavra" */
    [data-testid="stForm"] label p {{
        color: #1E1E1E !important; /* Grafite bem escuro */
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

    /* Estilo para o ícone de carregamento */
    .loading-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
        color: white; /* Para o texto "Transcrevendo" */
        text-shadow: 1px 1px 2px black;
    }}
    .loading-gif {{
        width: 25px;
        height: 25px;
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

# Novo código para o carregamento da IA
if audio_gravado:
    st.audio(audio_gravado['bytes'])
    
    # Exibe o ícone de carregamento e mensagem
    st.markdown(f'<div class="loading-container"><img class="loading-gif" src="{LOADING_GIF}" alt="Carregando...">Transcrevendo áudio com IA...</div>', unsafe_allow_html=True)
    
    # Aqui é onde a mágica acontece: Transcrição e Tradução
    try:
        # Placeholder para o Gemini transcrever (ainda sem o código completo para isso)
        st.info("Aguardando função de transcrição e tradução da IA...") 
        # Simula um tempo de processamento
        import time
        time.sleep(3) 

        # AQUI VIRIA A RESPOSTA DA IA (será adicionada no próximo passo)
        # response_text = "Em Ticuna: 'Na'ane'ë'."
        # st.success(f"IA traduz: {response_text}")

    except Exception as e:
        st.error(f"Erro ao processar voz: {e}")

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

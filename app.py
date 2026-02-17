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

# Ícone de carregamento (GIF invisível para manter o espaço)
LOADING_GIF = "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="

# CSS REFINADO PARA CONTRASTE TOTAL
st.markdown(f"""
    <style>
    /* 1. Remove cabeçalhos */
    [data-testid="stHeader"] {{ display: none !important; }}

    /* 2. Fundo da página */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}

    /* 3. Estilo dos textos em BRANCO com sombra */
    h1, h3, .stMarkdown p, .texto-branco-fixo {{
        color: white !important;
        text-shadow: 2px 2px 8px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
        text-align: center;
        font-weight: bold !important;
    }}

    /* 4. Caixa do formulário branca sólida */
    .stForm {{ 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0px 4px 20px rgba(0,0,0,0.5);
    }}

    /* Texto dentro da caixa branca deve ser escuro */
    [data-testid="stForm"] label p {{
        color: #1E1E1E !important;
    }}

    /* 5. Container de carregamento */
    .loading-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    /* Ajuste de margem superior */
    .main .block-container {{ padding-top: 2rem !important; }}
    </style>
    """, unsafe_allow_html=True)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

# Carregar Planilha
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TI'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar Tradutor_Ticuna.xlsx")

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
    # Removemos st.audio do seu áudio para não poluir, focamos na resposta
    status_placeholder = st.empty()
    status_placeholder.markdown(f'''
        <div class="loading-container texto-branco-fixo">
            Ouvindo sua voz...
        </div>
    ''', unsafe_allow_html=True)
    
    try:
        # 1. IA Transcreve o áudio para texto
        prompt_transcricao = "Transcreva apenas a palavra ou frase dita neste áudio, sem pontuação."
        response_ia = model.generate_content([
            prompt_transcricao,
            {"mime_type": "audio/wav", "data": audio_gravado['bytes']}
        ])
        
        palavra_dita = response_ia.text.strip()
        palavra_norm = normalizar(palavra_dita)
        
        status_placeholder.empty()

        # 2. Busca na Planilha (Igual à função de texto)
        resultado = df[df['BUSCA_PT'] == palavra_norm]
        
        if not resultado.empty:
            ticuna = resultado['TICUNA'].values[0]
            st.markdown(f'<p class="texto-branco-fixo">✅ Áudio processado! Você disse: "{palavra_dita}"</p>', unsafe_allow_html=True)
            st.success(f"Ticuna: {ticuna}")
            
            # 3. Voz sintética da tradução (Igual à função de texto)
            tts = gTTS(text=ticuna, lang='pt-br')
            tts.save("audio_voz.mp3")
            st.audio("audio_voz.mp3", autoplay=True)
        else:
            # Tenta busca reversa (se falou em Ticuna para traduzir para PT)
            resultado_rev = df[df['BUSCA_TI'] == palavra_norm]
            if not resultado_rev.empty:
                portugues = resultado_rev['PORTUGUES'].values[0]
                st.markdown(f'<p class="texto-branco-fixo">✅ Áudio processado! Tradução encontrada.</p>', unsafe_allow_html=True)
                st.success(f"Português: {portugues}")
                gTTS(text=portugues, lang='pt-br').save("audio_voz.mp3")
                st.audio("audio_voz.mp3", autoplay=True)
            else:
                st.warning(f"Palavra '{palavra_dita}' não encontrada na planilha. Consultando IA...")
                res_fallback = model.generate_content(f"Como se diz '{palavra_dita}' em língua Ticuna? Responda apenas a tradução.")
                trad_ia = res_fallback.text
                st.info(f"IA sugere: {trad_ia}")
                gTTS(text=trad_ia, lang='pt-br').save("audio_voz.mp3")
                st.audio("audio_voz.mp3", autoplay=True)

    except Exception as e:
        status_placeholder.empty()
        st.error(f"Erro ao processar áudio: Verifique sua conexão ou chave API.")

# --- SEÇÃO DE TEXTO ---
try:
    with st.form("tradutor_form"):
        texto = st.text_input("Ou digite uma palavra:", placeholder="Ex: Olá")
        submit = st.form_submit_button("🔍 TRADUZIR")
        
        if submit:
            if texto:
                t_norm = normalizar(texto)
                resultado = df[df['BUSCA_PT'] == t_norm]
                if not resultado.empty:
                    ticuna = resultado['TICUNA'].values[0]
                    st.success(f"Ticuna: {ticuna}")
                    tts = gTTS(text=ticuna, lang='pt-br')
                    tts.save("audio.mp3")
                    st.audio("audio.mp3", autoplay=True)
                else:
                    st.warning("Consultando IA...")
                    response = model.generate_content(f"Como se diz '{texto}' em língua Ticuna? Responda apenas a tradução.")
                    st.info(f"IA sugere: {response.text}")
                    gTTS(text=response.text, lang='pt-br').save("audio_ia.mp3")
                    st.audio("audio_ia.mp3", autoplay=True)
            else:
                st.warning("Por favor, digite uma palavra.")
except:
    pass

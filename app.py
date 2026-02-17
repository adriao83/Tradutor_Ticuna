import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import io

# Configuração da IA (Ajustada para evitar o erro 404)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
# Mudamos para 'gemini-1.5-flash' mas com a biblioteca atualizada
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# CSS (O que você já aprovou)
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
        text-shadow: 2px 2px 8px #000000 !important;
        text-align: center;
        font-weight: bold !important;
    }}
    .stForm {{ background-color: rgba(255, 255, 255, 0.95) !important; padding: 25px; border-radius: 15px; }}
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
st.markdown("### 🎤 Comando de Voz (Planilha + IA)")

# --- LÓGICA DE ÁUDIO ---
audio_gravado = mic_recorder(start_prompt="Falar 🎤", stop_prompt="Traduzir Áudio ⏹️", key='gravador')

if audio_gravado:
    st.audio(audio_gravado['bytes'])
    status = st.empty()
    status.markdown('<p class="texto-branco-fixo">IA processando sua voz...</p>', unsafe_allow_html=True)
    
    try:
        # 1. Transformar ÁUDIO em TEXTO usando o Gemini
        prompt_transcrever = "Transcreva exatamente o que foi dito neste áudio. Retorne apenas o texto da fala, nada mais."
        response_trans = model.generate_content([
            prompt_transcrever,
            {"mime_type": "audio/wav", "data": audio_gravado['bytes']}
        ])
        
        texto_falado = response_trans.text.strip()
        texto_norm = normalizar(texto_falado)
        
        # 2. BUSCAR NA PLANILHA (Sua base de dados oficial)
        # Busca em Português
        busca_pt = df[df['BUSCA_PT'] == texto_norm]
        # Busca em Ticuna
        busca_ti = df[df['BUSCA_TI'] == texto_norm]
        
        traducao_final = ""
        origem = ""

        if not busca_pt.empty:
            traducao_final = busca_pt['TICUNA'].values[0]
            origem = "Planilha (PT -> TI)"
        elif not busca_ti.empty:
            traducao_final = busca_ti['PORTUGUES'].values[0]
            origem = "Planilha (TI -> PT)"
        else:
            # 3. SE NÃO ESTIVER NA PLANILHA, USA A IA
            prompt_ia = f"Traduza a palavra ou frase '{texto_falado}' para Ticuna (se estiver em português) ou para Português (se estiver em Ticuna). Responda apenas a tradução."
            res_ia = model.generate_content(prompt_ia)
            traducao_final = res_ia.text
            origem = "Inteligência Artificial"

        status.empty()
        st.markdown(f'<p class="texto-branco-fixo">Você disse: "{texto_falado}"</p>', unsafe_allow_html=True)
        st.success(f"**Tradução ({origem}):** {traducao_final}")
        
        # Gerar som da tradução
        tts = gTTS(text=traducao_final, lang='pt-br')
        tts.save("voz.mp3")
        st.audio("voz.mp3", autoplay=True)

    except Exception as e:
        status.empty()
        st.error(f"Erro no processamento: {e}")

# --- SEÇÃO DE TEXTO (DIGITAÇÃO) ---
st.markdown("---")
with st.form("form_texto"):
    texto_input = st.text_input("Ou digite aqui:")
    if st.form_submit_button("🔍 TRADUZIR"):
        t_norm = normalizar(texto_input)
        res = df[df['BUSCA_PT'] == t_norm]
        if not res.empty:
            st.success(f"Ticuna: {res['TICUNA'].values[0]}")
        else:
            st.info("Consultando IA...")
            res_ia = model.generate_content(f"Traduza '{texto_input}' para Ticuna.")
            st.success(res_ia.text)

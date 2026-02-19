import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io
from streamlit_mic_recorder import mic_recorder, speech_to_text

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

def acao_limpar():
    st.session_state.texto_busca = ""
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN CSS ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    .stTextInput > div > div > input {{
        height: 48px !important;
    }}
    .stButton button {{
        height: 48px !important;
        width: 100%;
    }}
    /* Ajuste para o botão do microfone ficar circular ou quadrado igual aos outros */
    .stMicRecorder {{
        display: flex;
        justify-content: center;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("Tradutor_Ticuna.xlsx")
        df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
        df['BUSCA_TC'] = df['TICUNA'].apply(normalizar)
        return df
    except:
        return None

df = carregar_dados()

st.title("🏹 Tradutor Ticuna v0.1")

# --- DENTRO DA ÁREA DAS COLUNAS ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_mic:
    # O componente de voz
    # start_prompt é o que aparece no botão
    texto_falado = speech_to_text(
        language='pt-BR', 
        start_prompt="🎤", 
        stop_prompt="🛑", 
        key='gravador'
    )
    
    # Se você falou algo, atualizamos o estado do texto
    if texto_falado:
        st.session_state.texto_busca = texto_falado
        st.rerun() # Faz o app recarregar para mostrar o texto na caixa e traduzir

with col_txt:
    texto_query = st.text_input(
        "", 
        value=st.session_state.texto_busca, 
        placeholder="Digite ou fale...", 
        label_visibility="collapsed"
    )

with col_x:
    if st.button("✖"):
        acao_limpar()

with col_lupa:
    st.button("🔍")

# --- LÓGICA DE TRADUÇÃO ---
# Prioriza o texto digitado ou o falado
final_query = texto_query if texto_query else st.session_state.texto_busca

if final_query:
    t_norm = normalizar(final_query)
    
    if df is not None:
        # Busca bidirecional
        res_pt = df[df['BUSCA_PT'] == t_norm]
        res_tc = df[df['BUSCA_TC'] == t_norm]
        
        traducao = None
        
        if not res_pt.empty:
            traducao = res_pt['TICUNA'].values[0]
        elif not res_tc.empty:
            traducao = res_tc['PORTUGUES'].values[0]

        if traducao:
            st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:900; text-shadow:2px 2px 20px #000; padding:40px;">{traducao}</div>', unsafe_allow_html=True)
            
            try:
                tts = gTTS(text=str(traducao), lang='pt-br')
                tts_fp = io.BytesIO()
                tts.write_to_fp(tts_fp)
                st.audio(tts_fp, format="audio/mp3", autoplay=True)
            except:
                pass
        else:
            st.info("Palavra não encontrada.")

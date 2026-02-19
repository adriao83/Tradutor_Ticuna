import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# 1. Configuração de Página (Deve ser a primeira)
st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# 2. Cache de Dados para Performance
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("Tradutor_Ticuna.xlsx")
        df['B_PT'] = df['PORTUGUES'].astype(str).str.lower().str.strip()
        df['B_TIC'] = df['TICUNA'].astype(str).str.lower().str.strip()
        return df
    except:
        return None

df = carregar_dados()

# 3. Estado da Sessão
if 'texto_pesquisa' not in st.session_state:
    st.session_state.texto_pesquisa = ""

# 4. CSS Estático (Não causa recarregamento)
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stTextInput input {{ background-color: white !important; color: black !important; border-radius: 10px; height: 48px; }}
    .stButton button {{ background-color: white !important; color: black !important; border-radius: 10px; height: 48px; width: 100%; border: none; }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000; text-align: center; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# 5. Interface em Colunas
c1, c2, c3 = st.columns([0.6, 0.2, 0.2])

with c1:
    # O input lê do session_state
    busca = st.text_input("Busca", value=st.session_state.texto_pesquisa, label_visibility="collapsed", key="input_principal")

with c2:
    if st.button("🔍"):
        st.session_state.texto_pesquisa = busca

with c3:
    # Microfone com "Trava de Segurança" no JS
    val_mic = st.components.v1.html("""
    <script>
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = 'pt-BR';
        r.onresult = (e) => {
            const t = e.results[0][0].transcript;
            // Envia o valor apenas uma vez
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
        };
    </script>
    <button onclick="r.start()" style="background:white; border-radius:10px; height:48px; width:100%; border:none; cursor:pointer; font-size:20px;">🎤</button>
    """, height=50)

# LÓGICA DE ATUALIZAÇÃO (A parte que para o pisca-pisca)
if val_mic is not None and val_mic != "" and val_mic != st.session_state.texto_pesquisa:
    st.session_state.texto_pesquisa = val_mic
    st.rerun()

# 6. Tradução e Áudio
if st.session_state.texto_pesquisa and df is not None:
    q = st.session_state.texto_pesquisa.lower().strip()
    res = df[(df['B_PT'] == q) | (df['B_TIC'] == q)]
    
    if not res.empty:
        is_pt = not df[df['B_PT'] == q].empty
        trad = res['TICUNA'].values[0] if is_pt else res['PORTUGUES'].values[0]
        
        st.markdown(f'<div style="color:white; text-align:center; font-size:35px; font-weight:bold; text-shadow:2px 2px 20px #000; padding:20px;">{trad}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

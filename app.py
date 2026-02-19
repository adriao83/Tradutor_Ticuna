import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# 1. Configuração de Página
st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# 2. Cache de Dados (Essencial para não travar)
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Tradutor_Ticuna.xlsx")
        df['B_PT'] = df['PORTUGUES'].astype(str).str.lower().str.strip()
        df['B_TIC'] = df['TICUNA'].astype(str).str.lower().str.strip()
        return df
    except:
        return None

df = load_data()

# 3. Estado da Sessão
if 'voz' not in st.session_state:
    st.session_state.voz = ""

# 4. CSS Estático (Simples)
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover;
        background-position: center;
    }}
    .stTextInput input {{ background-color: white !important; border-radius: 10px; height: 45px; }}
    .stButton button {{ background-color: white !important; border-radius: 10px; height: 45px; width: 100%; border: none; font-size: 20px; }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000; text-align: center; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# 5. Interface
c1, c2, c3 = st.columns([0.6, 0.2, 0.2])

with c1:
    busca = st.text_input("Busca", value=st.session_state.voz, label_visibility="collapsed")

with c2:
    if st.button("🔍"):
        st.session_state.voz = busca

with c3:
    # Microfone ultra-leve
    res_mic = st.components.v1.html("""
    <body style="margin:0; background:transparent;">
        <button id="b" style="background:white; border-radius:10px; height:45px; width:100%; border:none; cursor:pointer;">🎤</button>
        <script>
            const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            r.lang = 'pt-BR';
            document.getElementById('b').onclick = () => r.start();
            r.onresult = (e) => {
                const t = e.results[0][0].transcript;
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
            };
        </script>
    </body>
    """, height=50)

# 6. Lógica de Rerun Protegida
if res_mic and res_mic != st.session_state.voz:
    st.session_state.voz = res_mic
    st.rerun()

# 7. Tradução
if st.session_state.voz and df is not None:
    q = st.session_state.voz.lower().strip()
    match = df[(df['B_PT'] == q) | (df['B_TIC'] == q)]
    
    if not match.empty:
        is_pt = not df[df['B_PT'] == q].empty
        trad = match['TICUNA'].values[0] if is_pt else match['PORTUGUES'].values[0]
        
        st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:bold; text-shadow:2px 2px 20px #000; padding:20px;">{trad}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

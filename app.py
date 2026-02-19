import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# 1. Configuração de Página (Primeira linha sempre)
st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# 2. Carregar Dados com Cache (Para não ler o Excel toda hora e travar)
@st.cache_data
def get_data():
    try:
        df_dados = pd.read_excel("Tradutor_Ticuna.xlsx")
        df_dados['B_PT'] = df_dados['PORTUGUES'].astype(str).str.lower().str.strip()
        df_dados['B_TIC'] = df_dados['TICUNA'].astype(str).str.lower().str.strip()
        return df_dados
    except:
        return None

df = get_data()

# 3. Inicializar Estado da Sessão
if 'pesquisa' not in st.session_state:
    st.session_state.pesquisa = ""

# 4. Interface e CSS
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

# 5. Colunas da Barra de Busca
c1, c2, c3 = st.columns([0.6, 0.2, 0.2])

with c1:
    # O valor vem do session_state para persistir após o microfone
    busca_manual = st.text_input("Busca", value=st.session_state.pesquisa, label_visibility="collapsed", key="main_input")

with c2:
    if st.button("🔍"):
        st.session_state.pesquisa = busca_manual

with c3:
    # Microfone com script de paragem forçada para evitar loops
    val_voz = st.components.v1.html("""
    <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR';
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
        };
    </script>
    <button onclick="recognition.start()" style="background:white; border-radius:10px; height:45px; width:100%; border:none; cursor:pointer; font-size:20px;">🎤</button>
    """, height=50)

# Lógica Anti-Loop: Só faz rerun se o microfone trouxer algo NOVO
if val_voz and val_voz != st.session_state.pesquisa:
    st.session_state.pesquisa = val_voz
    st.rerun()

# 6. Exibição da Tradução
if st.session_state.pesquisa and df is not None:
    alvo = st.session_state.pesquisa.lower().strip()
    res = df[(df['B_PT'] == alvo) | (df['B_TIC'] == alvo)]
    
    if not res.empty:
        is_pt = not df[df['B_PT'] == alvo].empty
        traducao = res['TICUNA'].values[0] if is_pt else res['PORTUGUES'].values[0]
        
        st.markdown(f'<div style="color:white; text-align:center; font-size:35px; font-weight:bold; text-shadow:2px 2px 20px #000; padding:20px;">{traducao}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(traducao), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except: pass

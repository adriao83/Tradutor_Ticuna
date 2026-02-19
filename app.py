import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- ESTADO DA SESSÃO ---
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS ULTRA-ESTÁVEL ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}
    
    /* Alinhamento da Barra */
    [data-testid="stHorizontalBlock"] {{ align-items: center !important; gap: 5px !important; }}

    .stTextInput > div > div > input {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 48px !important;
    }}

    .stButton button {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 48px !important;
        width: 48px !important;
        border: none !important;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3) !important;
    }}

    /* Ajuste de altura do Mic */
    div[data-testid="column"]:nth-of-type(4) {{ margin-top: -8px !important; }}
    iframe {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DADOS COM CACHE ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Tradutor_Ticuna.xlsx")
        df['B_PT'] = df['PORTUGUES'].apply(normalizar)
        df['B_TIC'] = df['TICUNA'].apply(normalizar)
        return df
    except:
        return None

df = load_data()

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    texto_busca = st.text_input("Busca", value=st.session_state.voz_texto, placeholder="Diga algo...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if st.button("✖"): acao_limpar()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Botão de Microfone que não quebra o servidor
    res_voz = st.components.v1.html(f"""
    <body style="margin:0;padding:0;background:transparent;display:flex;justify-content:center;">
        <button id="m" style="background:white;border-radius:10px;height:48px;width:48px;border:none;box-shadow:1px 1px 5px rgba(0,0,0,0.3);cursor:pointer;font-size:22px;">🎤</button>
        <script>
            const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            r.lang = 'pt-BR';
            document.getElementById('m').onclick = () => {{ r.start(); document.getElementById('m').style.background='#ffcccc'; }};
            r.onresult = (e) => {{
                const t = e.results[0][0].transcript;
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: t}}, '*');
            }};
            r.onend = () => {{ document.getElementById('m').style.background='white'; }};
        </script>
    </body>
    """, height=50)

# Atualiza apenas se houver mudança real
if res_voz and res_voz != st.session_state.voz_texto:
    st.session_state.voz_texto = res_voz
    st.rerun()

# --- TRADUÇÃO ---
if texto_busca and df is not None:
    busca = normalizar(texto_busca)
    res = df[(df['B_PT'] == busca) | (df['B_TIC'] == busca)]
    
    if not res.empty:
        # Verifica qual lado traduzir
        is_pt = not df[df['B_PT'] == busca].empty
        trad = res['TICUNA'].values[0] if is_pt else res['PORTUGUES'].values[0]
        label = "Ticuna" if is_pt else "Português"
        
        st.markdown(f'<div style="color:white;text-align:center;font-size:32px;font-weight:900;text-shadow:2px 2px 20px #000;padding:40px;">{label}: {trad}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except: pass
    elif texto_busca.strip() != "":
        st.markdown('<div style="color:white;text-align:center;text-shadow:1px 1px 5px #000;">Não encontrado</div>', unsafe_allow_html=True)

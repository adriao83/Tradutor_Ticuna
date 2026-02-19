import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO ---
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.voz_texto = ""
    st.session_state.contador += 1
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN CORRIGIDO (PARA NÃO PISCAR) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed;
    }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; -webkit-text-fill-color: white !important; }}
    
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

    /* Alinhamento do microfone */
    div[data-testid="column"]:nth-of-type(4) {{ margin-top: -8px !important; }}
    iframe {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TIC'] = df['TICUNA'].apply(normalizar)
except Exception as e:
    st.error(f"Erro ao carregar planilha: {e}")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    # Usamos um label invisível para evitar erros nos logs
    texto_busca = st.text_input("Busca", value=st.session_state.voz_texto, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Botão de voz simplificado (sem loop de rerun)
    resultado_voz = st.components.v1.html(f"""
    <body style="margin:0; padding:0; background:transparent; display:flex; align-items:center; justify-content:center;">
        <button id="mic-btn" style="background:white; border-radius:10px; height:48px; width:48px; border:none; box-shadow: 1px 1px 5px rgba(0,0,0,0.3); cursor:pointer; font-size:22px;">🎤</button>
        <script>
            const btn = document.getElementById('mic-btn');
            const recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = 'pt-BR';
            
            btn.onclick = () => {{
                btn.style.background = '#ffcccc';
                recognition.start();
            }};

            recognition.onresult = (event) => {{
                const text = event.results[0][0].transcript;
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: text}}, '*');
                btn.style.background = 'white';
            }};
            recognition.onend = () => {{ btn.style.background = 'white'; }};
        </script>
    </body>
    """, height=50)

# Só atualiza o estado se houver uma nova voz capturada
if resultado_voz and resultado_voz != st.session_state.voz_texto:
    st.session_state.voz_texto = resultado_voz
    st.rerun()

# --- TRADUÇÃO ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    res_pt = df[df['BUSCA_PT'] == t_norm] if 'df' in locals() else pd.DataFrame()
    res_tic = df[df['BUSCA_TIC'] == t_norm] if 'df' in locals() else pd.DataFrame()
    
    traducao = None
    if not res_pt.empty:
        traducao = res_pt['TICUNA'].values[0]
        alvo = "Ticuna"
    elif not res_tic.empty:
        traducao = res_tic['PORTUGUES'].values[0]
        alvo = "Português"

    if traducao:
        st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:900; text-shadow:2px 2px 20px #000; padding:40px;">{alvo}: {traducao}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(traducao), lang='pt-br')
            tts_fp = io.BytesIO()
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp, format="audio/mp3", autoplay=True)
        except: pass
    elif texto_busca.strip() != "":
        st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000; font-size:20px;">Não encontrada</div>', unsafe_allow_html=True)

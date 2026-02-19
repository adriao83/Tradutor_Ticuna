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
# Usamos o 'texto_input' para sincronizar o JS com o Python
if 'texto_input' not in st.session_state:
    st.session_state.texto_input = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.texto_input = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed;
    }}
    h1 {{ 
        color: white !important; 
        text-shadow: 2px 2px 10px #000 !important; 
        text-align: center; 
    }}
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
        width: 100% !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    # Pré-normalizamos as duas colunas para busca bidirecional
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TC'] = df['TICUNA'].apply(normalizar)
except Exception as e:
    st.error(f"Erro ao carregar planilha: {e}")

st.title("🏹 Tradutor Ticuna v0.1")

# --- LÓGICA DO MICROFONE (COMUNICAÇÃO COM SESSION STATE) ---
# O componente HTML envia o texto para o Streamlit via query params ou evento de clique
from streamlit_mic_recorder import mic_recorder # Uma alternativa mais estável se preferir

# Mantendo seu HTML, mas ajustando para que o Streamlit receba o valor
col_txt, col_x, col_mic = st.columns([0.7, 0.15, 0.15])

with col_txt:
    # O valor do input é vinculado ao session_state
    texto_busca = st.text_input("", value=st.session_state.texto_input, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"input_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

with col_mic:
    # Capturamos o retorno do JS usando um componente de retorno de valor
    feedback = st.components.v1.html(f"""
    <body style="margin:0; padding:0; background:transparent;">
        <button id="mic-btn" style="background:white; border-radius:10px; height:48px; width:48px; border:none; box-shadow: 1px 1px 5px rgba(0,0,0,0.3); cursor:pointer; font-size:22px;">🎤</button>
        <script>
            const btn = document.getElementById('mic-btn');
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'pt-BR';

            btn.onclick = () => {{
                btn.innerHTML = "⏳";
                recognition.start();
            }};

            recognition.onresult = (event) => {{
                const transcript = event.results[0][0].transcript;
                // Envia para o Streamlit via URL ou disparando um evento
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }}, '*');
                btn.innerHTML = "🎤";
            }};
            recognition.onerror = () => {{ btn.innerHTML = "🎤"; }};
        </script>
    </body>
    """, height=50)

# --- LÓGICA DE TRADUÇÃO BIDIRECIONAL ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    
    # Busca em Português
    res_pt = df[df['BUSCA_PT'] == t_norm]
    # Busca em Ticuna
    res_tc = df[df['BUSCA_TC'] == t_norm]
    
    traducao_final = None
    idioma_destino = "pt-br"

    if not res_pt.empty:
        traducao_final = res_pt['TICUNA'].values[0]
    elif not res_tc.empty:
        traducao_final = res_tc['PORTUGUES'].values[0]

    if traducao_final:
        st.markdown(f'''
            <div style="background: rgba(0,0,0,0.6); border-radius: 15px; padding: 20px; margin-top: 20px;">
                <p style="color: #ccc; margin: 0; text-align: center;">Tradução:</p>
                <h2 style="color: white; text-align: center; margin: 0;">{traducao_final}</h2>
            </div>
        ''', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(traducao_final), lang='pt-br')
            tts_fp = io.BytesIO()
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp, format="audio/mp3", autoplay=True)
        except: pass
    else:
        st.warning("Palavra não encontrada no dicionário.")

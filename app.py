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

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN (ALTURA UNIFICADA E TÍTULO BRANCO) ---
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
        -webkit-text-fill-color: white !important; 
    }}
    
    /* Alinhamento da linha de busca */
    [data-testid="stHorizontalBlock"] {{ 
        align-items: center !important; 
        gap: 5px !important; 
        background: transparent !important;
    }}

    /* Altura fixa para o Input */
    .stTextInput > div > div > input {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 48px !important;
    }}

    /* Altura fixa para os botões X e Lupa */
    .stButton button {{
        background-color: white !important;
        color: black !important;
        border-radius: 10px !important;
        height: 48px !important;
        width: 48px !important;
        border: none !important;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* Botão do Microfone (HTML) - Mesma altura e estilo */
    .mic-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 48px;
    }}
    
    .btn-mic {{
        background-color: white;
        border-radius: 10px;
        height: 48px;
        width: 48px;
        border: none;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
        cursor: pointer;
        font-size: 20px;
        transition: 0.3s;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    texto_busca = st.text_input("", value=st.session_state.voz_texto, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

with col_lupa:
    st.button("🔍")

with col_mic:
    # BOTÃO MICROFONE NATIVO (ESTILO GOOGLE)
    st.components.v1.html(f"""
    <div class="mic-container" style="display:flex; justify-content:center; align-items:center; height:48px;">
        <button id="mic-btn" style="background:white; border-radius:10px; height:48px; width:48px; border:none; box-shadow: 1px 1px 5px rgba(0,0,0,0.3); cursor:pointer; font-size:20px;">🎤</button>
    </div>
    <script>
        const btn = document.getElementById('mic-btn');
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR';

        btn.onclick = () => {{
            btn.style.background = '#ffcccc'; 
            recognition.start();
        }};

        recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            // Envia para o Streamlit e força a atualização
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: transcript}}, '*');
            btn.style.background = 'white';
        }};
        
        recognition.onend = () => {{ btn.style.background = 'white'; }};
    </script>
    """, height=48) # Altura do iframe igual à dos botões

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    res = df[df['BUSCA_PT'] == t_norm] if 'df' in locals() else pd.DataFrame()
    
    if not res.empty:
        trad = res['TICUNA'].values[0]
        st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:900; text-shadow:2px 2px 20px #000; padding:40px;">Ticuna: {trad}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            tts_fp = io.BytesIO()
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp, format="audio/mp3", autoplay=True)
        except: pass
    elif texto_busca.strip() != "":
        st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000; font-size:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

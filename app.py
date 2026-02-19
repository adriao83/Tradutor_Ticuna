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
if 'texto_input' not in st.session_state:
    st.session_state.texto_input = ""
if 'contador' not in st.session_state:
    st.session_state.contador = 0

def acao_limpar():
    st.session_state.texto_input = ""
    st.session_state.contador += 1

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- DESIGN (CSS REFINADO) ---
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
    
    [data-testid="stHorizontalBlock"] {{ 
        align-items: center !important; 
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
        border: none !important;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.3) !important;
    }}

    div[data-testid="column"]:nth-of-type(4) {{
        margin-top: -4px !important; 
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TC'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha Tradutor_Ticuna.xlsx.")

st.title("🏹 Tradutor Ticuna v0.1")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    # Vinculamos o valor à variável de estado
    texto_busca = st.text_input("", value=st.session_state.texto_input, placeholder="Digite ou fale...", label_visibility="collapsed", key=f"in_{st.session_state.contador}")

with col_x:
    if st.button("✖"):
        acao_limpar()
        st.rerun()

with col_lupa:
    if st.button("🔍"):
        st.session_state.texto_input = texto_busca # Garante a captura do que foi digitado
        st.rerun()

with col_mic:
    # AJUSTE AQUI: O componente agora captura o clique e retorna o valor para o Streamlit
    # Usamos uma técnica de "query params" ou o retorno direto do componente
    fala_capturada = st.components.v1.html(f"""
    <body style="margin:0; padding:0; background:transparent; display:flex; align-items:center; justify-content:center;">
        <button id="mic-btn" style="background:white; border-radius:10px; height:48px; width:48px; border:none; box-shadow: 1px 1px 5px rgba(0,0,0,0.3); cursor:pointer; font-size:22px;">🎤</button>
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
                // Envia o texto de volta para o Streamlit de forma que ele reconheça a mudança
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }}, '*');
                btn.style.background = 'white';
            }};
            
            recognition.onend = () => {{ btn.style.background = 'white'; }};
            recognition.onerror = () => {{ btn.style.background = 'white'; }};
        </script>
    </body>
    """, height=50)

# --- ATUALIZAÇÃO AUTOMÁTICA DO TEXTO ---
# Se o microfone enviou algo novo (fala_capturada), atualizamos o estado
if fala_capturada and fala_capturada != st.session_state.texto_input:
    st.session_state.texto_input = fala_capturada
    st.rerun()

# --- LÓGICA DE TRADUÇÃO ---
if texto_busca:
    t_norm = normalizar(texto_busca)
    
    res_pt = df[df['BUSCA_PT'] == t_norm] if 'df' in locals() else pd.DataFrame()
    res_tc = df[df['BUSCA_TC'] == t_norm] if 'df' in locals() else pd.DataFrame()
    
    traducao = ""
    encontrado = False

    if not res_pt.empty:
        traducao = res_pt['TICUNA'].values[0]
        encontrado = True
    elif not res_tc.empty:
        # Correção na lógica: se não achou em PT, pega o valor da coluna PORTUGUES do resultado TC
        traducao = res_tc['PORTUGUES'].values[0]
        encontrado = True

    if encontrado:
        st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:900; text-shadow:2px 2px 20px #000; padding:40px;">Tradução: {traducao}</div>', unsafe_allow_html=True)
        try:
            tts = gTTS(text=str(traducao), lang='pt-br')
            tts_fp = io.BytesIO()
            tts.write_to_fp(tts_fp)
            st.audio(tts_fp, format="audio/mp3", autoplay=True)
        except:
            pass
    else:
        st.markdown('<div style="color:white; text-align:center; text-shadow:1px 1px 5px #000; font-size:20px;">Palavra não encontrada</div>', unsafe_allow_html=True)

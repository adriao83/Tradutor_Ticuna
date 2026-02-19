import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- CONTROLE DE ESTADO (MEMÓRIA DO APP) ---
if 'texto_busca' not in st.session_state:
    st.session_state.texto_busca = ""

# --- DESIGN CSS ---
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover;
        background-position: center;
    }}
    /* Estilização dos botões para ficarem iguais */
    .stButton button {{
        height: 48px !important;
        border-radius: 10px !important;
        background-color: white !important;
        color: black !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA_PT'] = df['PORTUGUES'].apply(normalizar)
    df['BUSCA_TC'] = df['TICUNA'].apply(normalizar)
except:
    st.error("Erro ao carregar planilha.")

st.title("🏹 Tradutor Ticuna")

# --- BARRA DE PESQUISA ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    # O segredo aqui é o 'key'. O Streamlit vai atualizar este campo quando o JS mandar o valor.
    texto_input = st.text_input("", placeholder="Digite ou fale...", label_visibility="collapsed", key="caixa_de_texto")

with col_x:
    if st.button("✖"):
        st.session_state.caixa_de_texto = "" # Limpa a chave do input
        st.rerun()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Este componente HTML é SILENCIOSO. Ele só envia o texto e não reinicia a página sozinho.
    st.components.v1.html("""
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'pt-BR';
        
        // Função que será chamada ao clicar no botão de microfone
        window.iniciarMic = () => {
            recognition.start();
        };

        recognition.onresult = (event) => {
            const result = event.results[0][0].transcript;
            // Envia o texto para o Streamlit de forma segura
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: result
            }, '*');
        };
        </script>
        <button onclick="iniciarMic()" style="background:white; border-radius:10px; height:48px; width:48px; border:none; cursor:pointer; font-size:22px; box-shadow: 1px 1px 5px rgba(0,0,0,0.2);">🎤</button>
    """, height=50)

# --- LÓGICA DE BUSCA ---
# Usamos o valor que está no input (seja digitado ou vindo do microfone)
termo = st.session_state.get("caixa_de_texto", "")

if termo:
    t_norm = normalizar(termo)
    res_pt = df[df['BUSCA_PT'] == t_norm] if 'df' in locals() else pd.DataFrame()
    res_tc = df[df['BUSCA_TC'] == t_norm] if 'df' in locals() else pd.DataFrame()
    
    trad = None
    if not res_pt.empty:
        trad = res_pt['TICUNA'].values[0]
    elif not res_tc.empty:
        trad = res_tc['PORTUGUES'].values[0]

    if trad:
        st.markdown(f'<div style="color:white; text-align:center; font-size:32px; font-weight:bold; text-shadow:2px 2px 10px #000; padding:20px;">{trad}</div>', unsafe_allow_html=True)
        # Áudio
        tts = gTTS(text=str(trad), lang='pt-br')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format="audio/mp3", autoplay=True)

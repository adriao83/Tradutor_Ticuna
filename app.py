import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# --- 1. CONFIGURAÇÃO INICIAL (Obrigatório ser a primeira linha) ---
st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- 2. CARREGAMENTO DE DADOS (Com Cache para evitar lentidão) ---
@st.cache_data
def carregar_dados():
    try:
        df_dados = pd.read_excel("Tradutor_Ticuna.xlsx")
        # Normalização básica
        df_dados['B_PT'] = df_dados['PORTUGUES'].astype(str).str.lower().str.strip()
        df_dados['B_TIC'] = df_dados['TICUNA'].astype(str).str.lower().str.strip()
        return df_dados
    except:
        return None

df = carregar_dados()

# --- 3. ESTADO DA SESSÃO (Evita o loop infinito) ---
if 'texto_voz' not in st.session_state:
    st.session_state.texto_voz = ""

def limpar_busca():
    st.session_state.texto_voz = ""
    st.rerun()

# --- 4. DESIGN (CSS SIMPLIFICADO PARA ESTABILIDADE) ---
img_fundo = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img_fundo}");
        background-size: cover;
        background-position: center;
    }}
    h1 {{ color: white !important; text-shadow: 2px 2px 8px #000; text-align: center; }}
    
    /* Alinhamento dos botões */
    [data-testid="stHorizontalBlock"] {{ align-items: center !important; }}
    .stTextInput input {{ background-color: white !important; color: black !important; border-radius: 10px; height: 45px; }}
    .stButton button {{ background-color: white !important; color: black !important; border-radius: 10px; height: 45px; width: 45px; border: none; box-shadow: 1px 1px 5px rgba(0,0,0,0.2); }}
    
    /* Alinhamento do Microfone */
    div[data-testid="column"]:nth-of-type(4) {{ margin-top: -5px; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- 5. INTERFACE DE BUSCA ---
col_in, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_in:
    # Usamos um label fixo "Busca" para satisfazer o log do Streamlit
    busca_manual = st.text_input("Busca", value=st.session_state.texto_voz, label_visibility="collapsed")

with col_x:
    if st.button("✖"):
        limpar_busca()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Microfone simplificado: ele apenas preenche a caixa, não força o rerun imediato
    # Isso evita que o servidor caia
    res_voz = st.components.v1.html("""
    <div style="display:flex; justify-content:center;">
        <button id="mic" style="background:white; border-radius:10px; height:45px; width:45px; border:none; cursor:pointer; font-size:20px; box-shadow:1px 1px 5px rgba(0,0,0,0.2);">🎤</button>
    </div>
    <script>
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = 'pt-BR';
        document.getElementById('mic').onclick = () => { r.start(); };
        r.onresult = (e) => {
            const t = e.results[0][0].transcript;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
        };
    </script>
    """, height=50)

# Atualiza o estado se a voz capturar algo novo
if res_voz and res_voz != st.session_state.texto_voz:
    st.session_state.texto_voz = res_voz
    st.rerun()

# --- 6. LÓGICA DE TRADUÇÃO ---
texto_final = busca_manual if busca_manual else st.session_state.texto_voz

if texto_final and df is not None:
    t_norm = texto_final.lower().strip()
    # Busca em ambas as colunas
    resultado = df[(df['B_PT'] == t_norm) | (df['B_TIC'] == t_norm)]
    
    if not resultado.empty:
        # Define o sentido da tradução
        is_pt = not df[df['B_PT'] == t_norm].empty
        trad = resultado['TICUNA'].values[0] if is_pt else resultado['PORTUGUES'].values[0]
        label = "Ticuna" if is_pt else "Português"
        
        st.markdown(f'<div style="color:white; text-align:center; font-size:30px; font-weight:bold; text-shadow:2px 2px 15px #000; padding:30px;">{label}: {trad}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except:
            pass
    elif texto_final.strip() != "":
        st.markdown('<div style="color:white; text-align:center;">Palavra não encontrada</div>', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# --- CONFIGURAÇÃO DA PÁGINA (Sempre a primeira coisa) ---
st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹", layout="centered")

# --- FUNÇÃO DE NORMALIZAÇÃO ---
def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower().strip() if pd.notna(t) else ""

# --- CARGA DE DADOS (Com Cache para não travar o servidor) ---
@st.cache_data
def carregar_planilha():
    try:
        df_dados = pd.read_excel("Tradutor_Ticuna.xlsx")
        df_dados['B_PT'] = df_dados['PORTUGUES'].apply(normalizar)
        df_dados['B_TIC'] = df_dados['TICUNA'].apply(normalizar)
        return df_dados
    except Exception as e:
        st.error(f"Erro ao ler Excel: {e}")
        return None

df = carregar_planilha()

# --- ESTADO DA SESSÃO ---
if 'voz_texto' not in st.session_state:
    st.session_state.voz_texto = ""

def limpar():
    st.session_state.voz_texto = ""
    st.rerun()

img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# --- CSS (Blindado contra erros de renderização) ---
st.markdown(f"""
<style>
    [data-testid="stHeader"] {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("{img}");
        background-size: cover !important;
        background-position: center !important;
    }}
    h1 {{ color: white !important; text-shadow: 2px 2px 10px #000 !important; text-align: center; }}
    [data-testid="stHorizontalBlock"] {{ align-items: center !important; gap: 5px !important; }}
    .stTextInput > div > div > input {{ background-color: white !important; color: black !important; border-radius: 10px !important; height: 48px !important; }}
    .stButton button {{ background-color: white !important; color: black !important; border-radius: 10px !important; height: 48px !important; width: 48px !important; border: none !important; box-shadow: 1px 1px 5px rgba(0,0,0,0.3) !important; }}
    div[data-testid="column"]:nth-of-type(4) {{ margin-top: -8px !important; }}
    iframe {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

st.title("🏹 Tradutor Ticuna v0.1")

# --- INTERFACE ---
col_txt, col_x, col_lupa, col_mic = st.columns([0.55, 0.15, 0.15, 0.15])

with col_txt:
    # Definir um label fixo para evitar avisos de acessibilidade
    texto_busca = st.text_input("Input", value=st.session_state.voz_texto, placeholder="Escreve ou fala...", label_visibility="collapsed")

with col_x:
    if st.button("✖"): limpar()

with col_lupa:
    st.button("🔍")

with col_mic:
    # Microfone em HTML puro para não gerar conflito de reruns
    res_voz = st.components.v1.html("""
    <body style="margin:0;padding:0;background:transparent;display:flex;justify-content:center;">
        <button id="mic" style="background:white;border-radius:10px;height:48px;width:48px;border:none;box-shadow:1px 1px 5px rgba(0,0,0,0.3);cursor:pointer;font-size:22px;">🎤</button>
        <script>
            const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            r.lang = 'pt-BR';
            document.getElementById('mic').onclick = () => { r.start(); document.getElementById('mic').style.background='#ffcccc'; };
            r.onresult = (e) => {
                const t = e.results[0][0].transcript;
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
            };
            r.onend = () => { document.getElementById('mic').style.background='white'; };
        </script>
    </body>
    """, height=50)

# SEGURANÇA: Só atualiza se o texto for novo e diferente de vazio
if res_voz and res_voz != st.session_state.voz_texto:
    st.session_state.voz_texto = res_voz
    st.rerun()

# --- TRADUÇÃO ---
if texto_busca and df is not None:
    query = normalizar(texto_busca)
    # Procura em ambas as colunas
    match = df[(df['B_PT'] == query) | (df['B_TIC'] == query)]
    
    if not match.empty:
        # Descobre se a busca foi em PT ou TIC
        is_pt = not df[df['B_PT'] == query].empty
        trad = match['TICUNA'].values[0] if is_pt else match['PORTUGUES'].values[0]
        sentido = "Ticuna" if is_pt else "Português"
        
        st.markdown(f'<div style="color:white;text-align:center;font-size:32px;font-weight:900;text-shadow:2px 2px 20px #000;padding:40px;">{sentido}: {trad}</div>', unsafe_allow_html=True)
        
        try:
            tts = gTTS(text=str(trad), lang='pt-br')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            st.audio(fp, format="audio/mp3", autoplay=True)
        except: pass
    elif texto_busca.strip() != "":
        st.markdown('<div style="color:white;text-align:center;text-shadow:1px 1px 5px #000;">Palavra não encontrada</div>', unsafe_allow_html=True)

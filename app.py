import streamlit as st
import pandas as pd
from gtts import gTTS
import re
import io

# 1. Configuração inicial
st.set_page_config(page_title="Teste Tradutor", layout="centered")

# 2. Carregar dados (Sem cache agora para evitar erros de memória)
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['B_PT'] = df['PORTUGUES'].astype(str).str.lower().strip()
except:
    st.error("Erro ao carregar Excel")
    df = None

st.title("🏹 Tradutor Ticuna")

# 3. Interface Simples
busca = st.text_input("Digite uma palavra em Português")

if busca and df is not None:
    t_norm = busca.lower().strip()
    resultado = df[df['B_PT'] == t_norm]
    
    if not resultado.empty:
        traducao = resultado['TICUNA'].values[0]
        st.success(f"Ticuna: {traducao}")
        
        # Áudio
        tts = gTTS(text=str(traducao), lang='pt-br')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format="audio/mp3")
    else:
        st.warning("Não encontrado")

# 4. Microfone (Apenas o básico)
st.write("---")
st.write("Teste de Voz:")
res_voz = st.components.v1.html("""
    <script>
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = 'pt-BR';
        r.onresult = (e) => {
            const t = e.results[0][0].transcript;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: t}, '*');
        };
    </script>
    <button onclick="r.start()">🎤 Clicar para Falar</button>
""", height=50)

if res_voz:
    st.write(f"Voz detetada: {res_voz}")

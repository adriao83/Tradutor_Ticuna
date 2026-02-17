import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Deixa o botão verde e grande para o celular
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_content_allowed=True)

def normalizar(texto):
    if pd.isna(texto): return ""
    # Remove espaços, hífens e deixa tudo minúsculo
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

st.title("🏹 Tradutor Ticuna v0.1")
st.write("Protótipo de Preservação - Língua Magüta")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['PORT_BUSCA'] = df['PORTUGUES'].apply(normalizar)

    palavra_usuario = st.text_input("Digite em Português:")

    # O botão de lupa que você pediu
    if st.button("🔍 PESQUISAR TRADUÇÃO"):
        if palavra_usuario:
            busca = normalizar(palavra_usuario)
            resultado = df[df['PORT_BUSCA'] == busca]
            
            if not resultado.empty:
                ticuna = resultado['TICUNA'].values[0]
                port_original = resultado['PORTUGUES'].values[0]
                
                st.success(f"**Português:** {port_original}")
                st.subheader(f"Ticuna: {ticuna}")
                
                # Áudio do Google (Provisório até você gravar os reais)
                tts = gTTS(text=ticuna, lang='pt-br')
                tts.save("audio.mp3")
                st.audio("audio.mp3")
            else:
                st.error("Palavra não encontrada. Verifique se digitou corretamente.")
        else:
            st.warning("Por favor, digite uma palavra primeiro.")

except Exception as e:
    st.error("Erro ao carregar os dados da planilha.")

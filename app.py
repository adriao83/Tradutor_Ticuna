
import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Função para normalizar o texto (remove hífens, espaços e deixa minúsculo)
def normalizar(texto):
    if pd.isna(texto): return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

st.title("🏹 Tradutor Ticuna v0.1")
st.write("Protótipo - Preservação da Língua Magüta")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    
    # Criamos colunas invisíveis para busca facilitada
    df['PORT_BUSCA'] = df['PORTUGUES'].apply(normalizar)

    palavra_usuario = st.text_input("Digite em Português:")

    if palavra_usuario:
        busca = normalizar(palavra_usuario)
        resultado = df[df['PORT_BUSCA'] == busca]
        
        if not resultado.empty:
            ticuna = resultado['TICUNA'].values[0]
            port_original = resultado['PORTUGUES'].values[0]
            
            st.success(f"**Português:** {port_original}  \n**Ticuna:** {ticuna}")
            
            # Áudio (Provisório até você gravar os reais)
            tts = gTTS(text=ticuna, lang='pt-br')
            tts.save("audio.mp3")
            st.audio("audio.mp3")
        else:
            st.error(f"A palavra '{palavra_usuario}' não foi encontrada. Verifique a grafia ou tente outra.")

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique o arquivo Excel no GitHub.")

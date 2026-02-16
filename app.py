import streamlit as st
import pandas as pd
from gtts import gTTS

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

st.title("🏹 Tradutor Ticuna v0.1")
st.write("Protótipo para o Edital Centelha - Preservação da Língua Magüta")

# Carregando a planilha que você subiu
try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    
    palavra = st.text_input("Digite em Português para traduzir:")

    if palavra:
        # Busca exata na coluna PORTUGUES
        resultado = df[df['PORTUGUES'].str.fullmatch(palavra, case=False, na=False)]
        
        if not resultado.empty:
            ticuna = resultado['TICUNA'].values[0]
            st.success(f"### Tradução: {ticuna}")
            
            # Gerar áudio automático
            tts = gTTS(text=ticuna, lang='pt-br')
            tts.save("audio.mp3")
            st.audio("audio.mp3")
        else:
            st.warning("Palavra ainda não encontrada no nosso dicionário.")
            
except Exception as e:
    st.error("Erro ao carregar a planilha. Verifique se o nome está correto no GitHub.")

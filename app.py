import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

def normalizar(texto):
    if pd.isna(texto): return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

st.title("🏹 Tradutor Ticuna v0.1")
st.write("Protótipo de Preservação - Língua Magüta")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['PORT_BUSCA'] = df['PORTUGUES'].apply(normalizar)

    # Criamos um formulário para o Enter funcionar automaticamente
    with st.form(key="busca_tradutor", clear_on_submit=False):
        palavra_usuario = st.text_input("Digite em Português:")
        submit_button = st.form_submit_button(label="🔍 PESQUISAR TRADUÇÃO")

    # A lógica de busca acontece quando clica no botão OU aperta Enter
    if submit_button:
        if palavra_usuario:
            busca = normalizar(palavra_usuario)
            resultado = df[df['PORT_BUSCA'] == busca]
            
            if not resultado.empty:
                ticuna = resultado['TICUNA'].values[0]
                port_original = resultado['PORTUGUES'].values[0]
                
                st.success(f"**Português:** {port_original}")
                st.subheader(f"Ticuna: {ticuna}")
                
                tts = gTTS(text=ticuna, lang='pt-br')
                tts.save("audio.mp3")
                st.audio("audio.mp3")
            else:
                st.error("Palavra não encontrada. Verifique se digitou corretamente.")
        else:
            st.warning("Por favor, digite uma palavra primeiro.")

except Exception as e:
    st.error("Erro ao carregar os dados. Verifique a planilha no GitHub.")

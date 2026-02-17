import streamlit as st
import pandas as pd
from gtts import gTTS
import re

st.set_page_config(page_title="Tradutor Ticuna", page_icon="🏹")

# Link da sua foto
img = "https://raw.githubusercontent.com/adriao83/Tradutor_Ticuna/main/fundo.png"

# Forma de colocar o fundo que não causa erro de TypeError
st.markdown(
    f'<style>.stApp {{ background-image: url("{img}"); background-size: cover; }}</style>',
    unsafe_content_allowed=True
)

def normalizar(t):
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower() if pd.notna(t) else ""

st.title("🏹 Tradutor Ticuna v0.1")

try:
    df = pd.read_excel("Tradutor_Ticuna.xlsx")
    df['BUSCA'] = df['PORTUGUES'].apply(normalizar)

    with st.form("meu_form"):
        texto = st.text_input("Digite em Português:")
        if st.form_submit_button("PESQUISAR"):
            res = df[df['BUSCA'] == normalizar(texto)]
            if not res.empty:
                tic = res['TICUNA'].values[0]
                st.success(f"### Ticuna: {tic}")
                gTTS(tic, lang='pt-br').save("a.mp3")
                st.audio("a.mp3")
            else:
                st.error("Não encontrado.")
except:
    st.error("Erro ao carregar a planilha.")

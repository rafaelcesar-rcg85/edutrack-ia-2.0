import streamlit as st

# Configuração da Página (Título na aba do navegador)
st.set_page_config(page_title="EduTrack AI", page_icon=" ")

# Título Principal
st.title(" EduTrack AI")

st.write("Bem-vindo ao seu assistente acadêmico!")
st.info("Conecte ao Xano para ver seus dados reais.")

# Exemplo de Métrica Visual
col1, col2 = st.columns(2)
col1.metric("Disciplinas Ativas", "0")
col2.metric("Tarefas Pendentes", "0")

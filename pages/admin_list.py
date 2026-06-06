import streamlit as st
import pandas as pd
from utils.api import api_get_users

st.title("Lista de Usuários")

if st.session_state.get('user_role') != 'admin':
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

st.write("Visualize todas as contas cadastradas na plataforma.")

users = api_get_users()

if not users:
    st.info("Nenhum usuário encontrado ou ocorreu um erro na requisição.")
else:
    df_users = pd.DataFrame(users)
    cols_to_show = ['id', 'name', 'email', 'role']
    cols_to_show = [col for col in cols_to_show if col in df_users.columns]
    
    st.dataframe(df_users[cols_to_show], use_container_width=True)

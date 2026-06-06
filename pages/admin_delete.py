import streamlit as st
from utils.api import api_get_users, api_delete_user

st.title("Excluir Conta")

if st.session_state.get('user_role') != 'admin':
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

users = api_get_users()

if not users:
    st.info("Nenhum usuário encontrado ou ocorreu um erro na requisição.")
    st.stop()

st.warning("Aviso: A exclusão de uma conta de usuário é uma ação permanente e irreversível. Todos os dados vinculados a este usuário poderão ser perdidos ou ficar órfãos.")

user_options = {u.get('id'): f"ID {u.get('id')} - {u.get('name', '')} ({u.get('email', '')})" for u in users}
selected_user_id = st.selectbox("Selecione um usuário para excluir", options=list(user_options.keys()), format_func=lambda x: user_options[x])

if selected_user_id:
    selected_user = next((u for u in users if u.get('id') == selected_user_id), None)
    
    st.markdown("---")
    confirm_delete = st.checkbox(f"Eu entendo que excluir o usuário {selected_user.get('email')} é uma ação definitiva.")
    
    if st.button("Excluir Usuário", type="primary", disabled=not confirm_delete):
        if selected_user_id == st.session_state.get('user_id'):
            st.error("Você não pode excluir a sua própria conta logada.")
        else:
            res = api_delete_user(selected_user_id)
            if hasattr(res, 'status_code') and res.status_code == 200:
                st.success("Usuário excluído com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao excluir usuário.")

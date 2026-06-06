import streamlit as st
from utils.api import api_get_users, api_change_role, api_change_password, api_change_email

st.title("Gerenciar Usuário")

if st.session_state.get('user_role') != 'admin':
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

users = api_get_users()

if not users:
    st.info("Nenhum usuário encontrado ou ocorreu um erro na requisição.")
    st.stop()

user_options = {u.get('id'): f"ID {u.get('id')} - {u.get('name', '')} ({u.get('email', '')})" for u in users}
selected_user_id = st.selectbox("Selecione um usuário", options=list(user_options.keys()), format_func=lambda x: user_options[x])

if selected_user_id:
    selected_user = next((u for u in users if u.get('id') == selected_user_id), None)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Alterar Papel")
        current_role = selected_user.get('role', 'user')
        new_role = st.selectbox("Novo Papel", ["user", "admin"], index=0 if current_role == 'user' else 1)
        
        if st.button("Salvar Papel", type="primary", use_container_width=True):
            if current_role == new_role:
                st.warning("O usuário já possui este papel.")
            else:
                res = api_change_role(selected_user_id, new_role)
                if hasattr(res, 'status_code') and res.status_code == 200:
                    st.success("Papel alterado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao alterar o papel.")
    
    with col2:
        st.markdown("### Alterar Senha")
        new_password = st.text_input("Nova Senha", type="password")
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
        
        if st.button("Redefinir Senha", type="primary", use_container_width=True):
            if not new_password:
                st.warning("A senha não pode ser vazia.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            else:
                res = api_change_password(selected_user_id, new_password)
                if hasattr(res, 'status_code') and res.status_code == 200:
                    st.success("Senha alterada com sucesso!")
                else:
                    st.error("Erro ao alterar a senha.")
    
    with col3:
        st.markdown("### Alterar E-mail")
        current_email = selected_user.get('email', '')
        new_email = st.text_input("Novo E-mail", value=current_email)
        
        if st.button("Salvar E-mail", type="primary", use_container_width=True):
            if not new_email:
                st.warning("O e-mail não pode ser vazio.")
            elif new_email == current_email:
                st.warning("Este já é o e-mail atual do usuário.")
            else:
                res = api_change_email(selected_user_id, new_email)
                if hasattr(res, 'status_code') and res.status_code == 200:
                    st.success("E-mail alterado com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao alterar o e-mail.")

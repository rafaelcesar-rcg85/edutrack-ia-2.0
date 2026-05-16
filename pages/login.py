import streamlit as st
import requests
from utils.api import BASE_URL

def tela_acesso():
    st.title('Portal Acadêmico Personalizado')
    tab_login, tab_cadastro = st.tabs(['Entrar', 'Criar Minha Conta'])

    with tab_login:
        with st.form('login_form'):
            email = st.text_input('E-mail')
            senha = st.text_input('Senha', type='password')
            if st.form_submit_button('Acessar Meu Painel'):
                res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': senha})
                if res.status_code == 200:
                    st.session_state.auth_token = res.json().get('authToken')
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    try:
                        error_msg = res.json().get('message', 'Credenciais inválidas.')
                    except:
                        error_msg = 'Credenciais inválidas.'
                    st.error(f'Erro no login: {error_msg}')

    with tab_cadastro:
        with st.form('cadastro_form'):
            nome = st.text_input('Nome')
            email_c = st.text_input('E-mail')
            pass_c = st.text_input('Senha', type='password')
            if st.form_submit_button('Cadastrar'):
                res = requests.post(f'{BASE_URL}/auth/signup', json={'name': nome, 'email': email_c, 'password': pass_c})
                if res.status_code == 200:
                    st.success('Conta criada! Agora faça o login.')
                else:
                    try:
                        error_msg = res.json().get('message', 'Erro ao cadastrar usuário.')
                    except:
                        error_msg = 'Erro ao cadastrar usuário.'
                    st.error(f'Erro no cadastro: {error_msg}')

tela_acesso()

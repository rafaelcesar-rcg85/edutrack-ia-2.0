import streamlit as st
import requests
from utils.api import BASE_URL, USER_PROFILES_URL


def _do_login(email: str, senha: str) -> bool:
    """
    Autentica o usuário, popula st.session_state e retorna True em caso de sucesso.
    Também cria/garante o perfil do usuário após o login.
    """
    res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': senha})
    if res.status_code != 200:
        try:
            msg = res.json().get('message', 'Credenciais inválidas.')
        except Exception:
            msg = 'Credenciais inválidas.'
        st.error(f'Erro no login: {msg}')
        return False

    token = res.json().get('authToken')
    headers = {'Authorization': f'Bearer {token}'}

    # Recuperar informações do usuário autenticado
    res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
    if res_me.status_code == 200:
        user_data = res_me.json()
        st.session_state.user_id = user_data.get('id')
        # Guarda o nome do usuário para exibir na UI
        st.session_state.user_name = user_data.get('name', '')

    # Busca e armazena o perfil do usuário na sessão
    p_val = {}
    try:
        res_profile = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
        if res_profile.status_code == 200 and res_profile.json():
            data = res_profile.json()
            if isinstance(data, list):
                p_val = data[0] if len(data) > 0 else {}
            elif isinstance(data, dict):
                p_val = data
                
        if not p_val or res_profile.status_code == 404:
            res_all = requests.get(f'{USER_PROFILES_URL}/user_profiles', headers=headers)
            if res_all.status_code == 200:
                all_profiles = res_all.json()
                if isinstance(all_profiles, list):
                    uid = st.session_state.get('user_id')
                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                    # Ordenar por ID para garantir a ordem (o maior ID é o mais recente)
                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                    if matched:
                        p_val = matched[-1]
    except Exception:
        pass
        
    st.session_state.user_profile = p_val

    st.session_state.auth_token = token
    st.session_state.logged_in = True
    return True


def _criar_perfil(token: str, first_name: str) -> None:
    """
    Tenta criar o perfil inicial do usuário via API.
    O vínculo com o usuário é feito automaticamente pelo Xano via $auth.id.
    """
    headers = {'Authorization': f'Bearer {token}'}

    # Verifica se o perfil já existe
    res_check = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
    perfil_existente = False
    if res_check.status_code == 200:
        val = res_check.json()
        # Se retornar um registro ou um array não-vazio, o perfil existe
        if val and (not isinstance(val, list) or len(val) > 0):
            perfil_existente = True

    if not perfil_existente:
        user_id = None
        try:
            res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
            if res_me.status_code == 200:
                user_id = res_me.json().get('id')
        except:
            pass

        payload = {'first_name': first_name, 'last_name': ''}
        if user_id:
            payload['user_id'] = user_id

        profile_res = requests.post(
            f'{USER_PROFILES_URL}/user_profiles',
            headers=headers,
            json=payload
        )
        if profile_res.status_code not in (200, 201):
            # Log para debugging — não bloqueia o login
            try:
                err = profile_res.json()
            except Exception:
                err = profile_res.text
            st.warning(f'Aviso: perfil não pôde ser criado automaticamente ({err}). '
                       'Você pode preencher seus dados na página "Meu Perfil".')


def tela_acesso():
    st.title('Portal Acadêmico Personalizado')
    tab_login, tab_cadastro = st.tabs(['Entrar', 'Criar Minha Conta'])

    with tab_login:
        with st.form('login_form'):
            email = st.text_input('E-mail')
            senha = st.text_input('Senha', type='password')
            if st.form_submit_button('Acessar Meu Painel'):
                if _do_login(email, senha):
                    st.rerun()

    with tab_cadastro:
        with st.form('cadastro_form'):
            nome = st.text_input('Nome')
            email_c = st.text_input('E-mail')
            pass_c = st.text_input('Senha', type='password')

            if st.form_submit_button('Cadastrar'):
                res = requests.post(
                    f'{BASE_URL}/auth/signup',
                    json={'name': nome, 'email': email_c, 'password': pass_c}
                )

                if res.status_code == 200:
                    # Login automático após cadastro — melhor UX e garante vinculação do perfil
                    login_res = requests.post(
                        f'{BASE_URL}/auth/login',
                        json={'email': email_c, 'password': pass_c}
                    )

                    if login_res.status_code == 200:
                        token_novo = login_res.json().get('authToken')

                        # Cria o perfil com o nome digitado no cadastro
                        # O Xano vincula ao usuário via $auth.id (token JWT)
                        _criar_perfil(token_novo, first_name=nome)

                        # Loga automaticamente para não precisar refazer o login
                        if _do_login(email_c, pass_c):
                            st.success(f'Bem-vindo, {nome}! Sua conta foi criada com sucesso.')
                            st.rerun()
                    else:
                        st.success('Conta criada! Agora faça o login.')
                else:
                    try:
                        error_msg = res.json().get('message', 'Erro ao cadastrar usuário.')
                    except Exception:
                        error_msg = 'Erro ao cadastrar usuário.'
                    st.error(f'Erro no cadastro: {error_msg}')


tela_acesso()

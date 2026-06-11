import streamlit as st
import requests
import datetime
from utils.api import BASE_URL, USER_PROFILES_URL, api_user_change_password, api_user_change_email
from utils.theme import apply_theme


def perfil_usuario():
    apply_theme()
    st.title('Meu Perfil')

    if not st.session_state.get('logged_in') or not st.session_state.get('auth_token'):
        st.warning('Você precisa estar logado para acessar esta página.')
        return

    token = st.session_state.auth_token
    headers = {'Authorization': f'Bearer {token}'}

    # ------------------------------------------------------------------
    # Buscar dados do perfil
    # ------------------------------------------------------------------
    profile_data = {}
    try:
        res = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                profile_data = data[0] if len(data) > 0 else {}
            elif isinstance(data, dict):
                profile_data = data

        if not profile_data or res.status_code == 404:
            res_all = requests.get(f'{USER_PROFILES_URL}/user_profiles', headers=headers)
            if res_all.status_code == 200:
                all_profiles = res_all.json()
                if isinstance(all_profiles, list):
                    uid = st.session_state.get('user_id')
                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                    if matched:
                        profile_data = matched[-1]
    except Exception:
        profile_data = {}

    # Buscar e-mail do usuário (tabela auth)
    user_email = ""
    try:
        res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
        if res_me.status_code == 200:
            user_email = res_me.json().get('email', '')
    except Exception:
        pass

    # ==================================================================
    # SEÇÃO 1 — Dados do Perfil
    # ==================================================================
    st.subheader('📋 Dados do Perfil')

    with st.form('profile_form'):
        session_name = st.session_state.get('user_name', '')
        first_name = st.text_input('Nome', value=profile_data.get('first_name', '') or session_name)
        last_name  = st.text_input('Sobrenome', value=profile_data.get('last_name', ''))

        email_input = st.text_input('E-mail', value=user_email,
                                    help='Altere seu e-mail de acesso aqui.')

        # Converter timestamp para date
        dob_value = profile_data.get('date_of_birth')
        if dob_value:
            try:
                dob_date = datetime.datetime.fromtimestamp(dob_value / 1000).date()
            except Exception:
                dob_date = datetime.date.today()
        else:
            dob_date = datetime.date.today()

        min_date = datetime.date(1940, 1, 1)
        max_date = datetime.date.today()
        date_of_birth = st.date_input(
            'Data de Nascimento',
            value=dob_date,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )

        if st.form_submit_button('💾 Salvar Perfil', use_container_width=True):
            payload = {
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': int(
                    datetime.datetime.combine(date_of_birth, datetime.time.min).timestamp() * 1000
                )
            }

            if 'user_id' in st.session_state:
                payload['user_id'] = st.session_state.user_id

            profile_id = profile_data.get('id')
            if profile_id:
                payload['user_profiles_id'] = profile_id
                payload['id'] = profile_id

            try:
                # Atualizar e-mail se foi alterado
                email_changed = email_input.strip() and email_input.strip() != user_email
                if email_changed:
                    email_res = api_user_change_email(email_input.strip())
                    if email_res.status_code not in (200, 201):
                        try:
                            email_err = email_res.json().get('message', email_res.text)
                        except Exception:
                            email_err = email_res.text
                        st.error(f"Erro ao atualizar e-mail: {email_err}")
                        st.stop()

                save_res = requests.post(
                    f"{USER_PROFILES_URL}/user_profiles",
                    headers=headers,
                    json=payload
                )

                if save_res.status_code in (200, 201):
                    success_msg = "✅ Perfil atualizado com sucesso!"
                    if email_changed:
                        success_msg += " E-mail alterado — use o novo e-mail no próximo login."
                    st.success(success_msg)

                    # Recarregar o perfil na sessão
                    try:
                        updated_res = requests.get(
                            f"{USER_PROFILES_URL}/user_profiles/me", headers=headers
                        )
                        p_val = {}
                        if updated_res.status_code == 200:
                            data = updated_res.json()
                            if isinstance(data, list):
                                p_val = data[0] if len(data) > 0 else {}
                            elif isinstance(data, dict):
                                p_val = data

                        if not p_val or updated_res.status_code == 404:
                            res_all = requests.get(
                                f'{USER_PROFILES_URL}/user_profiles', headers=headers
                            )
                            if res_all.status_code == 200:
                                all_profiles = res_all.json()
                                if isinstance(all_profiles, list):
                                    uid = st.session_state.get('user_id')
                                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                                    if matched:
                                        p_val = matched[-1]

                        st.session_state.user_profile = p_val
                    except Exception:
                        pass

                    st.rerun()
                else:
                    st.error(f"Erro ao salvar — Status {save_res.status_code}: {save_res.text}")

            except Exception as e:
                st.error(f"Erro de conexão: {str(e)}")

    # ==================================================================
    # SEÇÃO 2 — Trocar Senha
    # ==================================================================
    st.divider()
    st.subheader('🔒 Trocar Senha')

    with st.expander('Clique aqui para alterar sua senha', expanded=False):
        with st.form('change_password_form'):
            st.caption('Para sua segurança, informe a senha atual antes de definir uma nova.')

            current_password = st.text_input(
                'Senha Atual',
                type='password',
                placeholder='Digite sua senha atual',
                key='cp_current'
            )
            new_password = st.text_input(
                'Nova Senha',
                type='password',
                placeholder='Mínimo 6 caracteres',
                key='cp_new'
            )
            confirm_password = st.text_input(
                'Confirmar Nova Senha',
                type='password',
                placeholder='Repita a nova senha',
                key='cp_confirm'
            )

            submitted = st.form_submit_button('🔑 Alterar Senha', use_container_width=True)

            if submitted:
                # Validações no frontend
                if not current_password:
                    st.error('Informe a senha atual.')
                elif not new_password:
                    st.error('Informe a nova senha.')
                elif len(new_password) < 6:
                    st.error('A nova senha deve ter pelo menos 6 caracteres.')
                elif new_password != confirm_password:
                    st.error('A confirmação de senha não confere. Tente novamente.')
                elif new_password == current_password:
                    st.warning('A nova senha não pode ser igual à senha atual.')
                else:
                    with st.spinner('Alterando senha...'):
                        res = api_user_change_password(current_password, new_password)

                    if res.status_code in (200, 201):
                        st.success('✅ Senha alterada com sucesso! Use a nova senha no próximo login.')
                    elif res.status_code == 401:
                        st.error('❌ Senha atual incorreta. Verifique e tente novamente.')
                    elif res.status_code == 503:
                        st.error('❌ Serviço temporariamente indisponível. Tente mais tarde.')
                    else:
                        try:
                            msg = res.json().get('message', res.text)
                        except Exception:
                            msg = res.text
                        st.error(f'❌ Erro ao alterar senha: {msg}')


perfil_usuario()
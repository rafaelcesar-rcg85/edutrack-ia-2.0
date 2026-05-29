import streamlit as st
import requests
from utils.api import BASE_URL, USER_PROFILES_URL
import datetime

def perfil_usuario():
    st.title('Meu Perfil')

    if not st.session_state.get('logged_in') or not st.session_state.get('auth_token'):
        st.warning('Você precisa estar logado para acessar esta página.')
        return

    token = st.session_state.auth_token
    headers = {'Authorization': f'Bearer {token}'}

    # Buscar dados do perfil
    try:
        res = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
        profile_data = (res.json() or {}) if res.status_code == 200 else {}
    except:
        profile_data = {}

    # Buscar e-mail do usuário (tabela auth)
    user_email = ""
    try:
        res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
        if res_me.status_code == 200:
            user_email = res_me.json().get('email', '')
    except:
        pass

    with st.form('profile_form'):
        # Fallback: usa o nome da sessão (vindo do cadastro) se o perfil ainda não tiver dados
        session_name = st.session_state.get('user_name', '')
        first_name = st.text_input('Nome', value=profile_data.get('first_name', '') or session_name)
        last_name = st.text_input('Sobrenome', value=profile_data.get('last_name', ''))
        
        # Campo de E-mail
        email_input = st.text_input('E-mail', value=user_email)
        
        # Converter timestamp para date
        dob_value = profile_data.get('date_of_birth')
        if dob_value:
            # timestamp in Xano is usually in milliseconds
            try:
                dob_date = datetime.datetime.fromtimestamp(dob_value / 1000).date()
            except:
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
        if st.form_submit_button('Salvar Perfil'):
            # Preparar payload básico
            payload = {
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': int(datetime.datetime.combine(date_of_birth, datetime.time.min).timestamp() * 1000)
            }
            try:
                # Enviar via JSON

                save_res = requests.post(
                    f"{USER_PROFILES_URL}/user_profiles",
                    headers=headers,
                    json=payload
                )

                if save_res.status_code == 200:
                    st.success("Perfil atualizado com sucesso!")

                    # Recarregar o perfil no estado da sessão
                    try:
                        updated_res = requests.get(f"{USER_PROFILES_URL}/user_profiles/me", headers=headers)
                        if updated_res.status_code == 200:
                            st.session_state.user_profile = updated_res.json()
                    except:
                        pass

                    st.rerun()
                else:
                    msg = save_res.json().get('message', 'Erro desconhecido ao salvar o perfil')
                    st.error(msg)

            except Exception as e:
                st.error(f"Erro de conexão: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

perfil_usuario()
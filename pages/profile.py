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
    profile_data = {}
    try:
        # Tenta a rota /me primeiro
        res = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                profile_data = data[0] if len(data) > 0 else {}
            elif isinstance(data, dict):
                profile_data = data
        
        # Se não encontrou ou a rota não existe, tenta buscar na listagem geral e filtrar
        if not profile_data or res.status_code == 404:
            res_all = requests.get(f'{USER_PROFILES_URL}/user_profiles', headers=headers)
            if res_all.status_code == 200:
                all_profiles = res_all.json()
                if isinstance(all_profiles, list):
                    # Pega o último perfil (mais recente) onde o user_id bate com o da sessão
                    uid = st.session_state.get('user_id')
                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                    if matched:
                        profile_data = matched[-1]
    except Exception as e:
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
            
            if 'user_id' in st.session_state:
                payload['user_id'] = st.session_state.user_id
            
            profile_id = profile_data.get('id')
            if profile_id:
                payload['user_profiles_id'] = profile_id
                payload['id'] = profile_id
                
            try:
                save_res = requests.post(
                    f"{USER_PROFILES_URL}/user_profiles",
                    headers=headers,
                    json=payload
                )

                if save_res.status_code in (200, 201):
                    st.success("Perfil atualizado com sucesso!")

                    # Recarregar o perfil no estado da sessão
                    try:
                        updated_res = requests.get(f"{USER_PROFILES_URL}/user_profiles/me", headers=headers)
                        p_val = {}
                        if updated_res.status_code == 200:
                            data = updated_res.json()
                            if isinstance(data, list):
                                p_val = data[0] if len(data) > 0 else {}
                            elif isinstance(data, dict):
                                p_val = data
                                
                        if not p_val or updated_res.status_code == 404:
                            res_all = requests.get(f'{USER_PROFILES_URL}/user_profiles', headers=headers)
                            if res_all.status_code == 200:
                                all_profiles = res_all.json()
                                if isinstance(all_profiles, list):
                                    uid = st.session_state.get('user_id')
                                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                                    if matched:
                                        p_val = matched[-1]
                                        
                        st.session_state.user_profile = p_val
                    except:
                        pass

                    st.rerun()
                else:
                    st.error(f"Erro do Xano - Status {save_res.status_code}: {save_res.text}")

            except Exception as e:
                st.error(f"Erro de conexão: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

perfil_usuario()
import requests
import streamlit as st

BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'
USER_PROFILES_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'

def get_headers():
    '''
    Gera o cabeçalho com o JSON Web Token (JWT) para autenticação segura.
    '''
    headers = {'Content-Type': 'application/json'}
    if 'auth_token' in st.session_state:
        headers['Authorization'] = f'Bearer {st.session_state.auth_token}'
    return headers

@st.cache_data(ttl=60)
def _cached_api_get(endpoint, auth_token, user_id):
    headers = {'Content-Type': 'application/json'}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    try:
        resposta = requests.get(f'{BASE_URL}/{endpoint}', headers=headers)
        dados = resposta.json() if resposta.status_code == 200 else []
        
        # Filtrar no frontend pelo user_id para garantir que o usuário só veja os seus próprios dados
        if user_id and isinstance(dados, list):
            dados = [item for item in dados if item.get('user_id') == user_id or 'user_id' not in item]
            
        return dados
    except requests.exceptions.RequestException as e:
        return None # Indica erro de conexão

def api_get(endpoint):
    '''
    Lê dados do Xano (filtra automaticamente pelo usuário no servidor ou no frontend).
    '''
    auth_token = st.session_state.get('auth_token')
    user_id = st.session_state.get('user_id')
    
    dados = _cached_api_get(endpoint, auth_token, user_id)
    if dados is None:
        st.error(f"Erro de conexão com o servidor: Não foi possível acessar '{endpoint}'. O Xano pode estar indisponível.")
        return []
    return dados

def clear_api_cache():
    _cached_api_get.clear()

def api_post(endpoint, dados):
    '''
    Cria um novo registro vinculado ao aluno logado.
    '''
    try:
        res = requests.post(f'{BASE_URL}/{endpoint}', json=dados, headers=get_headers())
        clear_api_cache()
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível salvar em '{endpoint}'.")
        # Retorna um objeto mockado com status_code de erro para não quebrar o resto do código
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

def api_patch(endpoint, id, dados):
    '''
    Atualiza um registro existente.
    '''
    try:
        res = requests.patch(f'{BASE_URL}/{endpoint}/{id}', json=dados, headers=get_headers())
        clear_api_cache()
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível atualizar o registro em '{endpoint}'.")
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

def api_delete(endpoint, id):
    '''
    Remove um registro do banco de dados.
    '''
    try:
        res = requests.delete(f'{BASE_URL}/{endpoint}/{id}', headers=get_headers())
        clear_api_cache()
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível deletar o registro em '{endpoint}'.")
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

# --- Funções Administrativas ---

ADMIN_BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:6_aEAYGN'

def api_get_users():
    '''Retorna todos os usuários (requer permissão de admin).'''
    try:
        res = requests.get(f'{ADMIN_BASE_URL}/users', headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def api_change_role(user_id, role):
    '''Altera o papel (role) de um usuário.'''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_role/{user_id}', json={'role': role}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_change_email(user_id, email):
    '''Altera o email de um usuário.'''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_email/{user_id}', json={'email': email}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_change_password(user_id, password):
    '''Altera a senha de um usuário.'''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_password/{user_id}', json={'password': password}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_delete_user(user_id):
    '''Deleta a conta de um usuário (com cascata local).'''
    try:
        return requests.delete(f'{ADMIN_BASE_URL}/user/{user_id}', headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

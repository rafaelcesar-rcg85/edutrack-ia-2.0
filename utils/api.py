import requests
import streamlit as st

BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'
USER_PROFILES_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:XzuWZAhQ'

def get_headers():
    '''
    Gera o cabeçalho com o JSON Web Token (JWT) para autenticação segura.
    '''
    headers = {'Content-Type': 'application/json'}
    if 'auth_token' in st.session_state:
        headers['Authorization'] = f'Bearer {st.session_state.auth_token}'
    return headers

def api_get(endpoint, params=None):
    '''
    Lê dados do Xano (filtra automaticamente pelo usuário no servidor ou no frontend).
    Suporta query params para filtrar por course_id.
    '''
    try:
        resposta = requests.get(f'{BASE_URL}/{endpoint}', headers=get_headers(), params=params)
        dados = resposta.json() if resposta.status_code == 200 else []
        
        # Filtrar no frontend pelo user_id e course_id para garantir a consistência
        if isinstance(dados, list):
            if 'user_id' in st.session_state:
                dados = [item for item in dados if item.get('user_id') == st.session_state.user_id or 'user_id' not in item]
            
            # Filtro temporário no frontend caso o Xano ainda não esteja filtrando por course_id
            if params and 'course_id' in params and params['course_id'] is not None:
                dados = [item for item in dados if item.get('course_id') == params['course_id'] or 'course_id' not in item]
                
        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com o servidor: Não foi possível acessar '{endpoint}'. O Xano pode estar indisponível.")
        return []

def api_post(endpoint, dados):
    '''
    Cria um novo registro vinculado ao aluno logado.
    '''
    try:
        return requests.post(f'{BASE_URL}/{endpoint}', json=dados, headers=get_headers())
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
        return requests.patch(f'{BASE_URL}/{endpoint}/{id}', json=dados, headers=get_headers())
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
        return requests.delete(f'{BASE_URL}/{endpoint}/{id}', headers=get_headers())
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível deletar o registro em '{endpoint}'.")
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

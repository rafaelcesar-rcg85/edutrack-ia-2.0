import requests
import streamlit as st

BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'

def get_headers():
    '''
    Gera o cabeçalho com o JSON Web Token (JWT) para autenticação segura.
    '''
    headers = {'Content-Type': 'application/json'}
    if 'auth_token' in st.session_state:
        headers['Authorization'] = f'Bearer {st.session_state.auth_token}'
    return headers

def api_get(endpoint):
    '''
    Lê dados do Xano (filtra automaticamente pelo usuário no servidor).
    '''
    resposta = requests.get(f'{BASE_URL}/{endpoint}', headers=get_headers())
    return resposta.json() if resposta.status_code == 200 else []

def api_post(endpoint, dados):
    '''
    Cria um novo registro vinculado ao aluno logado.
    '''
    return requests.post(f'{BASE_URL}/{endpoint}', json=dados, headers=get_headers())

def api_patch(endpoint, id, dados):
    '''
    Atualiza um registro existente.
    '''
    return requests.patch(f'{BASE_URL}/{endpoint}/{id}', json=dados, headers=get_headers())

def api_delete(endpoint, id):
    '''
    Remove um registro do banco de dados.
    '''
    return requests.delete(f'{BASE_URL}/{endpoint}/{id}', headers=get_headers())

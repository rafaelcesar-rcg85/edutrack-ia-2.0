"""
=============================================================
 utils/api.py — Camada de Comunicação com o Backend (Xano)
=============================================================
 Este arquivo centraliza TODAS as chamadas HTTP para a API
 do Xano. Ao invés de espalhar chamadas requests.get() por
 todo o projeto, usamos funções reutilizáveis aqui.

 Conceitos importantes:
   - REST API: padrão de comunicação web via HTTP
   - JWT (JSON Web Token): token de autenticação gerado
     pelo Xano no login e enviado em cada requisição
   - CRUD: Create (POST), Read (GET), Update (PATCH),
           Delete (DELETE)
   - Cache: armazenar resultados temporariamente para
     não fazer a mesma requisição várias vezes
=============================================================
"""

# ─── Importações ────────────────────────────────────────────
import requests    # Biblioteca Python para fazer chamadas HTTP
import streamlit as st  # Usado para acessar a sessão do usuário e exibir erros

# ============================================================
# URLs BASE DAS APIs DO XANO
# ============================================================
# Estas são as URLs raiz de cada grupo de API no Xano.
# Todo endpoint (ex: /courses, /disciplinas) é concatenado a elas.
BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'
USER_PROFILES_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'

# ============================================================
# AUTENTICAÇÃO — CABEÇALHO JWT
# ============================================================
def get_headers():
    '''
    Gera o cabeçalho HTTP com o JSON Web Token (JWT) para autenticação segura.
    
    O JWT é obtido no login e armazenado em st.session_state.auth_token.
    Ele é enviado no cabeçalho 'Authorization' de todas as requisições
    para que o Xano saiba quem está fazendo a chamada.
    
    Formato padrão: Authorization: Bearer <token>
    '''
    headers = {'Content-Type': 'application/json'}
    # Adiciona o token de autenticação se o usuário estiver logado
    if 'auth_token' in st.session_state:
        headers['Authorization'] = f'Bearer {st.session_state.auth_token}'
    return headers

# ============================================================
# [R]EAD — LEITURA COM CACHE
# ============================================================
@st.cache_data(ttl=60)
def _cached_api_get(endpoint, auth_token, user_id):
    """
    Versão interna do GET com cache de 60 segundos.
    
    @st.cache_data(ttl=60) significa que o resultado desta função
    é armazenado em memória por 60 segundos. Se a mesma requisição
    for feita dentro desse tempo, o Streamlit retorna o resultado
    salvo sem bater na API novamente — mais rápido e econômico.
    
    Parâmetros:
        endpoint   — caminho do recurso, ex: 'courses' ou 'disciplinas'
        auth_token — token JWT do usuário logado
        user_id    — ID do usuário, usado para filtrar os dados no frontend
    """
    headers = {'Content-Type': 'application/json'}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    try:
        # Monta a URL completa e faz a requisição GET
        resposta = requests.get(f'{BASE_URL}/{endpoint}', headers=headers)
        
        # Se a resposta foi OK (200), converte o JSON; caso contrário retorna lista vazia
        dados = resposta.json() if resposta.status_code == 200 else []
        
        # Filtrar no frontend pelo user_id para garantir que o usuário só veja os seus próprios dados
        # (segurança extra além da autenticação no Xano)
        if user_id and isinstance(dados, list):
            dados = [item for item in dados if item.get('user_id') == user_id or 'user_id' not in item]
            
        return dados
    except requests.exceptions.RequestException as e:
        return None  # Indica erro de conexão

def api_get(endpoint):
    '''
    Função pública de leitura de dados do Xano.
    
    Recupera a lista de registros de um endpoint.
    Filtra automaticamente pelo usuário logado (via token + user_id).
    
    Uso: cursos = api_get('curso')
    '''
    # Pega o token e o ID do usuário da sessão atual
    auth_token = st.session_state.get('auth_token')
    user_id = st.session_state.get('user_id')
    
    dados = _cached_api_get(endpoint, auth_token, user_id)
    
    # Se houve erro de conexão, exibe mensagem amigável e retorna lista vazia
    if dados is None:
        st.error(f"Erro de conexão com o servidor: Não foi possível acessar '{endpoint}'. O Xano pode estar indisponível.")
        return []
    return dados

def clear_api_cache():
    """
    Limpa o cache do GET após qualquer operação de escrita (POST, PATCH, DELETE).
    Isso garante que a próxima leitura busque dados atualizados do servidor.
    """
    _cached_api_get.clear()

# ============================================================
# [C]REATE — CRIAÇÃO DE REGISTRO
# ============================================================
def api_post(endpoint, dados):
    '''
    Cria um novo registro no banco de dados do Xano.
    
    Envia os dados via método HTTP POST no formato JSON.
    Após sucesso, limpa o cache para que a listagem seja atualizada.
    
    Uso: api_post('curso', {'name': 'Engenharia', 'status': 'cursando'})
    '''
    try:
        res = requests.post(f'{BASE_URL}/{endpoint}', json=dados, headers=get_headers())
        clear_api_cache()  # Invalida o cache para refletir o novo registro
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível salvar em '{endpoint}'.")
        # Retorna um objeto mockado com status_code de erro para não quebrar o resto do código
        # (evita que a aplicação trave por falta do objeto de resposta)
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

# ============================================================
# [U]PDATE — ATUALIZAÇÃO DE REGISTRO
# ============================================================
def api_patch(endpoint, id, dados):
    '''
    Atualiza um registro existente no Xano.
    
    Usa o método HTTP PATCH, que atualiza apenas os campos enviados
    (diferente do PUT, que substitui o registro inteiro).
    A URL inclui o ID do registro: /endpoint/{id}
    
    Uso: api_patch('curso', 5, {'status': 'formado'})
    '''
    try:
        res = requests.patch(f'{BASE_URL}/{endpoint}/{id}', json=dados, headers=get_headers())
        clear_api_cache()  # Invalida o cache para refletir a atualização
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível atualizar o registro em '{endpoint}'.")
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

# ============================================================
# [D]ELETE — REMOÇÃO DE REGISTRO
# ============================================================
def api_delete(endpoint, id):
    '''
    Remove um registro do banco de dados.
    
    Usa o método HTTP DELETE passando o ID do registro na URL.
    
    Uso: api_delete('curso', 5)
    '''
    try:
        res = requests.delete(f'{BASE_URL}/{endpoint}/{id}', headers=get_headers())
        clear_api_cache()  # Invalida o cache para refletir a remoção
        return res
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: Não foi possível deletar o registro em '{endpoint}'.")
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

# ============================================================
# FUNÇÕES ADMINISTRATIVAS (requerem permissão de admin)
# ============================================================
# URL de uma API separada no Xano com endpoints exclusivos para admins
ADMIN_BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:6_aEAYGN'

def api_get_users():
    '''Retorna todos os usuários cadastrados (requer permissão de admin).'''
    try:
        res = requests.get(f'{ADMIN_BASE_URL}/users', headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def api_get_login_stats():
    '''Retorna frequência de logins por usuário a partir do event_log.'''
    try:
        res = requests.get(f'{ADMIN_BASE_URL}/login_stats', headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def api_get_all_events():
    '''Retorna todos os eventos do event_log para análise administrativa.'''
    try:
        res = requests.get(f'{ADMIN_BASE_URL}/event_log_all', headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def api_change_role(user_id, role):
    '''
    Altera o papel (role) de um usuário: 'user' ou 'admin'.
    Apenas administradores têm acesso a esta função.
    '''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_role/{user_id}', json={'role': role}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_change_email(user_id, email):
    '''
    Altera o email de um usuário específico (função administrativa).
    Diferente da api_user_change_email que o próprio usuário chama.
    '''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_email/{user_id}', json={'email': email}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_change_password(user_id, password):
    '''Altera a senha de qualquer usuário (função administrativa).'''
    try:
        return requests.patch(f'{ADMIN_BASE_URL}/user_password/{user_id}', json={'password': password}, headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

def api_user_change_password(current_password, new_password):
    '''
    Troca a senha do próprio usuário autenticado.
    
    Fluxo de segurança em duas etapas:
      1. Valida a senha ATUAL fazendo um re-login (prova que o usuário conhece a senha)
      2. Se o re-login der certo, aplica a nova senha via PATCH
    
    Isso evita que alguém que encontrou uma sessão aberta troque a senha sem saber a atual.
    '''
    # Classe auxiliar para simular uma resposta HTTP em caso de erro
    class MockResponse:
        def __init__(self, code, msg):
            self.status_code = code
            self.text = msg
        def json(self):
            return {"message": self.text}

    try:
        # 1) Confirma a senha atual via login
        user_email = st.session_state.get('user_email', '')
        if not user_email:
            # Busca o e-mail do usuário autenticado via /auth/me
            me_res = requests.get(f'{BASE_URL}/auth/me', headers=get_headers())
            if me_res.status_code == 200:
                user_email = me_res.json().get('email', '')

        if not user_email:
            return MockResponse(400, 'Não foi possível obter o e-mail do usuário.')

        # Tentativa de login com a senha atual para validação
        verify_res = requests.post(
            f'{BASE_URL}/auth/login',
            json={'email': user_email, 'password': current_password}
        )
        # Se o login falhar, a senha atual está errada — aborta
        if verify_res.status_code != 200:
            return MockResponse(401, 'Senha atual incorreta.')

        # 2) Aplica a nova senha via endpoint customizado no Xano
        return requests.patch(
            f'{BASE_URL}/auth/change_password',
            json={'new_password': new_password},
            headers=get_headers()
        )
    except requests.exceptions.RequestException:
        return MockResponse(503, 'Serviço Indisponível')

def api_user_change_email(new_email):
    '''
    Permite que o próprio usuário autenticado atualize seu e-mail.
    O Xano identifica qual usuário é pelo token JWT no cabeçalho.
    '''
    try:
        return requests.patch(
            f'{BASE_URL}/auth/change_email',
            json={'new_email': new_email},
            headers=get_headers()
        )
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
            text = "Serviço Indisponível"
            def json(self): return {"message": self.text}
        return MockResponse()

def api_delete_user(user_id):
    '''
    Deleta a conta de um usuário (apenas administradores).
    A exclusão em cascata (dados relacionados) é tratada no Xano.
    '''
    try:
        return requests.delete(f'{ADMIN_BASE_URL}/user/{user_id}', headers=get_headers())
    except requests.exceptions.RequestException:
        class MockResponse:
            status_code = 503
        return MockResponse()

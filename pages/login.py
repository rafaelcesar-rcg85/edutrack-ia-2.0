"""
=============================================================
 pages/login.py — Tela de Login e Cadastro
=============================================================
 Esta página controla o acesso ao sistema:
   - Aba "Entrar": autentica o usuário existente
   - Aba "Criar Minha Conta": registra um novo usuário

 Fluxo de autenticação:
   1. Usuário envia email + senha
   2. Fazemos POST para /auth/login no Xano
   3. O Xano retorna um token JWT
   4. Armazenamos o token na sessão (st.session_state)
   5. Todas as próximas requisições usam esse token
=============================================================
"""

# ─── Importações ────────────────────────────────────────────
import streamlit as st  # Framework de interface web
import requests          # Biblioteca para chamadas HTTP
from utils.api import BASE_URL, USER_PROFILES_URL  # URLs da API Xano


# ============================================================
# FUNÇÃO DE LOGIN (LÓGICA INTERNA)
# ============================================================
def _do_login(email: str, senha: str) -> bool:
    """
    Realiza o login completo do usuário e popula a sessão.
    
    Retorna True se o login for bem-sucedido, False caso contrário.
    O prefixo _ indica que é uma função interna (uso privado neste arquivo).
    
    Etapas:
      1. POST /auth/login  → obtém o token JWT
      2. GET  /auth/me     → obtém os dados do usuário (id, nome, role)
      3. GET  /user_profiles/me → carrega o perfil completo (foto, nascimento etc.)
    """
    # Etapa 1: Autenticação — envia email e senha para o Xano
    res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': senha})
    
    # Se o servidor retornar algo diferente de 200, o login falhou
    if res.status_code != 200:
        try:
            msg = res.json().get('message', 'Credenciais inválidas.')
        except Exception:
            msg = 'Credenciais inválidas.'
        st.error(f'Erro no login: {msg}')
        return False

    # Extrai o token JWT da resposta do Xano
    token = res.json().get('authToken')
    # Monta o cabeçalho de autorização para as próximas chamadas desta função
    headers = {'Authorization': f'Bearer {token}'}

    # Etapa 2: Busca os dados do usuário autenticado
    res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
    if res_me.status_code == 200:
        user_data = res_me.json()
        st.session_state.user_id   = user_data.get('id')
        # Guarda o nome do usuário para exibir na UI
        st.session_state.user_name = user_data.get('name', '')
        # Guarda o papel do usuário (role): 'user' ou 'admin'
        st.session_state.user_role = user_data.get('role', 'user')

    # Etapa 3: Busca o perfil estendido do usuário (dados do user_profiles)
    p_val = {}
    try:
        res_profile = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
        if res_profile.status_code == 200 and res_profile.json():
            data = res_profile.json()
            # A API pode retornar um objeto ou uma lista — tratamos os dois casos
            if isinstance(data, list):
                p_val = data[0] if len(data) > 0 else {}
            elif isinstance(data, dict):
                p_val = data
                
        # Se não encontrou o perfil na rota /me, tenta buscar em todos os perfis
        if not p_val or res_profile.status_code == 404:
            res_all = requests.get(f'{USER_PROFILES_URL}/user_profiles', headers=headers)
            if res_all.status_code == 200:
                all_profiles = res_all.json()
                if isinstance(all_profiles, list):
                    uid = st.session_state.get('user_id')
                    # Filtra os perfis que pertencem ao usuário logado
                    matched = [p for p in all_profiles if p.get('user_id') == uid]
                    # Ordenar por ID para garantir a ordem (o maior ID é o mais recente)
                    matched = sorted(matched, key=lambda x: x.get('id', 0))
                    if matched:
                        p_val = matched[-1]  # Pega o perfil mais recente
    except Exception:
        pass  # Em caso de erro no perfil, não bloqueia o login
        
    # Salva o perfil na sessão para uso nas outras páginas
    st.session_state.user_profile = p_val

    # Finaliza o login: salva o token e marca o usuário como logado
    st.session_state.auth_token = token
    st.session_state.logged_in  = True

    # Restaura o tema salvo no Xano (silencioso — não bloqueia se falhar)
    try:
        from utils.api import api_load_theme
        from utils.theme import save_theme_to_session, DEFAULT_THEMES, DEFAULT_THEME_KEY
        saved_theme = api_load_theme()
        if saved_theme:
            # Salva na sessão SEM chamar api_save_theme (já está salvo no Xano)
            st.session_state.theme = saved_theme
            st.session_state.theme_key = saved_theme.get('name', 'custom').lower().replace(' ', '_')
        # Se não tiver tema salvo, mantém o padrão (já inicializado pelo get_theme())
    except Exception:
        pass

    return True


# ============================================================
# FUNÇÃO DE CRIAÇÃO DE PERFIL (APÓS CADASTRO)
# ============================================================
def _criar_perfil(token: str, first_name: str) -> None:
    """
    Cria o perfil inicial do usuário logo após o cadastro.
    
    O Xano vincula o perfil ao usuário automaticamente via $auth.id
    (identificado pelo token JWT enviado no cabeçalho).
    
    Importante: falhas aqui NÃO bloqueiam o acesso — apenas exibem um aviso.
    """
    headers = {'Authorization': f'Bearer {token}'}

    # Verifica se o perfil já existe antes de tentar criar
    res_check = requests.get(f'{USER_PROFILES_URL}/user_profiles/me', headers=headers)
    perfil_existente = False
    if res_check.status_code == 200:
        val = res_check.json()
        # Se retornar um registro ou um array não-vazio, o perfil existe
        if val and (not isinstance(val, list) or len(val) > 0):
            perfil_existente = True

    # Só cria o perfil se ele ainda não existir
    if not perfil_existente:
        user_id = None
        try:
            # Busca o ID do usuário recém-criado para vincular ao perfil
            res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
            if res_me.status_code == 200:
                user_id = res_me.json().get('id')
        except:
            pass

        # Monta o payload com o primeiro nome (sobrenome vazio por padrão)
        payload = {'first_name': first_name, 'last_name': ''}
        if user_id:
            payload['user_id'] = user_id

        # Envia a criação do perfil para o Xano
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


# ============================================================
# INTERFACE DA TELA DE ACESSO (LOGIN E CADASTRO)
# ============================================================
def tela_acesso():
    """
    Renderiza a interface da tela de login/cadastro com duas abas:
      - Aba 1: Formulário de login
      - Aba 2: Formulário de criação de conta
    """
    st.title('Portal Acadêmico Personalizado')
    
    # st.tabs cria abas na interface — o usuário clica para alternar
    tab_login, tab_cadastro = st.tabs(['Entrar', 'Criar Minha Conta'])

    # ── Aba de Login ──────────────────────────────────────────
    with tab_login:
        # st.form agrupa campos e botão; o submit só dispara quando o botão é clicado
        with st.form('login_form'):
            email = st.text_input('E-mail')
            senha = st.text_input('Senha', type='password')  # type='password' oculta o texto
            if st.form_submit_button('Acessar Meu Painel'):
                if _do_login(email, senha):
                    st.rerun()  # Recarrega o app → redireciona para o dashboard

    # ── Aba de Cadastro ───────────────────────────────────────
    with tab_cadastro:
        with st.form('cadastro_form'):
            nome       = st.text_input('Nome')
            email_c    = st.text_input('E-mail')
            pass_c     = st.text_input('Senha',           type='password')
            pass_confirm = st.text_input('Confirmar Senha', type='password')

            if st.form_submit_button('Cadastrar'):
                # Validações antes de enviar para a API
                if not pass_c:
                    st.error("A senha não pode ser vazia.")
                elif pass_c != pass_confirm:
                    st.error("As senhas não coincidem. Tente novamente.")
                else:
                    # Envia o cadastro para o Xano via /auth/signup
                    res = requests.post(
                        f'{BASE_URL}/auth/signup',
                        json={'name': nome, 'email': email_c, 'password': pass_c, 'role': 'user'}
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
                                st.rerun()  # Redireciona para o dashboard
                        else:
                            st.success('Conta criada! Agora faça o login.')
                    else:
                        # Exibe a mensagem de erro retornada pelo Xano
                        try:
                            error_msg = res.json().get('message', 'Erro ao cadastrar usuário.')
                        except Exception:
                            error_msg = 'Erro ao cadastrar usuário.'
                        st.error(f'Erro no cadastro: {error_msg}')


# ─── Ponto de entrada desta página ──────────────────────────
# O Streamlit executa este arquivo diretamente; chamamos a função principal aqui.
tela_acesso()

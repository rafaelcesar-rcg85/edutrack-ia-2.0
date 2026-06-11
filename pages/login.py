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
from utils.theme import apply_theme  # Sistema de temas visuais


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
def _criar_perfil(token: str, full_name: str) -> None:
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

        # Separa o nome completo em nome e sobrenome
        parts = full_name.strip().split(maxsplit=1)
        if len(parts) > 1:
            first_name = parts[0]
            last_name = parts[1]
        else:
            first_name = parts[0] if parts else ''
            last_name = '-'  # O Xano exige sobrenome não vazio

        payload = {'first_name': first_name, 'last_name': last_name}
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
    apply_theme()
    # Adicionar estilo CSS local para alinhar e suavizar as bordas das colunas
    st.markdown("<style>.block-container{max-width: 1200px; padding-top: 2rem;}</style>", unsafe_allow_html=True)
    
    st.title('🎓 EduTrack AI')
    st.caption('Acompanhe sua jornada acadêmica de forma inteligente e personalizada.')
    
    col_form, col_preview = st.columns([5, 6], gap="large")
    
    with col_form:
        # st.tabs cria abas na interface — o usuário clica para alternar
        tab_login, tab_cadastro = st.tabs(['Entrar', 'Criar Minha Conta'])

        # ── Aba de Login ──────────────────────────────────────────
        with tab_login:
            # st.form agrupa campos e botão; o submit só dispara quando o botão é clicado
            with st.form('login_form'):
                email = st.text_input(
                    'E-mail',
                    placeholder='seu.email@exemplo.com',
                    help='Digite seu e-mail acadêmico ou pessoal cadastrado.'
                )
                senha = st.text_input(
                    'Senha',
                    type='password',
                    placeholder='Digite sua senha',
                    help='Digite a senha vinculada a esta conta.'
                )
                if st.form_submit_button('Acessar Meu Painel', use_container_width=True):
                    if _do_login(email, senha):
                        st.rerun()  # Recarrega o app → redireciona para o dashboard

        # ── Aba de Cadastro ───────────────────────────────────────
        with tab_cadastro:
            with st.form('cadastro_form'):
                nome       = st.text_input(
                    'Nome Completo',
                    placeholder='Ex: João Silva',
                    help='Insira seu nome e sobrenome. O sistema irá dividi-los para preencher seu perfil.'
                )
                email_c    = st.text_input(
                    'E-mail',
                    placeholder='exemplo@email.com',
                    help='Utilize o e-mail principal com o qual deseja acessar o sistema.'
                )
                pass_c     = st.text_input(
                    'Senha',
                    type='password',
                    placeholder='Mínimo 8 caracteres (com letras e números)',
                    help='Crie uma senha de acesso contendo no mínimo 8 caracteres e pelo menos uma letra e um número.'
                )
                pass_confirm = st.text_input(
                    'Confirmar Senha',
                    type='password',
                    placeholder='Repita a senha acima',
                    help='Digite exatamente a mesma senha para confirmação.'
                )

                if st.form_submit_button('Cadastrar', use_container_width=True):
                    # Validações antes de enviar para a API
                    if not nome.strip():
                        st.error("O nome não pode ser vazio.")
                    elif not email_c.strip():
                        st.error("O e-mail não pode ser vazio.")
                    elif not pass_c:
                        st.error("A senha não pode ser vazia.")
                    elif len(pass_c) < 8 or not any(c.isalpha() for c in pass_c) or not any(c.isdigit() for c in pass_c):
                        st.error("A senha deve ter pelo menos 8 caracteres e conter pelo menos uma letra e um número.")
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
                                _criar_perfil(token_novo, full_name=nome)

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

    with col_preview:
        st.markdown(
            """
            <div style="background: var(--banner-grad); padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid var(--primary); box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                <h3 style="color: var(--banner-title); margin: 0 0 5px 0; font-family: var(--font-family); font-weight: 700;">Bem-vindo ao EduTrack AI! 🚀</h3>
                <p style="color: var(--text-muted); margin: 0; font-size: 0.9em; line-height: 1.4;">
                    Seu assistente acadêmico inteligente. Organize notas, acompanhe prazos de entrega, visualize relatórios de desempenho e gerencie sua vida acadêmica.
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="background: white; padding: 18px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border-top: 4px solid var(--primary); text-align: center;">
                    <p style="color: var(--text-muted); font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 5px 0;">MÉDIA GERAL</p>
                    <h2 style="color: var(--secondary); margin: 0; font-size: 2em; font-weight: 700;">9.20</h2>
                </div>
                <div style="background: white; padding: 18px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); border-top: 4px solid #27ae60; text-align: center;">
                    <p style="color: var(--text-muted); font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 5px 0;">TAXA DE CONCLUSÃO</p>
                    <h2 style="color: #27ae60; margin: 0; font-size: 2em; font-weight: 700;">85.7%</h2>
                </div>
            </div>
            
            <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #edf2f7; margin-bottom: 20px;">
                <h4 style="margin: 0 0 15px 0; color: var(--text-main); font-weight: 600; display: flex; align-items: center; gap: 8px;">
                    📅 Visão Geral de Atividades
                </h4>
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f7fafc; padding-bottom: 10px; margin-bottom: 10px;">
                    <div style="text-align: left;">
                        <span style="font-weight: 600; font-size: 0.9em; color: var(--text-main); display: block;">Trabalho de Inteligência Artificial</span>
                        <span style="font-size: 0.75em; color: var(--text-muted);">Disciplina: Ciência da Computação</span>
                    </div>
                    <span style="background: #def7ec; color: #03543f; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold; border: 1px solid #b2f5ea;">NOTA: 9.5</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #f7fafc; padding-bottom: 10px; margin-bottom: 10px;">
                    <div style="text-align: left;">
                        <span style="font-weight: 600; font-size: 0.9em; color: var(--text-main); display: block;">Prova de Cálculo II</span>
                        <span style="font-size: 0.75em; color: var(--text-muted);">Disciplina: Matemática Aplicada</span>
                    </div>
                    <span style="background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold; border: 1px solid #fde68a;">PARA ENTREGAR</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 2px;">
                    <div style="text-align: left;">
                        <span style="font-weight: 600; font-size: 0.9em; color: var(--text-main); display: block;">Projeto de Banco de Dados</span>
                        <span style="font-size: 0.75em; color: var(--text-muted);">Disciplina: Engenharia de Software</span>
                    </div>
                    <span style="background: #def7ec; color: #03543f; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: bold; border: 1px solid #b2f5ea;">NOTA: 8.9</span>
                </div>
            </div>""",
            unsafe_allow_html=True
        )


# ─── Ponto de entrada desta página ──────────────────────────
# O Streamlit executa este arquivo diretamente; chamamos a função principal aqui.
tela_acesso()

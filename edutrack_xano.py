"""
=============================================================
 EduTrack IA 2.0 — Arquivo Principal da Aplicação
=============================================================
 Este é o ponto de entrada (entry point) da aplicação.
 Ele configura o app, gerencia a sessão do usuário e
 controla a navegação entre as páginas.

 Tecnologias usadas:
   - Streamlit: framework Python para criar apps web
   - Xano: backend/API no-code que armazena os dados
=============================================================
"""

# ─── Importações ────────────────────────────────────────────
# Importa o Streamlit, a biblioteca principal da interface web
import streamlit as st

# ============================================================
# 1. CONFIGURAÇÃO GERAL DA APLICAÇÃO
# ============================================================
# Define o título que aparece na aba do navegador e o layout
# 'wide' usa toda a largura da tela (mais espaço para o conteúdo)
st.set_page_config(page_title='EduTrack AI', layout='wide')

# ============================================================
# 2. GERENCIAMENTO DE SESSÃO (Estado do Usuário)
# ============================================================
# st.session_state é um dicionário que persiste informações
# enquanto o usuário estiver navegando na aplicação.
# Aqui verificamos se a chave 'logged_in' já existe na sessão;
# se não existir, inicializamos com False (usuário deslogado).
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def logout():
    """
    Função de logout: limpa todos os dados da sessão do usuário
    (token JWT, nome, etc.) e recarrega a página para voltar
    automaticamente à tela de login.
    """
    st.session_state.clear()  # Apaga todos os dados da sessão
    st.rerun()                 # Recarrega o app do zero

# ============================================================
# 3. REGISTRO DE PÁGINAS (ROTEAMENTO / NAVEGAÇÃO)
# ============================================================
# Cada st.Page mapeia uma URL interna para um arquivo Python.
# O parâmetro 'title' define o nome exibido no menu lateral.
# O parâmetro 'icon' define o emoji que aparece ao lado do nome.

login_page      = st.Page("pages/login.py",         title="Acesso",             icon="🔑")
dashboard_page  = st.Page("pages/dashboard.py",     title="Painel Geral",       icon="📊")
cursos_page     = st.Page("pages/cursos.py",         title="Cursos",             icon="🎓")
professores_page= st.Page("pages/professores.py",   title="Professores",        icon="👨‍🏫")
disciplinas_page= st.Page("pages/disciplinas.py",   title="Disciplinas",        icon="📚")
tarefas_page    = st.Page("pages/tarefas.py",        title="Tarefas/Notas",      icon="📝")
relatorios_page = st.Page("pages/relatorios.py",    title="Relatórios",         icon="📋")
profile_page    = st.Page("pages/profile.py",       title="Meu Perfil",         icon="👤")

# Páginas exclusivas para usuários com papel (role) de Administrador
admin_list_page     = st.Page("pages/admin_list.py",     title="Lista de Usuários",    icon="👥")
admin_manage_page   = st.Page("pages/admin_manage.py",   title="Gerenciar Usuário",    icon="⚙️")
admin_delete_page   = st.Page("pages/admin_delete.py",   title="Excluir Conta",        icon="🗑️")
admin_activity_page = st.Page("pages/admin_activity.py", title="Atividade dos Usuários", icon="📊")

# ============================================================
# 4. CONTROLE DE NAVEGAÇÃO (ROTEADOR CONDICIONAL)
# ============================================================
# A lógica abaixo decide QUAIS páginas o usuário pode acessar.
# Isso é uma forma simples de "proteção de rota":
#   - Usuário NÃO logado → vê apenas a página de Login
#   - Usuário logado     → vê o menu completo
#   - Usuário admin      → vê também as páginas de Administração

if not st.session_state.logged_in:
    # Se não estiver logado, a única página acessível é a de Login
    pg = st.navigation([login_page])
else:
    # Se logado, exibe o menu lateral com botão de sair e libera as páginas internas
    with st.sidebar:
        st.title('EduTrack AI')
        # Botão de logout visível para o usuário no menu lateral
        if st.button('Sair'):
            logout()

    # Dicionário de páginas agrupadas (o nome da chave vira um cabeçalho no menu)
    pages = {
        # Grupo sem título (string vazia) contém as páginas principais
        "": [dashboard_page, cursos_page, professores_page, disciplinas_page, tarefas_page, relatorios_page, profile_page]
    }
    
    # Se o usuário tiver papel de admin, adiciona o grupo de Administração
    if st.session_state.get('user_role') == 'admin':
        pages["Administração"] = [admin_activity_page, admin_list_page, admin_manage_page, admin_delete_page]
        
    # Monta o objeto de navegação com os grupos de páginas
    pg = st.navigation(pages)

# ─── Executa a página atual ─────────────────────────────────
# Este comando inicia o roteador: ele lê a URL atual e
# executa o arquivo Python correspondente à página selecionada.
pg.run()

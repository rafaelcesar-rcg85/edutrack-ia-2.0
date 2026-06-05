import streamlit as st

# ==========================================
# 1. CONFIGURAÇÃO GERAL DA APLICAÇÃO
# ==========================================
st.set_page_config(page_title='EduTrack AI', layout='wide')

# ==========================================
# 2. GERENCIAMENTO DE SESSÃO
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def logout():
    """Limpa a sessão do usuário e recarrega a página para voltar à tela de login."""
    st.session_state.clear()
    st.rerun()

# ==========================================
# 3. REGISTRO DE PÁGINAS (ROTEAMENTO)
# ==========================================
login_page = st.Page("pages/login.py", title="Acesso", icon="🔑")
dashboard_page = st.Page("pages/dashboard.py", title="Painel Geral", icon="📊")
cursos_page = st.Page("pages/cursos.py", title="Cursos", icon="🎓")
professores_page = st.Page("pages/professores.py", title="Professores", icon="👨‍🏫")
disciplinas_page = st.Page("pages/disciplinas.py", title="Disciplinas", icon="📚")
tarefas_page = st.Page("pages/tarefas.py", title="Tarefas/Notas", icon="📝")
relatorios_page = st.Page("pages/relatorios.py", title="Relatórios", icon="📋")
profile_page = st.Page("pages/profile.py", title="Meu Perfil", icon="👤")

# ==========================================
# 4. CONTROLE DE NAVEGAÇÃO
# ==========================================
if not st.session_state.logged_in:
    # Se não estiver logado, a única página acessível é a de Login
    pg = st.navigation([login_page])
else:
    # Se logado, exibe o menu lateral com botão de sair e libera as páginas internas
    with st.sidebar:
        st.title('EduTrack AI')
        if st.button('Sair'):
            logout()
    pg = st.navigation([dashboard_page, cursos_page, professores_page, disciplinas_page, tarefas_page, relatorios_page, profile_page])

# Inicia o roteador de páginas
pg.run()

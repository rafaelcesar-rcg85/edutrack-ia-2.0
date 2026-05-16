import streamlit as st

st.set_page_config(page_title='EduTrack AI', layout='wide')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.session_state.clear()
    st.rerun()

login_page = st.Page("pages/login.py", title="Acesso", icon="🔑")
dashboard_page = st.Page("pages/dashboard.py", title="Painel Geral", icon="📊")
professores_page = st.Page("pages/professores.py", title="Professores", icon="👨‍🏫")
disciplinas_page = st.Page("pages/disciplinas.py", title="Disciplinas", icon="📚")
tarefas_page = st.Page("pages/tarefas.py", title="Tarefas/Notas", icon="📝")

if not st.session_state.logged_in:
    pg = st.navigation([login_page])
else:
    with st.sidebar:
        st.title('EduTrack AI')
        if st.button('Sair'):
            logout()
    pg = st.navigation([dashboard_page, professores_page, disciplinas_page, tarefas_page])

pg.run()

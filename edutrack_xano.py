# ------------------------------------------------
# IMPORTAÇÃO DE BIBLIOTECAS
# ------------------------------------------------

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ------------------------------------------------
# CONFIGURAÇÃO DA API XANO
# ------------------------------------------------

# Substitua pela SUA URL real do grupo de API no Xano
BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:iiiYAbKm'

# ------------------------------------------------
# FUNÇÕES DE CONEXÃO E UTILITÁRIOS
# ------------------------------------------------

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

# ------------------------------------------------
# SISTEMA DE AUTENTICAÇÃO
# ------------------------------------------------

def tela_acesso():
    st.title('Portal Acadêmico Personalizado')
    tab_login, tab_cadastro = st.tabs(['Entrar', 'Criar Minha Conta'])

    with tab_login:
        with st.form('login_form'):
            email = st.text_input('E-mail')
            senha = st.text_input('Senha', type='password')
            if st.form_submit_button('Acessar Meu Painel'):
                res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': senha})
                if res.status_code == 200:
                    st.session_state.auth_token = res.json().get('authToken')
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    try:
                        error_msg = res.json().get('message', 'Credenciais inválidas.')
                    except:
                        error_msg = 'Credenciais inválidas.'
                    st.error(f'Erro no login: {error_msg}')

    with tab_cadastro:
        with st.form('cadastro_form'):
            nome = st.text_input('Nome')
            email_c = st.text_input('E-mail')
            pass_c = st.text_input('Senha', type='password')
            if st.form_submit_button('Cadastrar'):
                res = requests.post(f'{BASE_URL}/auth/signup', json={'name': nome, 'email': email_c, 'password': pass_c})
                if res.status_code == 200:
                    st.success('Conta criada! Agora faça o login.')
                else:
                    try:
                        error_msg = res.json().get('message', 'Erro ao cadastrar usuário.')
                    except:
                        error_msg = 'Erro ao cadastrar usuário.'
                    st.error(f'Erro no cadastro: {error_msg}')

# ------------------------------------------------
# MÓDULOS CRUD PARA PROFESSORES, DISCIPLINAS
# E TAREFAS
# ------------------------------------------------

# GESTÃO DE PROFESSORES

def modulo_professores():
    st.header('‍Meus Professores')
    # [C]REATE
    with st.expander('➕ Adicionar Professor'):
        nome = st.text_input('Nome do Professor')
        email = st.text_input('E-mail de Contato')
        if st.button('Cadastrar Professor'):
            api_post('professores', {'nome': nome, 'email': email})
            st.rerun()

    # [R]EAD & [U]PDATE & [D]ELETE
    dados = api_get('professores')
    if dados:
        df = pd.DataFrame(dados)
        st.subheader('Seus Professores Cadastrados')
        # Editor de dados para facilitar a vida do aluno
        df_editado = st.data_editor(df[['id', 'nome', 'email']], use_container_width=True, hide_index=True, num_rows='dynamic')

        if st.button('Salvar Alterações/Exclusões em Professores'):
            # Para simplificar, atualizamos o que foi alterado
            for _, row in df_editado.iterrows():
                api_patch('professores', row['id'], {'nome': row['nome'], 'email': row['email']})
            st.success('Dados sincronizados!')
            st.rerun()
    else:
        st.info('Nenhum professor cadastrado ainda.')

# GESTÃO DE DISCIPLINAS

def modulo_disciplinas():
    st.header('Minhas Disciplina')
    profs = api_get('professores')
    
    if not profs:
        st.warning('Cadastre um professor antes de criar disciplinas.')
        return

    # [C]REATE
    with st.expander('➕ Nova Disciplina'):
        nome_d = st.text_input('Nome da Matéria')
        opcoes_p = {p['nome']: p['id'] for p in profs}
        p_escolhido = st.selectbox('Professor Responsável', options=list(opcoes_p.keys()))
        if st.button('Salvar Disciplina'):
            api_post('disciplinas', {'nome': nome_d, 'prof_id': opcoes_p[p_escolhido]})
            st.rerun()

    # [R]EAD
    discs = api_get('disciplinas')
    if discs:
        df_d = pd.DataFrame(discs)
        df_p = pd.DataFrame(profs)
        # Junta os nomes para exibição
        df_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'))
        st.dataframe(df_view[['id', 'nome', 'nome_prof']], use_container_width=True, hide_index=True)      

        # [D]ELETE
        id_del = st.number_input('ID para remover', min_value=1, step=1)
        if st.button('Remover Disciplina', type='primary'):
            api_delete('disciplinas', id_del)
            st.rerun()

# GESTÃO DE TAREFAS ---

def modulo_tarefas():
    st.header('Minhas Tarefas e Notas')
    discs = api_get('disciplinas')

    if not discs:
        st.warning('Cadastre uma disciplina primeiro.')
        return

    # [C]REATE
    with st.expander('➕ Lançar Atividade/Nota'):
        nome_t = st.text_input('Nome da Atividade')
        opcoes_d = {d['nome']: d['id'] for d in discs}
        d_escolhida = st.selectbox('Selecione a Disciplina', options=list(opcoes_d.keys()))
        nota = st.number_input('Nota Obtida', 0.0, 10.0, 0.0)
        if st.button('Registrar Nota'):
            api_post('tarefas', {'nome': nome_t, 'disc_id': opcoes_d[d_escolhida], 'nota': nota})
            st.rerun()
            
    # [R]EAD
    tarefas = api_get('tarefas')
    if tarefas:
        df_t = pd.DataFrame(tarefas)
        st.subheader('Quadro de Notas')
        st.dataframe(df_t[['id', 'nome', 'nota']], use_container_width=True, hide_index=True)

        # [D]ELETE
        id_del_t = st.number_input('ID da Tarefa para remover', min_value=1, step=1)
        if st.button('Remover Tarefa'):
            api_delete('tarefas', id_del_t)
            st.rerun()

# --- DASHBOARD ---

def modulo_dashboard():
    st.header('Resumo de Desempenho')
    tarefas = api_get('tarefas')
    discs = api_get('disciplinas')
    if not tarefas or not discs:
        st.info('Cadastre dados para visualizar seu desempenho gráfico.')
        return

    df_t = pd.DataFrame(tarefas)
    df_d = pd.DataFrame(discs)
    df_plot = df_t.merge(df_d, left_on='disc_id', right_on='id', suffixes=('_t', '_d'))
    fig = px.bar(df_plot, x='nome_t', y='nota', color='nome_d', 
                 title='Minhas Notas por Matéria', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# ESTRUTURA PRINCIPAL DE NAVEGAÇÃO
# ------------------------------------------

st.set_page_config(page_title='EduTrack AI', layout='wide')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tela_acesso()
else:
    with st.sidebar:
        st.title('EduTrack AI')
        menu = st.radio('Gerenciar:', ['Painel Geral', 'Professores', 'Disciplinas', 'Tarefas/Notas'])
        st.markdown('---')
        if st.button('Sair'):
            st.session_state.clear()
            st.rerun()

    match menu:
        case 'Painel Geral': modulo_dashboard()
        case 'Professores': modulo_professores()
        case 'Disciplinas': modulo_disciplinas()
        case 'Tarefas/Notas': modulo_tarefas()

import streamlit as st
import pandas as pd
from utils.api import api_post, api_get, api_patch

def modulo_professores():
    st.header('👨‍🏫 Meus Professores')
    
    course_id = st.session_state.get('active_course_id')
    if not course_id:
        st.warning("Selecione ou crie um curso no menu lateral para gerenciar os professores.")
        return
    # [C]REATE
    with st.expander('➕ Adicionar Professor'):
        nome = st.text_input('Nome do Professor')
        email = st.text_input('E-mail de Contato')
        
        cursos = api_get('courses')
        opcoes_cursos = {c['name']: c['id'] for c in cursos} if cursos else {}
        curso_idx = list(opcoes_cursos.values()).index(course_id) if course_id in opcoes_cursos.values() else 0
        curso_selecionado = st.selectbox('Curso', options=list(opcoes_cursos.keys()), index=curso_idx)
        
        if st.button('Cadastrar Professor'):
            selected_course_id = opcoes_cursos[curso_selecionado] if curso_selecionado else course_id
            dados_prof = {'nome': nome, 'email': email, 'course_id': selected_course_id}
            if 'user_id' in st.session_state:
                dados_prof['user_id'] = st.session_state.user_id
            api_post('professores', dados_prof)
            st.rerun()

    # [R]EAD & [U]PDATE & [D]ELETE
    dados = api_get('professores', params={'course_id': course_id})
    if dados:
        df = pd.DataFrame(dados)
        st.subheader('Seus Professores Cadastrados')
        df['curso'] = st.session_state.get('active_course_name', '')
        # Editor de dados para facilitar a vida do aluno
        df_editado = st.data_editor(df[['id', 'nome', 'email', 'curso']], use_container_width=True, hide_index=True, num_rows='dynamic', disabled=['curso', 'id'])

        if st.button('Salvar Alterações/Exclusões em Professores'):
            # Para simplificar, atualizamos o que foi alterado
            for _, row in df_editado.iterrows():
                payload = {'nome': row['nome'], 'email': row['email']}
                if 'user_id' in st.session_state:
                    payload['user_id'] = st.session_state.user_id
                api_patch('professores', row['id'], payload)
            st.success('Dados sincronizados!')
            st.rerun()
    else:
        st.info('Nenhum professor cadastrado ainda.')

modulo_professores()

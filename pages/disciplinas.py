import streamlit as st
import pandas as pd
from utils.api import api_get, api_post, api_delete

def modulo_disciplinas():
    st.header('📚 Minhas Disciplinas')
    
    course_id = st.session_state.get('active_course_id')
    if not course_id:
        st.warning("Selecione ou crie um curso no menu lateral para gerenciar as disciplinas.")
        return

    profs = api_get('professores', params={'course_id': course_id})
    
    if not profs:
        st.warning('Cadastre um professor antes de criar disciplinas.')
        return

    # [C]REATE
    with st.expander('➕ Nova Disciplina'):
        nome_d = st.text_input('Nome da Matéria')
        
        cursos = api_get('courses')
        opcoes_cursos = {c['name']: c['id'] for c in cursos} if cursos else {}
        curso_idx = list(opcoes_cursos.values()).index(course_id) if course_id in opcoes_cursos.values() else 0
        curso_selecionado = st.selectbox('Curso', options=list(opcoes_cursos.keys()), index=curso_idx)
        
        opcoes_p = {p['nome']: p['id'] for p in profs}
        p_escolhido = st.selectbox('Professor Responsável', options=list(opcoes_p.keys()))
        if st.button('Salvar Disciplina'):
            selected_course_id = opcoes_cursos[curso_selecionado] if curso_selecionado else course_id
            dados_disc = {'nome': nome_d, 'prof_id': opcoes_p[p_escolhido], 'course_id': selected_course_id}
            if 'user_id' in st.session_state:
                dados_disc['user_id'] = st.session_state.user_id
            api_post('disciplinas', dados_disc)
            st.rerun()

    # [R]EAD
    discs = api_get('disciplinas', params={'course_id': course_id})
    if discs:
        df_d = pd.DataFrame(discs)
        df_p = pd.DataFrame(profs)
        # Junta os nomes para exibição
        df_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'))
        df_view['curso'] = st.session_state.get('active_course_name', '')
        st.dataframe(df_view[['id', 'nome', 'nome_prof', 'curso']], use_container_width=True, hide_index=True)      

        # [D]ELETE
        id_del = st.number_input('ID para remover', min_value=1, step=1)
        if st.button('Remover Disciplina', type='primary'):
            api_delete('disciplinas', id_del)
            st.rerun()

modulo_disciplinas()

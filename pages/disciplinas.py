import streamlit as st
import pandas as pd
from utils.api import api_get, api_post, api_delete

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

modulo_disciplinas()

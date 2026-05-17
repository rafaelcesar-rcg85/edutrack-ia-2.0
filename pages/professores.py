import streamlit as st
import pandas as pd
from utils.api import api_post, api_get, api_patch

def modulo_professores():
    st.header('‍Meus Professores')
    # [C]REATE
    with st.expander('➕ Adicionar Professor'):
        nome = st.text_input('Nome do Professor')
        email = st.text_input('E-mail de Contato')
        if st.button('Cadastrar Professor'):
            dados_prof = {'nome': nome, 'email': email}
            if 'user_id' in st.session_state:
                dados_prof['user_id'] = st.session_state.user_id
            api_post('professores', dados_prof)
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

modulo_professores()

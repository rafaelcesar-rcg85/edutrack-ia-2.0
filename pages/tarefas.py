import streamlit as st
import pandas as pd
from utils.api import api_get, api_post, api_delete

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

modulo_tarefas()

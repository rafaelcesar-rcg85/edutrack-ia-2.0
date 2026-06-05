import streamlit as st
import pandas as pd
from utils.api import api_get, api_post, api_patch, api_delete

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
            dados_disc = {'nome': nome_d, 'prof_id': opcoes_p[p_escolhido]}
            if 'user_id' in st.session_state:
                dados_disc['user_id'] = st.session_state.user_id
            api_post('disciplinas', dados_disc)
            st.rerun()

    # [U]PDATE
    discs = api_get('disciplinas')
    if discs:
        with st.expander('✏️ Alterar Disciplina'):
            opcoes_d = {f"{d['nome']} (ID: {d['id']})": d for d in discs}
            d_escolhida_str = st.selectbox('Selecione a Disciplina para Alterar', options=[""] + list(opcoes_d.keys()))
            
            if d_escolhida_str:
                d_atual = opcoes_d[d_escolhida_str]
                def_nome = d_atual.get('nome', '')
                def_prof_id = d_atual.get('prof_id')
                
                # Mapeamento reverso de professores
                p_inverso = {p['id']: p['nome'] for p in profs}
                def_prof_nome = p_inverso.get(def_prof_id) if def_prof_id in p_inverso else list(opcoes_p.keys())[0]
                
                with st.form(f"form_edit_disc_{d_atual['id']}"):
                    novo_nome = st.text_input('Nome da Matéria', value=def_nome)
                    index_prof = list(opcoes_p.keys()).index(def_prof_nome) if def_prof_nome in opcoes_p else 0
                    novo_prof = st.selectbox('Professor Responsável ', options=list(opcoes_p.keys()), index=index_prof)
                    
                    if st.form_submit_button('Atualizar Disciplina'):
                        dados_update = {
                            'nome': novo_nome,
                            'prof_id': opcoes_p[novo_prof]
                        }
                        res_patch = api_patch('disciplinas', d_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Disciplina atualizada com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")

    # [R]EAD
    discs = api_get('disciplinas')
    if discs:
        df_d = pd.DataFrame(discs)
        df_p = pd.DataFrame(profs)
        # Junta os nomes para exibição
        df_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'))
        
        # Renomear colunas para exibição
        df_display = df_view[['id', 'nome', 'nome_prof']].rename(columns={
            'id': 'ID',
            'nome': 'Nome',
            'nome_prof': 'Professor'
        })
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)      

        # [D]ELETE
        id_del = st.number_input('ID para remover', min_value=1, step=1)
        if st.button('Remover Disciplina', type='primary'):
            api_delete('disciplinas', id_del)
            st.rerun()

modulo_disciplinas()

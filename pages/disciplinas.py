import streamlit as st
import pandas as pd
from utils.api import api_get, api_post, api_patch, api_delete
@st.dialog("Confirmar Exclusão")
def confirm_delete_disc(disc_id):
    st.error("Tem certeza que deseja excluir esta disciplina? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Voltar / Cancelar', use_container_width=True):
            st.rerun()
    with col2:
        if st.button('Confirmar Exclusão', type='primary', use_container_width=True):
            res_del = api_delete('disciplinas', disc_id)
            if res_del.status_code == 200:
                st.success("Disciplina removida com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res_del.text}")

def modulo_disciplinas():
    st.header('Minhas Disciplina')
    profs = api_get('professores')
    cursos = api_get('curso')
    
    if not profs or not cursos:
        st.warning('Cadastre ao menos um professor e um curso antes de criar disciplinas.')
        return

    # [C]REATE
    with st.expander('➕ Nova Disciplina'):
        nome_d = st.text_input('Nome da Matéria')
        opcoes_p = {p['nome']: p['id'] for p in profs}
        p_escolhido = st.selectbox('Professor Responsável', options=list(opcoes_p.keys()))
        
        opcoes_c = {c.get('curso', c.get('name', 'Sem Nome')): c['id'] for c in cursos}
        c_escolhido = st.selectbox('Curso Pertencente', options=list(opcoes_c.keys()))
        
        if st.button('Salvar Disciplina'):
            dados_disc = {
                'nome': nome_d, 
                'prof_id': opcoes_p[p_escolhido],
                'curso_id': opcoes_c[c_escolhido]
            }
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
                def_curso_id = d_atual.get('curso_id')
                
                # Mapeamento reverso de professores e cursos
                p_inverso = {p['id']: p['nome'] for p in profs}
                def_prof_nome = p_inverso.get(def_prof_id) if def_prof_id in p_inverso else list(opcoes_p.keys())[0]
                
                opcoes_c = {c.get('curso', c.get('name', 'Sem Nome')): c['id'] for c in cursos}
                c_inverso = {c['id']: c.get('curso', c.get('name', 'Sem Nome')) for c in cursos}
                def_curso_nome = c_inverso.get(def_curso_id) if def_curso_id in c_inverso else list(opcoes_c.keys())[0]
                
                with st.form(f"form_edit_disc_{d_atual['id']}"):
                    novo_nome = st.text_input('Nome da Matéria', value=def_nome)
                    index_prof = list(opcoes_p.keys()).index(def_prof_nome) if def_prof_nome in opcoes_p else 0
                    novo_prof = st.selectbox('Professor Responsável ', options=list(opcoes_p.keys()), index=index_prof)
                    
                    index_curso = list(opcoes_c.keys()).index(def_curso_nome) if def_curso_nome in opcoes_c else 0
                    novo_curso = st.selectbox('Curso Pertencente', options=list(opcoes_c.keys()), index=index_curso)
                    
                    if st.form_submit_button('Atualizar Disciplina'):
                        dados_update = {
                            'nome': novo_nome,
                            'prof_id': opcoes_p[novo_prof],
                            'curso_id': opcoes_c[novo_curso]
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                        res_patch = api_patch('disciplinas', d_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Disciplina atualizada com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
                
                st.markdown("---")
                if st.button('🗑️ Remover Disciplina', type='primary', use_container_width=True):
                    confirm_delete_disc(d_atual['id'])

    # [R]EAD
    discs = api_get('disciplinas')
    if discs:
        df_d = pd.DataFrame(discs)
        df_p = pd.DataFrame(profs)
        df_c = pd.DataFrame(cursos)
        
        # Junta os nomes para exibição
        df_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'), how='left')
        
        if not df_c.empty:
            df_c['nome_curso'] = df_c.apply(lambda row: row.get('curso', row.get('name', 'Sem Nome')), axis=1)
            df_view = df_view.merge(df_c[['id', 'nome_curso']], left_on='curso_id', right_on='id', suffixes=('', '_curso'), how='left')
        else:
            df_view['nome_curso'] = 'N/A'
        
        # Renomear colunas para exibição
        cols_to_show = ['id', 'nome', 'nome_prof', 'nome_curso']
        cols_to_show = [c for c in cols_to_show if c in df_view.columns]
        
        df_display = df_view[cols_to_show].rename(columns={
            'id': 'ID',
            'nome': 'Nome',
            'nome_prof': 'Professor',
            'nome_curso': 'Curso'
        })
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)      



modulo_disciplinas()

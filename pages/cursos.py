import streamlit as st
import pandas as pd
import datetime
from utils.api import api_post, api_get, api_patch, api_delete
@st.dialog("Confirmar Exclusão")
def confirm_delete_curso(curso_id):
    st.error("Tem certeza que deseja excluir este curso? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Voltar / Cancelar', use_container_width=True):
            st.rerun()
    with col2:
        if st.button('Confirmar Exclusão', type='primary', use_container_width=True):
            res_del = api_delete('curso', curso_id)
            if res_del.status_code == 200:
                st.success("Curso removido com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res_del.text}")

def modulo_cursos():
    st.header('Meus Cursos')
    
    # [C]REATE
    with st.expander('➕ Adicionar Curso'):
        nome = st.text_input('Nome do Curso / Instituição')
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input('Data de Início', key='create_data_inicio')
        with col2:
            data_fim = st.date_input('Data de Fim', key='create_data_fim')
        
        if st.button('Cadastrar Curso'):
            if nome:
                dados_curso = {
                    'name': nome,
                    'curso': nome, 
                    'data_inicio': data_inicio.isoformat() if data_inicio else None, 
                    'data_fim': data_fim.isoformat() if data_fim else None
                }
                if 'user_id' in st.session_state:
                    dados_curso['user_id'] = st.session_state.user_id
                api_post('curso', dados_curso)
                st.success("Curso cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("Por favor, insira o nome do curso.")

    cursos = api_get('curso')
    
    # [U]PDATE
    if cursos:
        with st.expander('✏️ Alterar Curso'):
            opcoes_c = {f"{c.get('curso', c.get('name', 'Sem Nome'))} (ID: {c['id']})": c for c in cursos}
            c_escolhido_str = st.selectbox('Selecione o Curso para Alterar', options=[""] + list(opcoes_c.keys()))
            
            if c_escolhido_str:
                c_atual = opcoes_c[c_escolhido_str]
                def_nome = c_atual.get('curso', c_atual.get('name', ''))
                
                # Conversão segura de datas para o st.date_input
                try:
                    def_data_inicio = datetime.date.fromisoformat(str(c_atual.get('data_inicio'))[:10]) if c_atual.get('data_inicio') else datetime.date.today()
                except Exception:
                    def_data_inicio = datetime.date.today()
                try:
                    def_data_fim = datetime.date.fromisoformat(str(c_atual.get('data_fim'))[:10]) if c_atual.get('data_fim') else datetime.date.today()
                except Exception:
                    def_data_fim = datetime.date.today()
                
                with st.form(f"form_edit_curso_{c_atual['id']}"):
                    novo_nome = st.text_input('Nome do Curso', value=def_nome)
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_data_inicio = st.date_input('Data de Início', value=def_data_inicio)
                    with col2:
                        novo_data_fim = st.date_input('Data de Fim', value=def_data_fim)
                    
                    if st.form_submit_button('Atualizar Curso'):
                        dados_update = {
                            'name': novo_nome,
                            'curso': novo_nome,
                            'data_inicio': novo_data_inicio.isoformat() if novo_data_inicio else None,
                            'data_fim': novo_data_fim.isoformat() if novo_data_fim else None
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                        res_patch = api_patch('curso', c_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Curso atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
                
                st.markdown("---")
                if st.button('🗑️ Remover Curso', type='primary', use_container_width=True):
                    confirm_delete_curso(c_atual['id'])

    # [R]EAD
    if cursos:
        df = pd.DataFrame(cursos)
        st.subheader('Seus Cursos Cadastrados')
        
        # Renomear colunas para exibição
        cols_to_show = ['id', 'curso', 'name', 'data_inicio', 'data_fim']
        cols_to_show = [c for c in cols_to_show if c in df.columns]
        
        rename_map = {
            'id': 'ID',
            'curso': 'Nome do Curso',
            'name': 'Nome do Curso',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim'
        }
        df_display = df[cols_to_show].rename(columns=rename_map)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        

    else:
        st.info('Nenhum curso cadastrado ainda.')

modulo_cursos()

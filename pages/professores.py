import streamlit as st
import pandas as pd
from utils.api import api_post, api_get, api_patch, api_delete
from utils.theme import apply_theme
@st.dialog("Confirmar Exclusão")
def confirm_delete_prof(prof_id):
    st.error("Tem certeza que deseja excluir este professor? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Voltar / Cancelar', use_container_width=True):
            st.rerun()
    with col2:
        if st.button('Confirmar Exclusão', type='primary', use_container_width=True):
            res_del = api_delete('professores', prof_id)
            if res_del.status_code == 200:
                st.success("Professor removido com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res_del.text}")

def modulo_professores():
    apply_theme()
    st.header('Meus Professores')
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

    professores = api_get('professores')
    
    # [U]PDATE
    if professores:
        with st.expander('✏️ Alterar Professor'):
            opcoes_p = {f"{p['nome']} (ID: {p['id']})": p for p in professores}
            p_escolhido_str = st.selectbox('Selecione o Professor para Alterar', options=[""] + list(opcoes_p.keys()))
            
            if p_escolhido_str:
                p_atual = opcoes_p[p_escolhido_str]
                def_nome = p_atual.get('nome', '')
                def_email = p_atual.get('email', '')
                
                with st.form(f"form_edit_prof_{p_atual['id']}"):
                    novo_nome = st.text_input('Nome do Professor', value=def_nome)
                    novo_email = st.text_input('E-mail de Contato', value=def_email)
                    
                    if st.form_submit_button('Atualizar Professor'):
                        dados_update = {
                            'nome': novo_nome,
                            'email': novo_email
                        }
                        res_patch = api_patch('professores', p_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Professor atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
                
                st.markdown("---")
                if st.button('🗑️ Remover Professor', type='primary', use_container_width=True):
                    confirm_delete_prof(p_atual['id'])

    # [R]EAD
    if professores:
        df = pd.DataFrame(professores)
        st.subheader('Seus Professores Cadastrados')
        
        # Renomear colunas para exibição
        cols_to_show = ['id', 'nome', 'email']
        cols_to_show = [c for c in cols_to_show if c in df.columns]
        
        rename_map = {
            'id': 'ID',
            'nome': 'Nome',
            'email': 'E-mail'
        }
        df_display = df[cols_to_show].rename(columns=rename_map)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        

    else:
        st.info('Nenhum professor cadastrado ainda.')

modulo_professores()

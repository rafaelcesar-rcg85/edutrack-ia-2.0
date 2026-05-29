import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import api_post, api_get, api_patch, api_delete

def modulo_cursos():
    st.header('🏫 Meus Cursos / Instituições')
    
    st.write("Crie diferentes cursos para manter suas disciplinas e tarefas separadas e organizadas.")

    # [C]REATE
    with st.expander('➕ Adicionar Novo Curso', expanded=True):
        nome = st.text_input('Nome do Curso/Instituição')
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input('Data de Início', format="DD/MM/YYYY")
        with col2:
            data_fim = st.date_input('Data de Término', format="DD/MM/YYYY")
            
        if st.button('Cadastrar Curso'):
            if nome:
                dados_curso = {
                    'name': nome,
                    'data_inicio': data_inicio.isoformat() if data_inicio else None,
                    'data_fim': data_fim.isoformat() if data_fim else None
                }
                if 'user_id' in st.session_state:
                    dados_curso['user_id'] = st.session_state.user_id
                res = api_post('courses', dados_curso)
                if hasattr(res, 'status_code') and res.status_code in [200, 201]:
                    st.success("Curso cadastrado com sucesso!")
                    st.rerun()
                else:
                    try:
                        msg = res.json().get('message', res.text)
                    except:
                        msg = res.text if hasattr(res, 'text') else "Erro desconhecido"
                    st.error(f"Erro ao salvar no Xano: {msg} (Status: {getattr(res, 'status_code', 'N/A')})")

    # [R]EAD & [U]PDATE
    dados = api_get('courses')
    if dados:
        df = pd.DataFrame(dados)
        
        # Garante a existência das colunas para evitar erros de renderização
        if 'data_inicio' not in df.columns:
            df['data_inicio'] = None
        if 'data_fim' not in df.columns:
            df['data_fim'] = None

        st.subheader('Cursos Cadastrados')
        
        # Formata datas para exibição na tabela
        def formatar_data(d):
            if not d or pd.isna(d):
                return "Não informada"
            try:
                return datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
            except:
                return str(d)
        
        df_exibicao = df.copy()
        df_exibicao['Início'] = df_exibicao['data_inicio'].apply(formatar_data)
        df_exibicao['Término'] = df_exibicao['data_fim'].apply(formatar_data)
        df_exibicao = df_exibicao.rename(columns={'name': 'Curso/Instituição'})
        
        st.dataframe(
            df_exibicao[['id', 'Curso/Instituição', 'Início', 'Término']], 
            use_container_width=True, 
            hide_index=True
        )

        # [U]PDATE (Edição por formulário)
        with st.expander('✏️ Alterar Curso'):
            opcoes_c = {f"{c['name']} (ID: {c['id']})": c for c in dados}
            c_escolhido_str = st.selectbox('Selecione o Curso para Alterar', options=[""] + list(opcoes_c.keys()))
            
            if c_escolhido_str:
                c_atual = opcoes_c[c_escolhido_str]
                
                def_nome = c_atual.get('name', '')
                
                # Trata data de início padrão
                def_data_ini = datetime.today().date()
                if c_atual.get('data_inicio'):
                    try:
                        def_data_ini = datetime.fromisoformat(str(c_atual['data_inicio']).split('T')[0]).date()
                    except:
                        pass
                
                # Trata data de término padrão
                def_data_fim = datetime.today().date()
                if c_atual.get('data_fim'):
                    try:
                        def_data_fim = datetime.fromisoformat(str(c_atual['data_fim']).split('T')[0]).date()
                    except:
                        pass
                
                with st.form(f"form_edit_curso_{c_atual['id']}"):
                    novo_nome = st.text_input('Nome do Curso/Instituição', value=def_nome)
                    col1_ed, col2_ed = st.columns(2)
                    with col1_ed:
                        nova_data_ini = st.date_input('Data de Início', value=def_data_ini, format="DD/MM/YYYY")
                    with col2_ed:
                        nova_data_fim = st.date_input('Data de Término', value=def_data_fim, format="DD/MM/YYYY")
                    
                    submitted = st.form_submit_button('Atualizar Curso')
                    if submitted:
                        dados_update = {
                            'name': novo_nome,
                            'data_inicio': nova_data_ini.isoformat() if nova_data_ini else None,
                            'data_fim': nova_data_fim.isoformat() if nova_data_fim else None
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                            
                        res_patch = api_patch('courses', c_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Curso atualizado!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
            
        st.divider()
        # [D]ELETE
        id_del = st.number_input('ID para remover', min_value=1, step=1, key='del_curso')
        if st.button('Remover Curso', type='primary'):
            api_delete('courses', id_del)
            st.rerun()
    else:
        st.info('Você ainda não cadastrou nenhum curso. Crie um acima para começar a organizar sua vida acadêmica!')

modulo_cursos()


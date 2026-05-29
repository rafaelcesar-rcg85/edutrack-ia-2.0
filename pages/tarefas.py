import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import api_get, api_post, api_patch, api_delete

def modulo_tarefas():
    st.header('📝 Minhas Tarefas e Notas')
    
    course_id = st.session_state.get('active_course_id')
    if not course_id:
        st.warning("Selecione ou crie um curso no menu lateral para gerenciar as tarefas.")
        return

    discs = api_get('disciplinas', params={'course_id': course_id})
    tarefas_gerais = api_get('tarefas')
    
    # Filtra as tarefas para mostrar apenas as que pertencem às disciplinas deste curso
    tarefas = []
    if tarefas_gerais and discs:
        valid_disc_ids = [d['id'] for d in discs]
        tarefas = [t for t in tarefas_gerais if t.get('disc_id') in valid_disc_ids]

    if not discs:
        st.warning('Cadastre uma disciplina primeiro.')
        return

    # Mapeamentos para dropdowns
    opcoes_d = {d['nome']: d['id'] for d in discs}
    d_inverso = {d['id']: d['nome'] for d in discs}

    # [C]REATE
    with st.expander('➕ Lançar Atividade/Nota'):
        nome_t = st.text_input('Nome da Atividade')
        d_escolhida = st.selectbox('Selecione a Disciplina', options=list(opcoes_d.keys()))
        
        status = st.selectbox('Status', options=['Concluída', 'Para Entregar'])
        data_entrega = None
        if status == 'Para Entregar':
            data_entrega = st.date_input('Data de Entrega', format="DD/MM/YYYY")
            
        nota = st.number_input('Nota Obtida', 0.0, 10.0, 0.0)
        
        if st.button('Registrar Atividade'):
            dados = {
                'nome': nome_t, 
                'disc_id': opcoes_d[d_escolhida], 
                'status': status
            }
            if 'user_id' in st.session_state:
                dados['user_id'] = st.session_state.user_id
            if status == 'Concluída':
                dados['nota'] = nota
                
            if status == 'Para Entregar' and data_entrega:
                dados['data_entrega'] = data_entrega.isoformat()
                
            res = api_post('tarefas', dados)
            if res.status_code in [200, 201]:
                st.success("Atividade registrada!")
                st.rerun()
            else:
                st.error(f"Erro ao salvar: {res.text}")

    # [U]PDATE
    if tarefas:
        with st.expander('✏️ Alterar Atividade/Nota'):
            opcoes_t = {f"{t['nome']} (ID: {t['id']})": t for t in tarefas}
            t_escolhida_str = st.selectbox('Selecione a Atividade para Alterar', options=[""] + list(opcoes_t.keys()))
            
            if t_escolhida_str:
                t_atual = opcoes_t[t_escolhida_str]
                
                def_nome = t_atual.get('nome', '')
                def_disc_id = t_atual.get('disc_id')
                def_disc_nome = d_inverso.get(def_disc_id) if def_disc_id in d_inverso else list(opcoes_d.keys())[0]
                def_status = t_atual.get('status', 'Concluída')
                def_nota = float(t_atual.get('nota', 0.0)) if t_atual.get('nota') is not None else 0.0
                
                def_data = datetime.today()
                if def_status == 'Para Entregar' and t_atual.get('data_entrega'):
                    try:
                        def_data = datetime.fromisoformat(str(t_atual['data_entrega']).split('T')[0]).date()
                    except:
                        pass
                
                with st.form(f"form_edit_{t_atual['id']}"):
                    novo_nome = st.text_input('Nome da Atividade', value=def_nome)
                    index_disc = list(opcoes_d.keys()).index(def_disc_nome) if def_disc_nome in opcoes_d else 0
                    nova_disc = st.selectbox('Disciplina', options=list(opcoes_d.keys()), index=index_disc)
                    
                    index_status = 1 if def_status == 'Para Entregar' else 0
                    novo_status = st.selectbox('Status', options=['Concluída', 'Para Entregar'], index=index_status)
                    
                    nova_data = st.date_input('Data de Entrega', value=def_data, format="DD/MM/YYYY")
                    nova_nota = st.number_input('Nota Obtida', 0.0, 10.0, def_nota)
                    
                    submitted = st.form_submit_button('Atualizar Atividade')
                    if submitted:
                        dados_update = {
                            'nome': novo_nome,
                            'disc_id': opcoes_d[nova_disc],
                            'status': novo_status
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                            
                        if novo_status == 'Concluída':
                            dados_update['nota'] = nova_nota
                        elif novo_status == 'Para Entregar':
                            dados_update['data_entrega'] = nova_data.isoformat()
                            
                        res_patch = api_patch('tarefas', t_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Atividade atualizada!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")

    # [R]EAD
    if tarefas:
        df_t = pd.DataFrame(tarefas)
        st.subheader('Quadro de Atividades e Notas')
        
        if 'status' not in df_t.columns:
            df_t['status'] = 'Concluída'
        if 'data_entrega' not in df_t.columns:
            df_t['data_entrega'] = None
        else:
            def format_date(d):
                if not d or pd.isna(d): return ""
                try:
                    return datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
                except:
                    return str(d)
            df_t['data_entrega'] = df_t['data_entrega'].apply(format_date)
            
        cols_to_show = ['id', 'nome', 'status', 'data_entrega', 'nota']
        cols_to_show = [c for c in cols_to_show if c in df_t.columns]
        
        st.dataframe(df_t[cols_to_show], use_container_width=True, hide_index=True)

        # [D]ELETE
        id_del_t = st.number_input('ID da Tarefa para remover', min_value=1, step=1)
        if st.button('Remover Tarefa'):
            res_del = api_delete('tarefas', id_del_t)
            if res_del.status_code == 200:
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res_del.text}")

modulo_tarefas()

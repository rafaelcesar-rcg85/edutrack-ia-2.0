"""
=============================================================
 pages/tarefas.py — Módulo de Tarefas e Notas
=============================================================
 Implementa o CRUD completo de Tarefas/Notas:
   [C]reate — Lançar nova atividade/nota
   [R]ead   — Visualizar quadro de atividades
   [U]pdate — Alterar dados de uma atividade
   [D]elete — Remover uma atividade

 As tarefas são o nível mais baixo da hierarquia:
   Curso → Disciplinas → Tarefas/Notas

 Cada tarefa tem dois modos:
   - "Concluída"     → exige nota (0 a 10)
   - "Para Entregar" → exige data de entrega
=============================================================
"""

# ─── Importações ────────────────────────────────────────────
import streamlit as st    # Interface web
import pandas as pd       # Manipulação de dados em tabela
from datetime import datetime  # Tratamento de datas
from utils.api import api_get, api_post, api_patch, api_delete  # Funções CRUD da API
from utils.theme import apply_theme  # Sistema de temas visuais


# ============================================================
# DIÁLOGO DE CONFIRMAÇÃO DE EXCLUSÃO
# ============================================================
@st.dialog("Confirmar Exclusão")
def confirm_delete_tarefa(tarefa_id):
    """
    Modal de confirmação antes de excluir uma tarefa.
    
    @st.dialog transforma esta função em um pop-up modal,
    impedindo exclusões acidentais por um clique errado.
    """
    st.error("Tem certeza que deseja excluir esta tarefa? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Voltar / Cancelar', use_container_width=True):
            st.rerun()  # Fecha o modal sem deletar
    with col2:
        if st.button('Confirmar Exclusão', type='primary', use_container_width=True):
            # Chama DELETE na API passando o ID da tarefa
            res_del = api_delete('tarefas', tarefa_id)
            if res_del.status_code == 200:
                st.success("Tarefa removida com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res_del.text}")


# ============================================================
# MÓDULO PRINCIPAL DE TAREFAS
# ============================================================
def modulo_tarefas():
    """
    Função principal que monta toda a interface da página de Tarefas.
    Carrega disciplinas e cursos para montar os seletores,
    depois executa o fluxo CRUD.
    """
    apply_theme()
    st.header('Minhas Tarefas e Notas')
    
    # Carrega os dados necessários para montar os seletores (dropdowns)
    discs   = api_get('disciplinas')  # Lista de disciplinas do usuário
    cursos  = api_get('curso')        # Lista de cursos do usuário
    tarefas = api_get('tarefas')      # Lista de tarefas do usuário

    # Pré-condição: não é possível criar tarefas sem ter disciplinas e cursos
    if not discs or not cursos:
        st.warning('Cadastre uma disciplina e um curso primeiro.')
        return  # Interrompe a execução da página

    # ── Mapeamentos para os Dropdowns ────────────────────────
    # Dicionários que mapeiam nome → id e id → nome
    # Usados para exibir nomes amigáveis e enviar IDs para a API

    # Disciplinas: {nome: id}
    opcoes_d = {d['nome']: d['id'] for d in discs}
    # Disciplinas invertido: {id: nome} — para exibir o nome atual na edição
    d_inverso = {d['id']: d['nome'] for d in discs}
    
    # Cursos: {nome: id}
    opcoes_c = {c.get('curso', c.get('name', 'Sem Nome')): c['id'] for c in cursos}
    # Cursos invertido: {id: nome}
    c_inverso = {c['id']: c.get('curso', c.get('name', 'Sem Nome')) for c in cursos}

    # ── [C]REATE — Lançar Nova Atividade/Nota ────────────────
    with st.expander('➕ Lançar Atividade/Nota'):
        nome_t     = st.text_input('Nome da Atividade')
        d_escolhida = st.selectbox('Selecione a Disciplina', options=list(opcoes_d.keys()))
        c_escolhido = st.selectbox('Curso Pertencente',      options=list(opcoes_c.keys()))
        
        # O status determina quais campos adicionais são exibidos
        status = st.selectbox('Status', options=['Concluída', 'Para Entregar'])
        
        data_entrega = None
        if status == 'Para Entregar':
            # Só exibe o campo de data se a tarefa ainda não foi concluída
            data_entrega = st.date_input('Data de Entrega', format="DD/MM/YYYY")
            
        # Campo de nota só faz sentido para tarefas concluídas
        nota = st.number_input('Nota Obtida', 0.0, 10.0, 0.0)
        
        if st.button('Registrar Atividade'):
            # Monta o payload com os campos obrigatórios
            dados = {
                'nome'    : nome_t,
                'disc_id' : opcoes_d[d_escolhida],  # Converte nome → ID da disciplina
                'curso_id': opcoes_c[c_escolhido],  # Converte nome → ID do curso
                'status'  : status
            }
            # Vincula a tarefa ao usuário logado
            if 'user_id' in st.session_state:
                dados['user_id'] = st.session_state.user_id
                
            # Adiciona campos opcionais conforme o status escolhido
            if status == 'Concluída':
                dados['nota'] = nota
                
            if status == 'Para Entregar' and data_entrega:
                dados['data_entrega'] = data_entrega.isoformat()  # Converte data para string
                
            # Envia o POST para criar a tarefa no Xano
            res = api_post('tarefas', dados)
            if res.status_code in [200, 201]:
                st.success("Atividade registrada!")
                st.rerun()
            else:
                st.error(f"Erro ao salvar: {res.text}")

    # ── [U]PDATE — Alterar Atividade Existente ───────────────
    if tarefas:
        with st.expander('✏️ Alterar Atividade/Nota'):
            # Cria dicionário: "Nome (ID: X)" → objeto tarefa completo
            opcoes_t = {f"{t['nome']} (ID: {t['id']})": t for t in tarefas}
            t_escolhida_str = st.selectbox('Selecione a Atividade para Alterar', options=[""] + list(opcoes_t.keys()))
            
            if t_escolhida_str:
                t_atual = opcoes_t[t_escolhida_str]
                
                # Recupera os valores atuais para pré-preencher o formulário
                def_nome     = t_atual.get('nome', '')
                def_disc_id  = t_atual.get('disc_id')
                # Se o ID da disciplina existir no mapeamento, usa o nome; senão usa o primeiro
                def_disc_nome = d_inverso.get(def_disc_id) if def_disc_id in d_inverso else list(opcoes_d.keys())[0]
                
                def_curso_id  = t_atual.get('curso_id')
                def_curso_nome = c_inverso.get(def_curso_id) if def_curso_id in c_inverso else list(opcoes_c.keys())[0]
                
                def_status = t_atual.get('status', 'Concluída')
                # Garante que a nota é float (evita erros de tipo)
                def_nota   = float(t_atual.get('nota', 0.0)) if t_atual.get('nota') is not None else 0.0
                
                # Converte a data de entrega armazenada para o tipo date
                def_data = datetime.today()
                if def_status == 'Para Entregar' and t_atual.get('data_entrega'):
                    try:
                        def_data = datetime.fromisoformat(str(t_atual['data_entrega']).split('T')[0]).date()
                    except:
                        pass
                
                # Formulário de edição com key única baseada no ID da tarefa
                with st.form(f"form_edit_{t_atual['id']}"):
                    novo_nome = st.text_input('Nome da Atividade', value=def_nome)
                    
                    # Define o índice do selectbox para a disciplina atual
                    index_disc = list(opcoes_d.keys()).index(def_disc_nome) if def_disc_nome in opcoes_d else 0
                    nova_disc  = st.selectbox('Disciplina', options=list(opcoes_d.keys()), index=index_disc)
                    
                    # Define o índice do selectbox para o curso atual
                    index_curso = list(opcoes_c.keys()).index(def_curso_nome) if def_curso_nome in opcoes_c else 0
                    novo_curso  = st.selectbox('Curso Pertencente', options=list(opcoes_c.keys()), index=index_curso)
                    
                    # Define o status padrão (0 = Concluída, 1 = Para Entregar)
                    index_status = 1 if def_status == 'Para Entregar' else 0
                    novo_status  = st.selectbox('Status', options=['Concluída', 'Para Entregar'], index=index_status)
                    
                    nova_data = st.date_input('Data de Entrega', value=def_data, format="DD/MM/YYYY")
                    nova_nota = st.number_input('Nota Obtida', 0.0, 10.0, def_nota)
                    
                    submitted = st.form_submit_button('Atualizar Atividade')
                    if submitted:
                        # Monta o payload com os dados atualizados
                        dados_update = {
                            'nome'    : novo_nome,
                            'disc_id' : opcoes_d[nova_disc],
                            'curso_id': opcoes_c[novo_curso],
                            'status'  : novo_status
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                            
                        # Adiciona nota ou data de entrega conforme o status
                        if novo_status == 'Concluída':
                            dados_update['nota'] = nova_nota
                        elif novo_status == 'Para Entregar':
                            dados_update['data_entrega'] = nova_data.isoformat()
                            
                        # Envia o PATCH para atualizar o registro no Xano
                        res_patch = api_patch('tarefas', t_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Atividade atualizada!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
                
                st.markdown("---")
                # Botão que aciona o modal de confirmação de exclusão
                if st.button('🗑️ Remover Tarefa', type='primary', use_container_width=True):
                    confirm_delete_tarefa(t_atual['id'])

    # ── [R]EAD — Quadro de Atividades e Notas ────────────────
    if tarefas:
        # Converte a lista de tarefas em DataFrame para manipulação
        df_t = pd.DataFrame(tarefas)
        st.subheader('Quadro de Atividades e Notas')
        
        # Garante que as colunas esperadas existam mesmo se a API não retorná-las
        if 'status' not in df_t.columns:
            df_t['status'] = 'Concluída'
        if 'data_entrega' not in df_t.columns:
            df_t['data_entrega'] = None
        else:
            # Formata as datas de ISO 8601 para DD/MM/YYYY
            def format_date(d):
                if not d or pd.isna(d): return ""
                try:
                    return datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
                except:
                    return str(d)
            df_t['data_entrega'] = df_t['data_entrega'].apply(format_date)
            
        # Cruzar com o DataFrame de disciplinas para obter o nome da disciplina
        # (o DataFrame de tarefas só armazena disc_id — precisamos do nome para exibir)
        if discs:
            df_d    = pd.DataFrame(discs)
            # merge() une dois DataFrames pela coluna disc_id = id
            df_view = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', suffixes=('', '_disc'), how='left')
            df_view.rename(columns={'nome_disc': 'disciplina'}, inplace=True)
        else:
            df_view = df_t.copy()
            df_view['disciplina'] = "Desconhecida"
            
        # Cruzar com os cursos para obter o nome do curso
        if cursos:
            df_c = pd.DataFrame(cursos)
            if not df_c.empty and 'curso_id' in df_view.columns:
                # Cria coluna unificada 'nome_curso' compatível com os dois campos possíveis
                df_c['nome_curso'] = df_c.apply(lambda row: row.get('curso', row.get('name', 'Sem Nome')), axis=1)
                df_view = df_view.merge(df_c[['id', 'nome_curso']], left_on='curso_id', right_on='id', suffixes=('', '_curso'), how='left')
            else:
                df_view['nome_curso'] = 'N/A'
        else:
            df_view['nome_curso'] = 'N/A'
            
        # Seleciona apenas as colunas relevantes para exibição
        cols_to_show = ['id', 'nome', 'nome_curso', 'disciplina', 'status', 'data_entrega', 'nota']
        cols_to_show = [c for c in cols_to_show if c in df_view.columns]
        
        # Renomeia os cabeçalhos para português amigável
        rename_map = {
            'id'          : 'ID',
            'nome'        : 'Atividade',
            'nome_curso'  : 'Curso',
            'disciplina'  : 'Disciplina',
            'status'      : 'Status',
            'data_entrega': 'Data de Entrega',
            'nota'        : 'Nota'
        }
        df_display = df_view[cols_to_show].rename(columns=rename_map)
        
        # Exibe a tabela interativa no Streamlit
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ─── Ponto de entrada desta página ──────────────────────────
modulo_tarefas()

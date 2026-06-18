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
    
    # Cursos ativos: trazer somente os que estiver com o status cursando
    cursos_ativos = [c for c in cursos if c.get('status') == 'cursando']
    
    # Cursos: {nome: id}
    opcoes_c = {c.get('curso', c.get('name', 'Sem Nome')): c['id'] for c in cursos_ativos}
    # Cursos invertido: {id: nome} (inclui todos os cursos para resolver nomes históricos)
    c_inverso = {c['id']: c.get('curso', c.get('name', 'Sem Nome')) for c in cursos}

    # ── [C]REATE — Lançar Nova Atividade/Nota ────────────────
    with st.expander('➕ Lançar Atividade/Nota'):
        if not opcoes_c:
            st.warning("Não há nenhum curso ativo (com status 'cursando'). Acesse a página de Cursos para definir um curso como ativo.")
        else:
            nome_t     = st.text_input('Nome da Atividade')
            c_escolhido = st.selectbox('Curso Pertencente',      options=list(opcoes_c.keys()))
            id_curso_escolhido = opcoes_c[c_escolhido]
            
            # Filtrar as disciplinas associadas ao curso escolhido
            discs_filtradas = [d for d in discs if (d.get('curso_id') == id_curso_escolhido or d.get('course_id') == id_curso_escolhido)]
            opcoes_d_filtradas = {d['nome']: d['id'] for d in discs_filtradas}
            
            if not opcoes_d_filtradas:
                st.warning("Não há nenhuma disciplina vinculada a este curso. Cadastre disciplinas para este curso primeiro.")
            else:
                d_escolhida = st.selectbox('Selecione a Disciplina', options=list(opcoes_d_filtradas.keys()))
                
                # O status determina quais campos adicionais são exibidos
                status = st.selectbox('Status', options=['Concluída', 'Para Entregar'])
                
                # Sempre exibe o campo de data, alterando a etiqueta dinamicamente
                label_data = 'Data de Conclusão' if status == 'Concluída' else 'Data de Entrega'
                data_entrega = st.date_input(label_data, format="DD/MM/YYYY")
                    
                # Campo de nota só faz sentido para tarefas concluídas
                nota = 0.0
                if status == 'Concluída':
                    nota = st.number_input('Nota Obtida', 0.0, 10.0, 0.0)
                
                # Tipo de avaliação
                opcoes_tipo = {
                    "Outro": "OUTRO",
                    "MAP (Avaliação Parcial)": "MAP",
                    "PROVA (Prova Principal)": "PROVA",
                    "SUB (Substitutiva)": "SUB",
                    "PAI (Avaliação Interdisciplinar)": "PAI"
                }
                tipo_escolhido = st.selectbox('Tipo de Avaliação', options=list(opcoes_tipo.keys()))

                if st.button('Registrar Atividade'):
                    # Monta o payload com os campos obrigatórios
                    dados = {
                        'nome'    : nome_t,
                        'disc_id' : opcoes_d_filtradas[d_escolhida],  # Converte nome → ID da disciplina
                        'curso_id': id_curso_escolhido,              # ID do curso
                        'status'  : status,
                        'tipo'    : opcoes_tipo[tipo_escolhido]
                    }
                    # Vincula a tarefa ao usuário logado
                    if 'user_id' in st.session_state:
                        dados['user_id'] = st.session_state.user_id
                        
                    # Adiciona campos opcionais conforme o status escolhido
                    if status == 'Concluída':
                        dados['nota'] = nota
                        
                    if data_entrega:
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
            # Cria dicionário: "Nome - Disciplina (ID: X)" → objeto tarefa completo
            opcoes_t = {}
            for t in tarefas:
                disc_nome = d_inverso.get(t.get('disc_id'), 'Sem Disciplina')
                label = f"{t['nome']} - {disc_nome} (ID: {t['id']})"
                opcoes_t[label] = t
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
                if t_atual.get('data_entrega'):
                    try:
                        parsed_date = datetime.fromisoformat(str(t_atual['data_entrega']).split('T')[0]).date()
                        # Se o ano for maior que 1970 (data válida, não o padrão Unix Epoch), pré-preenche
                        if parsed_date.year > 1970:
                            def_data = parsed_date
                    except:
                        pass
                
                def_tipo = t_atual.get('tipo', 'OUTRO') or 'OUTRO'
                tipo_display_map = {
                    "OUTRO": "Outro",
                    "MAP": "MAP (Avaliação Parcial)",
                    "PROVA": "PROVA (Prova Principal)",
                    "SUB": "SUB (Substitutiva)",
                    "PAI": "PAI (Avaliação Interdisciplinar)"
                }
                def_tipo_nome = tipo_display_map.get(def_tipo, "Outro")
                
                # Monta opções de cursos para edição
                opcoes_c_edit = dict(opcoes_c)
                if def_curso_nome and def_curso_nome not in opcoes_c_edit and def_curso_id is not None:
                    opcoes_c_edit[def_curso_nome] = def_curso_id
                
                # Campos de edição (sem st.form para permitir a filtragem dinâmica)
                novo_nome = st.text_input('Nome da Atividade', value=def_nome, key=f"edit_nome_{t_atual['id']}")
                
                # Curso Pertencente acima de Disciplina
                index_curso = list(opcoes_c_edit.keys()).index(def_curso_nome) if def_curso_nome in opcoes_c_edit else 0
                novo_curso  = st.selectbox('Curso Pertencente', options=list(opcoes_c_edit.keys()), index=index_curso, key=f"edit_curso_{t_atual['id']}")
                id_novo_curso = opcoes_c_edit.get(novo_curso)
                
                # Filtrar disciplinas associadas ao curso selecionado na edição
                discs_filtradas_edit = [d for d in discs if (d.get('curso_id') == id_novo_curso or d.get('course_id') == id_novo_curso)]
                opcoes_d_filtradas_edit = dict(sorted({d['nome']: d['id'] for d in discs_filtradas_edit}.items()))
                
                if not opcoes_d_filtradas_edit:
                    st.warning("Não há nenhuma disciplina vinculada a este curso.")
                    nova_disc = None
                else:
                    # Tenta pré-selecionar a disciplina anterior se ela pertencer a esse curso, senão seleciona a primeira
                    def_disc_index = 0
                    if def_disc_nome in opcoes_d_filtradas_edit:
                        def_disc_index = list(opcoes_d_filtradas_edit.keys()).index(def_disc_nome)
                    nova_disc  = st.selectbox('Disciplina', options=list(opcoes_d_filtradas_edit.keys()), index=def_disc_index, key=f"edit_disc_{t_atual['id']}")
                
                index_status = 1 if def_status == 'Para Entregar' else 0
                novo_status  = st.selectbox('Status', options=['Concluída', 'Para Entregar'], index=index_status, key=f"edit_status_{t_atual['id']}")
                
                label_nova_data = 'Data de Conclusão' if novo_status == 'Concluída' else 'Data de Entrega'
                nova_data = st.date_input(label_nova_data, value=def_data, format="DD/MM/YYYY", key=f"edit_data_{t_atual['id']}")
                nova_nota = 0.0
                if novo_status == 'Concluída':
                    nova_nota = st.number_input('Nota Obtida', 0.0, 10.0, def_nota, key=f"edit_nota_{t_atual['id']}")
                
                opcoes_tipo = {
                    "Outro": "OUTRO",
                    "MAP (Avaliação Parcial)": "MAP",
                    "PROVA (Prova Principal)": "PROVA",
                    "SUB (Substitutiva)": "SUB",
                    "PAI (Avaliação Interdisciplinar)": "PAI"
                }
                index_tipo = list(opcoes_tipo.keys()).index(def_tipo_nome) if def_tipo_nome in opcoes_tipo else 0
                novo_tipo = st.selectbox('Tipo de Avaliação', options=list(opcoes_tipo.keys()), index=index_tipo, key=f"edit_tipo_{t_atual['id']}")

                if st.button('Atualizar Atividade', key=f"btn_edit_{t_atual['id']}"):
                    if not nova_disc:
                        st.error("Por favor, selecione uma disciplina válida para atualizar.")
                    else:
                        # Monta o payload com os dados atualizados
                        dados_update = {
                            'nome'    : novo_nome,
                            'disc_id' : opcoes_d_filtradas_edit[nova_disc],
                            'curso_id': id_novo_curso,
                            'status'  : novo_status,
                            'tipo'    : opcoes_tipo[novo_tipo]
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                            
                        # Adiciona nota se for concluída
                        if novo_status == 'Concluída':
                            dados_update['nota'] = nova_nota
                        
                        # Sempre envia a data de entrega/conclusão
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
            
        # Cruzar com o DataFrame de disciplinas para obter o nome da disciplina
        if discs:
            df_d    = pd.DataFrame(discs)
            df_view = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', suffixes=('', '_disc'), how='left')
            df_view.rename(columns={'nome_disc': 'disciplina'}, inplace=True)
        else:
            df_view = df_t.copy()
            df_view['disciplina'] = "Desconhecida"
            
        # Cruzar com os cursos para obter o nome do curso
        if cursos:
            df_c = pd.DataFrame(cursos)
            if not df_c.empty and 'curso_id' in df_view.columns:
                df_c['nome_curso'] = df_c.apply(lambda row: row.get('curso', row.get('name', 'Sem Nome')), axis=1)
                df_view = df_view.merge(df_c[['id', 'nome_curso']], left_on='curso_id', right_on='id', suffixes=('', '_curso'), how='left')
            else:
                df_view['nome_curso'] = 'N/A'
        else:
            df_view['nome_curso'] = 'N/A'
            
        # Mapeia tipo no dataframe para exibição
        tipo_lbl_map = {
            "MAP": "MAP",
            "PROVA": "Prova",
            "SUB": "Sub",
            "PAI": "PAI",
            "OUTRO": "Outro"
        }
        if 'tipo' in df_view.columns:
            df_view['tipo_lbl'] = df_view['tipo'].fillna('OUTRO').map(tipo_lbl_map).fillna('Outro')
        else:
            df_view['tipo_lbl'] = 'Outro'

        # Parse data crua para data real (para filtros e ordenação)
        def parse_date(d):
            if not d or pd.isna(d): return None
            try:
                if isinstance(d, (int, float)):
                    return datetime.fromtimestamp(d/1000.0).date()
                return datetime.fromisoformat(str(d).split('T')[0]).date()
            except:
                return None
        df_view['data_parsed'] = df_view['data_entrega'].apply(parse_date)

        # Filtros do Quadro de Atividades
        with st.expander("🔍 Filtrar Quadro de Atividades"):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                cursos_options = ["Todos"] + sorted(list(df_view['nome_curso'].dropna().unique()))
                filtro_curso = st.selectbox("Curso", options=cursos_options, key="filtro_board_curso")
            with f_col2:
                discs_options = ["Todas"] + sorted(list(df_view['disciplina'].dropna().unique()))
                filtro_disc = st.selectbox("Disciplina", options=discs_options, key="filtro_board_disc")
            with f_col3:
                status_options = ["Todos", "Concluída", "Para Entregar"]
                filtro_status = st.selectbox("Status", options=status_options, key="filtro_board_status")
                
            f_col4, f_col5, f_col6 = st.columns(3)
            with f_col4:
                tipo_options = ["Todos", "Outro", "MAP", "Prova", "Sub", "PAI"]
                filtro_tipo = st.selectbox("Tipo de Avaliação", options=tipo_options, key="filtro_board_tipo")
            with f_col5:
                filtro_data_ini = st.date_input("Data Entrega (De)", value=None, format="DD/MM/YYYY", key="filtro_board_dataini")
            with f_col6:
                filtro_data_fim = st.date_input("Data Entrega (Até)", value=None, format="DD/MM/YYYY", key="filtro_board_datafim")

        # Aplicando os filtros
        df_filtered = df_view.copy()
        if filtro_curso != "Todos":
            df_filtered = df_filtered[df_filtered['nome_curso'] == filtro_curso]
        if filtro_disc != "Todas":
            df_filtered = df_filtered[df_filtered['disciplina'] == filtro_disc]
        if filtro_status != "Todos":
            df_filtered = df_filtered[df_filtered['status'] == filtro_status]
        if filtro_tipo != "Todos":
            df_filtered = df_filtered[df_filtered['tipo_lbl'] == filtro_tipo]
        if filtro_data_ini:
            df_filtered = df_filtered[df_filtered['data_parsed'] >= filtro_data_ini]
        if filtro_data_fim:
            df_filtered = df_filtered[df_filtered['data_parsed'] <= filtro_data_fim]

        # Formata a data para exibição final
        def format_parsed_date(d):
            if not d or pd.isna(d) or d.year <= 1970: return ""
            return d.strftime('%d/%m/%Y')
        df_filtered['data_entrega_format'] = df_filtered['data_parsed'].apply(format_parsed_date)

        # Seleciona apenas as colunas relevantes para exibição
        cols_to_show = ['id', 'nome', 'nome_curso', 'disciplina', 'tipo_lbl', 'status', 'data_entrega_format', 'nota']
        cols_to_show = [c for c in cols_to_show if c in df_filtered.columns]
        
        # Renomeia os cabeçalhos para português amigável
        rename_map = {
            'id'                 : 'ID',
            'nome'               : 'Atividade',
            'nome_curso'         : 'Curso',
            'disciplina'         : 'Disciplina',
            'tipo_lbl'           : 'Tipo',
            'status'             : 'Status',
            'data_entrega_format': 'Data de Entrega',
            'nota'               : 'Nota'
        }
        df_display = df_filtered[cols_to_show].rename(columns=rename_map)
        
        # Exibe a tabela interativa no Streamlit
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ─── Ponto de entrada desta página ──────────────────────────
modulo_tarefas()

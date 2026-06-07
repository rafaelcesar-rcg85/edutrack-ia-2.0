"""
=============================================================
 pages/cursos.py — Módulo de Gerenciamento de Cursos
=============================================================
 Implementa o CRUD completo de Cursos:
   [C]reate — Adicionar novo curso
   [R]ead   — Listar cursos cadastrados
   [U]pdate — Alterar dados de um curso
   [D]elete — Remover um curso

 Os cursos são o nível mais alto da hierarquia:
   Curso → Disciplinas → Tarefas/Notas
=============================================================
"""

# ─── Importações ────────────────────────────────────────────
import streamlit as st   # Interface web
import pandas as pd      # Manipulação de tabelas de dados (DataFrames)
import datetime          # Tratamento de datas
from utils.api import api_post, api_get, api_patch, api_delete  # Funções CRUD da API


# ============================================================
# DIÁLOGO DE CONFIRMAÇÃO DE EXCLUSÃO
# ============================================================
@st.dialog("Confirmar Exclusão")
def confirm_delete_curso(curso_id):
    """
    Abre um modal (janela pop-up) de confirmação antes de deletar.
    
    @st.dialog é um decorador do Streamlit que transforma a função
    em um modal — o usuário precisa confirmar ou cancelar.
    Isso evita exclusões acidentais.
    """
    st.error("Tem certeza que deseja excluir este curso? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Voltar / Cancelar', use_container_width=True):
            st.rerun()  # Fecha o modal e volta à página normal
    with col2:
        if st.button('Confirmar Exclusão', type='primary', use_container_width=True):
            # Chama a API DELETE enviando o ID do curso a ser removido
            res_del = api_delete('curso', curso_id)
            if res_del.status_code == 200:
                st.success("Curso removido com sucesso!")
                st.rerun()  # Recarrega a página para atualizar a lista
            else:
                st.error(f"Erro ao remover: {res_del.text}")


# ============================================================
# MÓDULO PRINCIPAL DE CURSOS
# ============================================================
def modulo_cursos():
    """
    Função principal que monta toda a interface da página de Cursos.
    Segue a estrutura CRUD: Create → Update/Delete → Read.
    """
    st.header('Meus Cursos')
    
    # ── [C]REATE — Adicionar Novo Curso ──────────────────────
    # st.expander cria uma seção retrátil (abre/fecha ao clicar)
    with st.expander('➕ Adicionar Curso'):
        nome = st.text_input('Nome do Curso / Instituição')
        
        # st.columns divide a linha em colunas de igual tamanho
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input('Data de Início', key='create_data_inicio', format="DD/MM/YYYY")
        with col2:
            data_fim = st.date_input('Data de Fim', key='create_data_fim', format="DD/MM/YYYY")
            
        # st.selectbox cria uma lista suspensa com opções predefinidas
        status = st.selectbox('Status', options=["matriculado", "cursando", "formado"], key='create_status')
        
        if st.button('Cadastrar Curso'):
            if nome:
                # Monta o dicionário com os dados a enviar para a API
                dados_curso = {
                    'name'       : nome,
                    'curso'      : nome,  # Campo legado mantido para compatibilidade
                    'data_inicio': data_inicio.isoformat() if data_inicio else None,  # Converte para string ISO 8601
                    'data_fim'   : data_fim.isoformat() if data_fim else None,
                    'status'     : status
                }
                # Vincula o curso ao usuário logado via user_id da sessão
                if 'user_id' in st.session_state:
                    dados_curso['user_id'] = st.session_state.user_id
                    
                # Envia o POST para a API; o resultado é armazenado mas não usado aqui
                api_post('curso', dados_curso)
                st.success("Curso cadastrado com sucesso!")
                st.rerun()  # Recarrega para exibir o novo curso na listagem
            else:
                st.warning("Por favor, insira o nome do curso.")

    # ── Carregamento dos Cursos do Servidor ──────────────────
    # Faz GET na API para buscar a lista de cursos do usuário logado
    cursos = api_get('curso')
    
    # ── [U]PDATE — Alterar Curso Existente ───────────────────
    if cursos:  # Só exibe o formulário de edição se existirem cursos
        with st.expander('✏️ Alterar Curso'):
            # Cria um dicionário: "Nome do Curso (ID: X)" → objeto curso
            # Isso permite exibir um texto amigável no selectbox mas usar o objeto completo
            opcoes_c = {f"{c.get('curso', c.get('name', 'Sem Nome'))} (ID: {c['id']})": c for c in cursos}
            c_escolhido_str = st.selectbox('Selecione o Curso para Alterar', options=[""] + list(opcoes_c.keys()))
            
            if c_escolhido_str:
                # Recupera o objeto completo do curso selecionado
                c_atual = opcoes_c[c_escolhido_str]
                # Usa .get() com fallback para lidar com campos que podem não existir
                def_nome   = c_atual.get('curso', c_atual.get('name', ''))
                def_status = c_atual.get('status', 'matriculado')
                
                # Conversão segura de datas para o st.date_input
                # (a API retorna string ISO; precisamos de datetime.date)
                try:
                    def_data_inicio = datetime.date.fromisoformat(str(c_atual.get('data_inicio'))[:10]) if c_atual.get('data_inicio') else datetime.date.today()
                except Exception:
                    def_data_inicio = datetime.date.today()
                try:
                    def_data_fim = datetime.date.fromisoformat(str(c_atual.get('data_fim'))[:10]) if c_atual.get('data_fim') else datetime.date.today()
                except Exception:
                    def_data_fim = datetime.date.today()
                
                # st.form com key único garante que cada curso tem seu próprio formulário
                with st.form(f"form_edit_curso_{c_atual['id']}"):
                    novo_nome        = st.text_input('Nome do Curso', value=def_nome)
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_data_inicio = st.date_input('Data de Início', value=def_data_inicio, format="DD/MM/YYYY")
                    with col2:
                        novo_data_fim    = st.date_input('Data de Fim',    value=def_data_fim,    format="DD/MM/YYYY")
                        
                    opcoes_status = ["matriculado", "cursando", "formado"]
                    # Define o índice padrão no selectbox baseado no status atual do curso
                    idx_status = opcoes_status.index(def_status) if def_status in opcoes_status else 0
                    novo_status = st.selectbox('Status', options=opcoes_status, index=idx_status, key=f"status_{c_atual['id']}")
                    
                    if st.form_submit_button('Atualizar Curso'):
                        dados_update = {
                            'name'       : novo_nome,
                            'curso'      : novo_nome,
                            'data_inicio': novo_data_inicio.isoformat() if novo_data_inicio else None,
                            'data_fim'   : novo_data_fim.isoformat()    if novo_data_fim    else None,
                            'status'     : novo_status
                        }
                        if 'user_id' in st.session_state:
                            dados_update['user_id'] = st.session_state.user_id
                            
                        # Envia o PATCH passando o ID do curso a ser atualizado
                        res_patch = api_patch('curso', c_atual['id'], dados_update)
                        if res_patch.status_code in [200, 201]:
                            st.success("Curso atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao atualizar: {res_patch.text}")
                
                st.markdown("---")
                # Botão de exclusão que abre o modal de confirmação
                if st.button('🗑️ Remover Curso', type='primary', use_container_width=True):
                    confirm_delete_curso(c_atual['id'])

    # ── [R]EAD — Exibir Lista de Cursos ──────────────────────
    if cursos:
        # pd.DataFrame converte a lista de dicionários em uma tabela estruturada
        df = pd.DataFrame(cursos)
        st.subheader('Seus Cursos Cadastrados')
        
        # Função auxiliar para formatar datas de ISO 8601 para DD/MM/YYYY
        def format_date(d):
            if not d or pd.isna(d): return ""
            try:
                return datetime.datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
            except:
                return str(d)
                
        # Aplica a formatação nas colunas de data, se existirem no DataFrame
        if 'data_inicio' in df.columns:
            df['data_inicio'] = df['data_inicio'].apply(format_date)
        if 'data_fim' in df.columns:
            df['data_fim'] = df['data_fim'].apply(format_date)
        
        # Seleciona apenas as colunas relevantes para exibição
        cols_to_show = ['id', 'curso', 'name', 'status', 'data_inicio', 'data_fim']
        cols_to_show = [c for c in cols_to_show if c in df.columns]
        
        # Renomeia as colunas para nomes amigáveis em português
        rename_map = {
            'id'        : 'ID',
            'curso'     : 'Nome do Curso',
            'name'      : 'Nome do Curso',
            'status'    : 'Status',
            'data_inicio': 'Data de Início',
            'data_fim'  : 'Data de Fim'
        }
        df_display = df[cols_to_show].rename(columns=rename_map)
        
        # Exibe a tabela interativa no Streamlit
        # use_container_width=True → ocupa toda a largura disponível
        # hide_index=True          → oculta o índice numérico do pandas
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
    else:
        # Mensagem informativa quando não há dados
        st.info('Nenhum curso cadastrado ainda.')


# ─── Ponto de entrada desta página ──────────────────────────
modulo_cursos()

import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import requests
from utils.api import api_get, BASE_URL, USER_PROFILES_URL

def modulo_relatorios():
    st.markdown("<style>.block-container{padding-top: 2rem;}</style>", unsafe_allow_html=True)
    
    st.header('📋 Relatórios Acadêmicos')
    st.write('Analise seu progresso geral, verifique estatísticas de notas e exporte relatórios consolidados em formatos premium.')

    if not st.session_state.get('logged_in') or not st.session_state.get('auth_token'):
        st.warning('Você precisa estar logado para acessar esta página.')
        return

    # 1. BUSCAR DADOS
    token = st.session_state.auth_token
    headers = {'Authorization': f'Bearer {token}'}

    # Buscar dados do perfil do estudante do estado da sessão
    profile_data = st.session_state.get('user_profile', {})
    if isinstance(profile_data, list):
        profile_data = profile_data[0] if len(profile_data) > 0 else {}
    elif not isinstance(profile_data, dict):
        profile_data = {}

    # Buscar e-mail do estudante
    user_email = ""
    try:
        res_me = requests.get(f'{BASE_URL}/auth/me', headers=headers)
        if res_me.status_code == 200:
            user_email = res_me.json().get('email', '')
    except:
        pass

    # Buscar entidades do Xano
    professores = api_get('professores')
    disciplinas = api_get('disciplinas')
    tarefas = api_get('tarefas')

    # Se não houver disciplinas ou professores, orientar o usuário
    if not professores and not disciplinas and not tarefas:
        st.info("Ainda não há dados registrados para gerar o relatório. Cadastre professores, disciplinas e tarefas para começar!")
        return

    # Processar nome e dados do aluno para o cabeçalho do relatório
    session_name = st.session_state.get('user_name', 'Estudante')
    first_name = profile_data.get('first_name', '') or session_name
    last_name = profile_data.get('last_name', '')
    student_full_name = f"{first_name} {last_name}".strip()

    dob_value = profile_data.get('date_of_birth')
    dob_str = "Não informada"
    if dob_value:
        try:
            dob_date = datetime.datetime.fromtimestamp(dob_value / 1000).date()
            dob_str = dob_date.strftime('%d/%m/%Y')
        except:
            pass

    # 2. CÁLCULO DE MÉTRICAS E INDICADORES (KPIs)
    num_professores = len(professores) if professores else 0
    num_disciplinas = len(disciplinas) if disciplinas else 0
    num_tarefas = len(tarefas) if tarefas else 0
    
    tarefas_concluidas = [t for t in tarefas if t.get('status') == 'Concluída'] if tarefas else []
    tarefas_pendentes = [t for t in tarefas if t.get('status') == 'Para Entregar'] if tarefas else []
    
    num_concluidas = len(tarefas_concluidas)
    num_pendentes = len(tarefas_pendentes)
    
    taxa_conclusao = (num_concluidas / num_tarefas * 100) if num_tarefas > 0 else 0.0
    
    # Calcular média de notas (apenas concluídas e com nota válida)
    notas_validas = [float(t.get('nota')) for t in tarefas_concluidas if t.get('nota') is not None]
    media_geral = (sum(notas_validas) / len(notas_validas)) if notas_validas else 0.0

    # 3. EXIBIÇÃO DE METRICAS VISUAIS (DESIGN PREMIUM)
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #f3f0ff 0%, #e0d8ff 100%); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
        <h4 style="color: #4a3b8c; margin-top: 0; margin-bottom: 5px;">Relatório Consolidado de: {student_full_name}</h4>
        <p style="color: #666; margin: 0; font-size: 0.9em;">
            <strong>E-mail:</strong> {user_email or 'Não informado'} | 
            <strong>Data de Nascimento:</strong> {dob_str} | 
            <strong>Gerado em:</strong> {datetime.date.today().strftime('%d/%m/%Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Grid de KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #6c5ce7;">
            <p style="color: #888; font-size: 0.85em; margin-bottom: 5px; font-weight: 500;">MÉDIA GERAL</p>
            <h2 style="color: #4a3b8c; margin: 0; font-size: 1.8em;">{media_geral:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #27ae60;">
            <p style="color: #888; font-size: 0.85em; margin-bottom: 5px; font-weight: 500;">TAXA CONCLUSÃO</p>
            <h2 style="color: #27ae60; margin: 0; font-size: 1.8em;">{taxa_conclusao:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #e67e22;">
            <p style="color: #888; font-size: 0.85em; margin-bottom: 5px; font-weight: 500;">TAREFAS ATIVAS</p>
            <h2 style="color: #e67e22; margin: 0; font-size: 1.8em;">{num_tarefas}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #2980b9;">
            <p style="color: #888; font-size: 0.85em; margin-bottom: 5px; font-weight: 500;">DISCIPLINAS</p>
            <h2 style="color: #2980b9; margin: 0; font-size: 1.8em;">{num_disciplinas}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. GRÁFICOS INTERATIVOS
    st.subheader('📊 Gráficos de Acompanhamento')
    g1, g2 = st.columns([6, 4], gap="medium")
    
    with g1:
        # Gráfico de Desempenho por Disciplina
        if tarefas and disciplinas:
            df_t = pd.DataFrame(tarefas)
            df_d = pd.DataFrame(disciplinas)
            df_merged = df_t.merge(df_d, left_on='disc_id', right_on='id', suffixes=('_t', '_d'))
            
            # Filtro para notas
            df_concluidas = df_merged[(df_merged['status'] == 'Concluída') & (df_merged['nota'].notna())]
            
            if not df_concluidas.empty:
                df_concluidas['nota'] = df_concluidas['nota'].astype(float)
                # Agrupar e calcular média por disciplina
                df_media_disc = df_concluidas.groupby('nome_d')['nota'].mean().reset_index()
                df_media_disc.columns = ['Disciplina', 'Média de Notas']
                
                fig_bar = px.bar(
                    df_media_disc, 
                    x='Disciplina', 
                    y='Média de Notas',
                    color='Média de Notas',
                    color_continuous_scale=px.colors.sequential.Purples[2:], # Evitar o tom mais claro
                    title='Média de Notas por Disciplina'
                )
                
                # Adicionando um contorno (borda) nas colunas para garantir que mesmo cores claras fiquem visíveis
                fig_bar.update_traces(marker_line_color='#4a3b8c', marker_line_width=1.5)
                
                fig_bar.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="",
                    yaxis_title="Nota Média",
                    yaxis=dict(gridcolor='#eee', range=[0, 10]),
                    margin=dict(l=0, r=0, t=35, b=0),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Registre atividades concluídas com notas para gerar o gráfico de desempenho por disciplina.")
        else:
            st.info("Informações insuficientes para gerar o gráfico de barras.")

    with g2:
        # Distribuição de Tarefas
        if tarefas:
            df_t = pd.DataFrame(tarefas)
            df_status = df_t['status'].value_counts().reset_index()
            df_status.columns = ['Status', 'Quantidade']
            
            fig_pie = px.pie(
                df_status, 
                values='Quantidade', 
                names='Status',
                color='Status',
                color_discrete_map={'Concluída': '#27ae60', 'Para Entregar': '#e67e22'},
                title='Distribuição de Status de Tarefas',
                hole=0.4
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=35, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Registre tarefas para visualizar a distribuição de status.")

    st.markdown("<br><hr style='border-top: 1px solid #eee;'><br>", unsafe_allow_html=True)

    # 5. QUADROS DETALHADOS E FILTROS
    st.subheader('📝 Quadro Geral de Informações')
    
    tab_tarefas, tab_disciplinas, tab_professores = st.tabs(['Tarefas e Notas', 'Disciplinas', 'Professores'])
    
    with tab_tarefas:
        if tarefas:
            df_t = pd.DataFrame(tarefas)
            df_d = pd.DataFrame(disciplinas) if disciplinas else pd.DataFrame()
            
            # Formatação de datas e junção de disciplina
            if not df_d.empty:
                df_t_view = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', suffixes=('', '_disc'))
            else:
                df_t_view = df_t.copy()
                df_t_view['nome_disc'] = 'N/A'

            # Filtros na Interface do Streamlit
            st.write("🔍 **Filtrar Dados do Quadro**")
            f_col1, f_col2 = st.columns(2)
            
            with f_col1:
                disc_options = ['Todas'] + list(df_t_view['nome_disc'].unique())
                filtro_disc = st.selectbox('Filtrar por Disciplina', options=disc_options, key='filtro_disc_rep')
                
            with f_col2:
                status_options = ['Todos', 'Concluída', 'Para Entregar']
                filtro_status = st.selectbox('Filtrar por Status', options=status_options, key='filtro_status_rep')
            
            # Aplicar filtros
            df_filtrado = df_t_view.copy()
            if filtro_disc != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['nome_disc'] == filtro_disc]
            if filtro_status != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['status'] == filtro_status]
                
            # Formatar a data
            def format_date(d):
                if not d or pd.isna(d): return "-"
                try:
                    return datetime.datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
                except:
                    return str(d)
            
            if 'data_entrega' in df_filtrado.columns:
                df_filtrado['data_entrega_format'] = df_filtrado['data_entrega'].apply(format_date)
            else:
                df_filtrado['data_entrega_format'] = "-"
                
            if 'nota' not in df_filtrado.columns:
                df_filtrado['nota'] = "-"
            else:
                df_filtrado['nota'] = df_filtrado['nota'].apply(lambda x: f"{float(x):.1f}" if x is not None and not pd.isna(x) else "-")

            df_filtrado = df_filtrado.rename(columns={
                'nome': 'Tarefa/Atividade',
                'nome_disc': 'Disciplina',
                'status': 'Status',
                'data_entrega_format': 'Prazo/Entrega',
                'nota': 'Nota'
            })
            
            cols_exibicao = ['Tarefa/Atividade', 'Disciplina', 'Status', 'Prazo/Entrega', 'Nota']
            cols_exibicao = [c for c in cols_exibicao if c in df_filtrado.columns]
            
            st.dataframe(df_filtrado[cols_exibicao], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma tarefa cadastrada.")

    with tab_disciplinas:
        if disciplinas:
            df_d = pd.DataFrame(disciplinas)
            df_p = pd.DataFrame(professores) if professores else pd.DataFrame()
            
            if not df_p.empty:
                df_d_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'))
            else:
                df_d_view = df_d.copy()
                df_d_view['nome_prof'] = 'N/A'
                
            df_d_view = df_d_view.rename(columns={
                'id': 'ID Disciplina',
                'nome': 'Nome da Matéria',
                'nome_prof': 'Professor Responsável'
            })
            
            st.dataframe(df_d_view[['ID Disciplina', 'Nome da Matéria', 'Professor Responsável']], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma disciplina cadastrada.")

    with tab_professores:
        if professores:
            df_p = pd.DataFrame(professores)
            df_p = df_p.rename(columns={
                'id': 'ID Professor',
                'nome': 'Nome',
                'email': 'E-mail de Contato'
            })
            
            cols_p = ['ID Professor', 'Nome', 'E-mail de Contato']
            cols_p = [c for c in cols_p if c in df_p.columns]
            
            st.dataframe(df_p[cols_p], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum professor cadastrado.")

    st.markdown("<br><hr style='border-top: 1px solid #eee;'><br>", unsafe_allow_html=True)

    # 6. GERAÇÃO DE EXPORTAÇÃO PREMIUM EM HTML (PRONTO PARA IMPRESSÃO EM PDF)
    st.subheader('📥 Central de Exportação')
    st.write('Baixe o relatório consolidado para impressão ou análise externa.')

    # Lógica de construção do HTML Premium
    # CSS com design incrível baseado em HSL/RGB do EduTrack AI
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>EduTrack AI - Relatório Acadêmico Completo</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #f8f9fa;
            color: #2d3748;
            margin: 0;
            padding: 40px 20px;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        }}
        
        /* Banner de Cabeçalho */
        .header-banner {{
            background: linear-gradient(135deg, #6c5ce7 0%, #4a3b8c 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }}
        .header-banner h1 {{
            margin: 0 0 10px 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header-banner p {{
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .student-info {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            font-size: 13px;
        }}
        .student-info div span {{
            font-weight: 600;
            display: block;
            margin-bottom: 2px;
            opacity: 0.8;
        }}
        .student-info div p {{
            margin: 0;
            font-weight: 500;
            font-size: 14px;
        }}

        /* Grade de Indicadores (KPIs) */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 35px;
        }}
        .metric-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: transform 0.2s;
        }}
        .metric-card.primary {{ border-top: 4px solid #6c5ce7; }}
        .metric-card.success {{ border-top: 4px solid #27ae60; }}
        .metric-card.warning {{ border-top: 4px solid #e67e22; }}
        .metric-card.info {{ border-top: 4px solid #2980b9; }}
        
        .metric-label {{
            font-size: 10px;
            font-weight: 700;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: #1a202c;
            margin: 0;
        }}

        /* Seções e Tabelas */
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #edf2f7;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            font-size: 13px;
        }}
        th {{
            background-color: #f7fafc;
            color: #4a5568;
            font-weight: 600;
            text-align: left;
            padding: 10px 12px;
            border-bottom: 2px solid #e2e8f0;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #edf2f7;
            color: #4a5568;
        }}
        tr:hover {{
            background-color: #fcfcfd;
        }}
        
        /* Badges de Status e Notas */
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge.concluida {{
            background-color: #def7ec;
            color: #03543f;
        }}
        .badge.entrega {{
            background-color: #fef3c7;
            color: #92400e;
        }}
        
        .nota-badge {{
            font-weight: bold;
            color: #2d3748;
        }}
        .nota-badge.aprovado {{
            color: #27ae60;
        }}
        .nota-badge.reprovado {{
            color: #e74c3c;
        }}

        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 11px;
            color: #a0aec0;
            border-top: 1px solid #edf2f7;
            padding-top: 20px;
        }}
        
        /* Otimizações Específicas para Impressão PDF */
        @media print {{
            body {{
                background-color: #ffffff;
                padding: 0;
                margin: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
                max-width: 100%;
            }}
            .header-banner {{
                background: #f1f1f1 !important;
                color: #000000 !important;
                border: 1px solid #ccc;
            }}
            .student-info {{
                border-top: 1px solid #999;
            }}
            .student-info div span, .student-info div p {{
                color: #000 !important;
            }}
            .metric-card {{
                border: 1px solid #ccc !important;
            }}
            .metric-value {{
                color: #000 !important;
            }}
            tr {{
                page-break-inside: avoid;
            }}
            th {{
                border-bottom: 2px solid #333 !important;
            }}
            td {{
                border-bottom: 1px solid #ddd !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Banner de Cabeçalho -->
        <div class="header-banner">
            <h1>EduTrack AI</h1>
            <p>Relatório de Desempenho e Histórico Acadêmico</p>
            
            <div class="student-info">
                <div>
                    <span>ESTUDANTE</span>
                    <p>{student_full_name}</p>
                </div>
                <div>
                    <span>E-MAIL</span>
                    <p>{user_email or 'Não informado'}</p>
                </div>
                <div>
                    <span>NASCIMENTO</span>
                    <p>{dob_str}</p>
                </div>
                <div>
                    <span>DATA DE EMISSÃO</span>
                    <p>{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </div>

        <!-- Grade de Metricas -->
        <div class="metrics-grid">
            <div class="metric-card primary">
                <div class="metric-label">Média Geral</div>
                <div class="metric-value">{media_geral:.2f}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Taxa Conclusão</div>
                <div class="metric-value">{taxa_conclusao:.1f}%</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Total Atividades</div>
                <div class="metric-value">{num_tarefas}</div>
            </div>
            <div class="metric-card info">
                <div class="metric-label">Disciplinas</div>
                <div class="metric-value">{num_disciplinas}</div>
            </div>
        </div>

        <!-- Tabela de Tarefas e Notas -->
        <div class="section-title">
            <span>Histórico de Tarefas, Atividades e Notas</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Atividade</th>
                    <th>Disciplina</th>
                    <th>Status</th>
                    <th>Prazo/Entrega</th>
                    <th>Nota</th>
                </tr>
            </thead>
            <tbody>"""
            
    # Adicionar as tarefas dinamicamente no HTML
    if tarefas:
        df_t = pd.DataFrame(tarefas)
        df_d = pd.DataFrame(disciplinas) if disciplinas else pd.DataFrame()
        if not df_d.empty:
            df_merged_t = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', suffixes=('', '_disc'))
        else:
            df_merged_t = df_t.copy()
            df_merged_t['nome_disc'] = 'N/A'

        for _, row in df_merged_t.iterrows():
            nome_t = row.get('nome', '-')
            disc_n = row.get('nome_disc', '-')
            status_t = row.get('status', 'Concluída')
            
            # Format status badge
            if status_t == 'Concluída':
                badge_class = "badge concluida"
                status_desc = "Concluída"
            else:
                badge_class = "badge entrega"
                status_desc = "Para Entregar"
                
            # Data entrega
            d_val = row.get('data_entrega')
            prazo = "-"
            if d_val:
                try:
                    prazo = datetime.datetime.fromisoformat(str(d_val).split('T')[0]).strftime('%d/%m/%Y')
                except:
                    prazo = str(d_val)
                    
            # Nota
            nota_val = row.get('nota')
            if nota_val is not None and not pd.isna(nota_val):
                nota_num = float(nota_val)
                nota_class = "nota-badge aprovado" if nota_num >= 6.0 else "nota-badge reprovado"
                nota_desc = f"<span class='{nota_class}'>{nota_num:.1f}</span>"
            else:
                nota_desc = "-"
                
            html_content += f"""
                <tr>
                    <td style="font-weight: 500;">{nome_t}</td>
                    <td>{disc_n}</td>
                    <td><span class="{badge_class}">{status_desc}</span></td>
                    <td>{prazo}</td>
                    <td>{nota_desc}</td>
                </tr>"""
    else:
        html_content += """<tr><td colspan="5" style="text-align: center; color: #a0aec0;">Nenhuma tarefa/nota cadastrada ainda.</td></tr>"""

    html_content += """
            </tbody>
        </table>

        <!-- Tabela de Disciplinas e Professores -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px;">
            <div>
                <div class="section-title">Disciplinas e Corpo Docente</div>
                <table>
                    <thead>
                        <tr>
                            <th>Disciplina</th>
                            <th>Professor</th>
                        </tr>
                    </thead>
                    <tbody>"""
                    
    # Adicionar disciplinas dinamicamente
    if disciplinas:
        df_d = pd.DataFrame(disciplinas)
        df_p = pd.DataFrame(professores) if professores else pd.DataFrame()
        if not df_p.empty:
            df_merged_d = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', suffixes=('', '_prof'))
        else:
            df_merged_d = df_d.copy()
            df_merged_d['nome_prof'] = 'N/A'

        for _, row in df_merged_d.iterrows():
            d_nome = row.get('nome', '-')
            p_nome = row.get('nome_prof', '-')
            html_content += f"""
                        <tr>
                            <td style="font-weight: 500;">{d_nome}</td>
                            <td>{p_nome}</td>
                        </tr>"""
    else:
        html_content += """<tr><td colspan="2" style="text-align: center; color: #a0aec0;">Nenhuma disciplina cadastrada.</td></tr>"""

    html_content += """
                    </tbody>
                </table>
            </div>

            <div>
                <div class="section-title">Contatos dos Professores</div>
                <table>
                    <thead>
                        <tr>
                            <th>Professor</th>
                            <th>E-mail de Contato</th>
                        </tr>
                    </thead>
                    <tbody>"""

    # Adicionar contatos de professores dinamicamente
    if professores:
        for p in professores:
            p_nome = p.get('nome', '-')
            p_email = p.get('email', '-') or "Não informado"
            html_content += f"""
                        <tr>
                            <td style="font-weight: 500;">{p_nome}</td>
                            <td style="font-family: monospace; font-size: 12px;">{p_email}</td>
                        </tr>"""
    else:
        html_content += """<tr><td colspan="2" style="text-align: center; color: #a0aec0;">Nenhum professor cadastrado.</td></tr>"""

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Rodapé do Relatório -->
        <div class="footer">
            <p>EduTrack AI - Sistema Inteligente de Acompanhamento Acadêmico</p>
            <p style="opacity: 0.7;">Este relatório foi gerado automaticamente pelo sistema e reflete fielmente os dados armazenados na plataforma.</p>
        </div>
    </div>
</body>
</html>"""

    # Lógica de download em CSV
    csv_data = ""
    if tarefas:
        df_t = pd.DataFrame(tarefas)
        df_d = pd.DataFrame(disciplinas) if disciplinas else pd.DataFrame()
        if not df_d.empty:
            df_merged_t = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', suffixes=('', '_disc'))
        else:
            df_merged_t = df_t.copy()
            df_merged_t['nome_disc'] = 'N/A'
        
        # Formatar a data para CSV
        def format_date_simple(d):
            if not d or pd.isna(d): return ""
            try:
                return datetime.datetime.fromisoformat(str(d).split('T')[0]).strftime('%Y-%m-%d')
            except:
                return str(d)
        
        df_export = pd.DataFrame()
        df_export['ID'] = df_merged_t.get('id', '')
        df_export['Tarefa_Atividade'] = df_merged_t.get('nome', '')
        df_export['Disciplina'] = df_merged_t.get('nome_disc', '')
        df_export['Status'] = df_merged_t.get('status', '')
        df_export['Prazo_Entrega'] = df_merged_t['data_entrega'].apply(format_date_simple) if 'data_entrega' in df_merged_t.columns else ""
        df_export['Nota'] = df_merged_t.get('nota', '')
        
        csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')

    # Opções de downloads na UI do Streamlit
    ex_col1, ex_col2 = st.columns(2)
    
    with ex_col1:
        st.download_button(
            label="📄 Baixar Relatório Premium (HTML)",
            data=html_content,
            file_name=f"Relatorio_Academico_{student_full_name.replace(' ', '_')}.html",
            mime="text/html",
            help="Baixa um relatório visual elegante. Abra no navegador e use Ctrl+P para salvar como PDF.",
            use_container_width=True
        )

    with ex_col2:
        if csv_data:
            st.download_button(
                label="📊 Baixar Dados em Planilha (CSV)",
                data=csv_data,
                file_name=f"Dados_Academicos_{student_full_name.replace(' ', '_')}.csv",
                mime="text/csv",
                help="Baixa a grade completa em formato compatível com Excel e Google Sheets.",
                use_container_width=True
            )
        else:
            st.button("📊 Baixar Dados em Planilha (CSV)", disabled=True, use_container_width=True)

modulo_relatorios()

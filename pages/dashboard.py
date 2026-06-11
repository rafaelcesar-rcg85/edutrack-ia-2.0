import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
from datetime import datetime, date
import calendar
from utils.api import api_get
from utils.theme import apply_theme

def get_custom_calendar(year, month, task_dict):
    cal = calendar.monthcalendar(year, month)
    
    html = f"""
    <style>
    .cal-container {{
        background: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
        width: 100%;
        overflow: hidden;
    }}
    .cal-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }}
    .cal-table th {{
        color: #888;
        font-weight: normal;
        font-size: 0.8em;
        padding-bottom: 6px;
        text-align: center;
    }}
    .cal-table td {{
        text-align: center;
        padding: 4px 0;
        font-size: 0.85em;
        color: #555;
    }}
    .cal-day {{
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        border-radius: 50%;
        transition: transform 0.2s;
    }}
    .cal-day:hover {{
        transform: scale(1.1);
    }}
    .cal-day.active {{
        background-color: #f3f0ff;
        font-weight: bold;
    }}
    /* Cores das tarefas */
    .cal-day.task-pendente {{
        border: 2px solid #e67e22;
        color: #e67e22;
        font-weight: bold;
        line-height: 20px;
        cursor: help;
    }}
    .cal-day.task-concluida {{
        border: 2px solid #27ae60;
        color: #27ae60;
        font-weight: bold;
        line-height: 20px;
        cursor: help;
    }}
    .cal-day.task-mixed {{
        border: 2px solid #3498db;
        color: #3498db;
        font-weight: bold;
        line-height: 20px;
        cursor: help;
    }}
    .cal-day.active.task-pendente, .cal-day.active.task-concluida, .cal-day.active.task-mixed {{
        background-color: #f8f9fa;
    }}
    </style>
    <div class="cal-container">
        <table class="cal-table">
            <tr><th>D</th><th>S</th><th>T</th><th>Q</th><th>Q</th><th>S</th><th>S</th></tr>
    """
    
    today = date.today()
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            else:
                current_date = date(year, month, day)
                classes = ["cal-day"]
                if current_date == today:
                    classes.append("active")
                    
                title_attr = ""
                if current_date in task_dict:
                    day_tasks = task_dict[current_date]
                    
                    has_pendente = any(t.get('status') == 'Para Entregar' for t in day_tasks)
                    has_concluida = any(t.get('status') == 'Concluída' for t in day_tasks)
                    
                    if has_pendente and has_concluida:
                        classes.append("task-mixed")
                    elif has_pendente:
                        classes.append("task-pendente")
                    elif has_concluida:
                        classes.append("task-concluida")
                    
                    # Tooltip content com quebra de linha HTML (&#10;)
                    titles = [f"• {t.get('nome', 'Tarefa')} ({t.get('status', '')})" for t in day_tasks]
                    tooltip = "&#10;".join(titles)
                    title_attr = f'title="{tooltip}"'
                
                class_str = " ".join(classes)
                html += f'<td><span class="{class_str}" {title_attr}>{day}</span></td>'
        html += "</tr>"
    html += "</table></div>"
    
    return html

def modulo_dashboard():
    # Aplica o tema visual escolhido pelo usuário
    apply_theme()
    # Remove margins superior do título pra dar mais espaço
    st.markdown("<style>.block-container{padding-top: 2rem;}</style>", unsafe_allow_html=True)
    
    # Busca o perfil do usuário da session state para personalização
    profile = st.session_state.get('user_profile', {})
    if isinstance(profile, list):
        profile = profile[0] if len(profile) > 0 else {}
    elif not isinstance(profile, dict):
        profile = {}
    
    tarefas = api_get('tarefas')
    discs = api_get('disciplinas')
    cursos = api_get('curso')

    # Processar métricas
    num_cursos = len(cursos) if cursos else 0
    num_discs = len(discs) if discs else 0
    concluidas = len([t for t in tarefas if t.get('status') == 'Concluída']) if tarefas else 0
    pendentes = len([t for t in tarefas if t.get('status') == 'Para Entregar']) if tarefas else 0
    
    # Mapeamento rápido de cursos para a side bar
    map_cursos = {}
    if cursos:
        for c in cursos:
            map_cursos[c['id']] = c.get('curso', c.get('name', 'Sem Nome'))
    
    # Processar datas
    task_dict = {}
    upcoming_tasks = []
    if tarefas:
        for t in tarefas:
            d_str = t.get('data_entrega')
            if d_str:
                try:
                    if isinstance(d_str, int):
                        dt = datetime.fromtimestamp(d_str/1000.0).date()
                    else:
                        dt = datetime.fromisoformat(str(d_str).split('T')[0]).date()
                        
                    if dt not in task_dict:
                        task_dict[dt] = []
                    task_dict[dt].append(t)
                    
                    if t.get('status') == 'Para Entregar':
                        t['parsed_date'] = dt
                        upcoming_tasks.append(t)
                except:
                    pass
    
    # Ordenar próximas tarefas pela data mais próxima
    upcoming_tasks.sort(key=lambda x: x['parsed_date'])

    col_main, col_side = st.columns([7, 3], gap="large")

    with col_main:
        # Personaliza o banner de boas-vindas
        # Pega o nome do perfil (que pode ser completo) ou da sessão e extrai a primeira palavra.
        name_for_banner = profile.get('first_name') or st.session_state.get('user_name', 'Usuário')
        first_name = name_for_banner.split(' ')[0]

        # Banner
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #f3f0ff 0%, #e0d8ff 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px;">
            <h2 style="color: #4a3b8c; margin-top: 0;">Bem-vindo(a) de volta, {first_name}!</h2>
            <p style="color: #666; margin-bottom: 0;">Acompanhe seu desempenho e mantenha o ritmo. Continue melhorando!</p>
        </div>
        """, unsafe_allow_html=True)

        # Métricas em "Cards"
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Cursos Cadastrados</p>
                <h2 style="color: #3498db; margin: 0;">{num_cursos}</h2>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Disciplinas Ativas</p>
                <h2 style="color: #4a3b8c; margin: 0;">{num_discs}</h2>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Tarefas Concluídas</p>
                <h2 style="color: #27ae60; margin: 0;">{concluidas}</h2>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Para Entregar</p>
                <h2 style="color: #e67e22; margin: 0;">{pendentes}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráfico
        st.subheader("Evolução de Notas")
        if tarefas and discs:
            df_t = pd.DataFrame(tarefas)
            df_d = pd.DataFrame(discs)
            df_plot = df_t.merge(df_d, left_on='disc_id', right_on='id', suffixes=('_t', '_d'))
            
            if cursos:
                df_c = pd.DataFrame(cursos)
                if not df_c.empty:
                    df_c['nome_curso'] = df_c.apply(lambda row: row.get('curso', row.get('name', 'Sem Nome')), axis=1)
                    
                    col_curso = None
                    if 'curso_id_t' in df_plot.columns:
                        col_curso = 'curso_id_t'
                    elif 'curso_id' in df_plot.columns:
                        col_curso = 'curso_id'
                    elif 'curso_id_d' in df_plot.columns:
                        col_curso = 'curso_id_d'
                        
                    if col_curso:
                        df_plot = df_plot.merge(df_c[['id', 'nome_curso']], left_on=col_curso, right_on='id', suffixes=('', '_c'), how='left')
                        df_plot['nome_curso'] = df_plot['nome_curso'].fillna('N/A')
                    else:
                        df_plot['nome_curso'] = 'N/A'
                else:
                    df_plot['nome_curso'] = 'N/A'
            else:
                df_plot['nome_curso'] = 'N/A'
            
            # Filtrar para exibir apenas as tarefas com status "Concluída" no gráfico
            if 'status_t' in df_plot.columns:
                df_plot = df_plot[df_plot['status_t'] == 'Concluída']
            elif 'status' in df_plot.columns:
                df_plot = df_plot[df_plot['status'] == 'Concluída']
                
            if not df_plot.empty:
                # Obter lista de cursos disponíveis
                cursos_disponiveis = [c for c in df_plot['nome_curso'].unique() if pd.notna(c) and c != 'N/A']
                opcoes_cursos = ["Todos os Cursos"] + sorted(cursos_disponiveis)
                
                # Filtro principal de curso
                filtro_curso = st.selectbox("Selecione o Curso para visualizar as Disciplinas", opcoes_cursos)
                
                # Aplica o filtro de curso
                if filtro_curso != "Todos os Cursos":
                    df_plot_filtro = df_plot[df_plot['nome_curso'] == filtro_curso]
                else:
                    df_plot_filtro = df_plot
                
                if not df_plot_filtro.empty:
                    # Opções de visualização para o usuário (Tipo e Ordem)
                    col_chart_type, col_sort = st.columns(2)
                    with col_chart_type:
                        tipo_grafico = st.selectbox("Escolha o tipo de gráfico", ["Linha", "Barra", "Dispersão"])
                    with col_sort:
                        ordem_grafico = st.selectbox("Ordem de Exibição", ["Cronológica", "Alfabética"])
                    
                    # Ordenar o dataframe com base na escolha
                    if ordem_grafico == "Cronológica":
                        df_plot_filtro = df_plot_filtro.sort_values(by='id_t')
                    else:
                        df_plot_filtro = df_plot_filtro.sort_values(by='nome_t')
                    
                    if tipo_grafico == "Linha":
                        fig = px.line(df_plot_filtro, x='nome_t', y='nota', color='nome_d', markers=True)
                    elif tipo_grafico == "Barra":
                        fig = px.bar(df_plot_filtro, x='nome_t', y='nota', color='nome_d', barmode='group')
                    elif tipo_grafico == "Dispersão":
                        fig = px.scatter(df_plot_filtro, x='nome_t', y='nota', color='nome_d', size='nota')
                    
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="",
                        yaxis_title="Nota",
                        legend_title="Disciplina",
                        margin=dict(l=0, r=0, t=20, b=0),
                        yaxis=dict(gridcolor='#eee', range=[0, 10])
                    )
                    if tipo_grafico == "Linha":
                        fig.update_traces(line=dict(width=3), marker=dict(size=8))
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Não há tarefas concluídas para o curso selecionado.")
            else:
                st.info("Cadastre notas nas atividades concluídas para visualizar o gráfico.")
        else:
            st.info("Cadastre dados para visualizar seu desempenho gráfico.")

    with col_side:
        # Card do Perfil do Usuário
        if profile:
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()

            if full_name:
                # Obter email
                token = st.session_state.get('auth_token')
                user_email = st.session_state.get('user_email', '')
                if token and not user_email:
                    try:
                        import requests
                        from utils.api import BASE_URL
                        res_me = requests.get(f'{BASE_URL}/auth/me', headers={'Authorization': f'Bearer {token}'})
                        if res_me.status_code == 200:
                            user_email = res_me.json().get('email', '')
                            st.session_state.user_email = user_email
                    except:
                        pass
                
                # Obter data de nascimento
                dob_str = ""
                dob = profile.get('date_of_birth')
                if dob:
                    try:
                        dob_date = datetime.fromtimestamp(dob / 1000).date()
                        dob_str = dob_date.strftime('%d/%m/%Y')
                    except:
                        pass
                
                email_html = f"<p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>📧 {user_email}</p>" if user_email else ""
                dob_html = f"<p style='margin: 2px 0 0 0; color: #888; font-size: 0.85em;'>🎂 {dob_str}</p>" if dob_str else ""

                formados = [c.get('curso', c.get('name', '')) for c in (cursos or []) if c.get('status') == 'formado']
                formados_html = ""
                if formados:
                    lista_f = ", ".join(formados)
                    formados_html = f"<p style='margin: 10px 0 0 0; color: #27ae60; font-size: 0.85em; font-weight: bold;'>🎓 Formado em: {lista_f}</p>"
                    
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;">
                    <h4 style="color: #333; margin: 0;">{full_name}</h4>
                    {email_html}
                    {dob_html}
                    {formados_html}
                </div>
                """, unsafe_allow_html=True)
                
        # Status dos Cursos (Cursando / Matriculado)
        if cursos:
            hoje = date.today()
            for c in cursos:
                c_nome = c.get('curso', c.get('name', 'Sem Nome'))
                c_status = c.get('status', 'matriculado')
                
                # Parse datas
                d_inicio = None
                d_fim = None
                try:
                    if c.get('data_inicio'):
                        d_inicio = datetime.fromisoformat(str(c['data_inicio']).split('T')[0]).date()
                    if c.get('data_fim'):
                        d_fim = datetime.fromisoformat(str(c['data_fim']).split('T')[0]).date()
                except:
                    pass
                
                if c_status == 'cursando':
                    if d_fim:
                        dias_falta = (d_fim - hoje).days
                        txt_dias = f"Faltam {dias_falta} dias para o fim" if dias_falta >= 0 else "Prazo encerrado"
                    else:
                        txt_dias = "Data de fim não definida"
                        
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <p style="margin: 0; font-weight: bold; color: #333; font-size: 0.9em;">📘 Cursando: {c_nome}</p>
                        <p style="margin: 0; color: #888; font-size: 0.8em; margin-top: 5px;">⏳ {txt_dias}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                elif c_status == 'matriculado':
                    if d_inicio:
                        dias_falta = (d_inicio - hoje).days
                        txt_dias = f"Começa em {dias_falta} dias" if dias_falta >= 0 else "Já começou ou data passada"
                    else:
                        txt_dias = "Data de início não definida"
                        
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #f1c40f; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <p style="margin: 0; font-weight: bold; color: #333; font-size: 0.9em;">📅 Matriculado: {c_nome}</p>
                        <p style="margin: 0; color: #888; font-size: 0.8em; margin-top: 5px;">⏳ {txt_dias}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Calendário
        st.markdown("<h4 style='text-align: center; margin-bottom: 17px; color: #4a3b8c;'>Calendário das tarefas</h4>", unsafe_allow_html=True)
        
        hoje_cal = date.today()
        if 'cal_month' not in st.session_state:
            st.session_state.cal_month = hoje_cal.month
        if 'cal_year' not in st.session_state:
            st.session_state.cal_year = hoje_cal.year
            
        col_prev, col_title, col_next = st.columns([1, 5, 1])
        with col_prev:
            if st.button("◀", key="btn_prev_month", use_container_width=True):
                st.session_state.cal_month -= 1
                if st.session_state.cal_month < 1:
                    st.session_state.cal_month = 12
                    st.session_state.cal_year -= 1
                st.rerun()
        with col_title:
            meses_pt = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 1.1em; padding-top: 5px;'>{meses_pt[st.session_state.cal_month]} {st.session_state.cal_year}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("▶", key="btn_next_month", use_container_width=True):
                st.session_state.cal_month += 1
                if st.session_state.cal_month > 12:
                    st.session_state.cal_month = 1
                    st.session_state.cal_year += 1
                st.rerun()
                
        cal_html = get_custom_calendar(st.session_state.cal_year, st.session_state.cal_month, task_dict)
        st.markdown(cal_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Upcoming Events
        st.subheader("Próximas Tarefas")
        if upcoming_tasks:
            for task in upcoming_tasks[:4]: # Mostrar as 4 próximas
                c_name = map_cursos.get(task.get('curso_id'), "S/ Curso")
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #6c5ce7; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <p style="margin: 0; font-weight: bold; color: #333; font-size: 0.95em;">{task.get('nome')}</p>
                    <p style="margin: 0; color: #888; font-size: 0.8em; margin-top: 5px;">📅 {task['parsed_date'].strftime('%d/%m/%Y')} | 🎓 {c_name}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #888; font-size: 0.9em;'>Nenhuma tarefa próxima pendente.</p>", unsafe_allow_html=True)

modulo_dashboard()

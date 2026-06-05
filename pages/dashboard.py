import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
from datetime import datetime, date
import calendar
from utils.api import api_get

def get_custom_calendar(year, month, task_dates):
    cal = calendar.monthcalendar(year, month)
    
    meses_pt = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    month_name = meses_pt[month]
    
    html = f"""
    <style>
    .cal-container {{
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
    }}
    .cal-header {{
        text-align: center;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 10px;
        color: #333;
    }}
    .cal-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .cal-table th {{
        color: #888;
        font-weight: normal;
        font-size: 0.85em;
        padding-bottom: 8px;
    }}
    .cal-table td {{
        text-align: center;
        padding: 6px 0;
        font-size: 0.9em;
        color: #555;
    }}
    .cal-day.active {{
        background-color: #6c5ce7;
        color: white;
        border-radius: 50%;
        font-weight: bold;
        display: inline-block;
        width: 28px;
        height: 28px;
        line-height: 28px;
    }}
    .cal-day.has-task {{
        border: 2px solid #6c5ce7;
        color: #6c5ce7;
        border-radius: 50%;
        font-weight: bold;
        display: inline-block;
        width: 28px;
        height: 28px;
        line-height: 24px;
        background-color: #f3f0ff;
    }}
    .cal-day.active.has-task {{
        border: 2px solid #4a3b8c;
        background-color: #6c5ce7;
        color: white;
    }}
    </style>
    <div class="cal-container">
        <div class="cal-header">{month_name} {year}</div>
        <table class="cal-table">
            <tr><th>Dom</th><th>Seg</th><th>Ter</th><th>Qua</th><th>Qui</th><th>Sex</th><th>Sáb</th></tr>
    """
    
    today = date.today()
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            else:
                current_date = date(year, month, day)
                classes = "cal-day"
                if current_date == today:
                    classes += " active"
                if current_date in task_dates:
                    classes += " has-task"
                
                html += f'<td><span class="{classes}">{day}</span></td>'
        html += "</tr>"
    html += "</table></div>"
    
    return html

def modulo_dashboard():
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

    # Processar métricas
    num_discs = len(discs) if discs else 0
    concluidas = len([t for t in tarefas if t.get('status') == 'Concluída']) if tarefas else 0
    pendentes = len([t for t in tarefas if t.get('status') == 'Para Entregar']) if tarefas else 0
    
    # Processar datas
    task_dates = []
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
                    task_dates.append(dt)
                    
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
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Disciplinas Ativas</p>
                <h2 style="color: #4a3b8c; margin: 0;">{num_discs}</h2>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <p style="color: #888; font-size: 0.9em; margin-bottom: 5px;">Tarefas Concluídas</p>
                <h2 style="color: #27ae60; margin: 0;">{concluidas}</h2>
            </div>
            """, unsafe_allow_html=True)
        with c3:
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
            
            # Filtrar para exibir apenas as tarefas com status "Concluída" no gráfico
            if 'status' in df_plot.columns:
                df_plot = df_plot[df_plot['status'] == 'Concluída']
                
            if not df_plot.empty:
                # Opções de visualização para o usuário (Tipo e Ordem)
                col_chart_type, col_sort = st.columns(2)
                with col_chart_type:
                    tipo_grafico = st.selectbox("Escolha o tipo de gráfico", ["Linha", "Barra", "Dispersão"])
                with col_sort:
                    ordem_grafico = st.selectbox("Ordem de Exibição", ["Cronológica", "Alfabética"])
                
                # Ordenar o dataframe com base na escolha
                if ordem_grafico == "Cronológica":
                    df_plot = df_plot.sort_values(by='id_t')
                else:
                    df_plot = df_plot.sort_values(by='nome_t')
                
                if tipo_grafico == "Linha":
                    fig = px.line(df_plot, x='nome_t', y='nota', color='nome_d', markers=True)
                elif tipo_grafico == "Barra":
                    fig = px.bar(df_plot, x='nome_t', y='nota', color='nome_d', barmode='group')
                elif tipo_grafico == "Dispersão":
                    fig = px.scatter(df_plot, x='nome_t', y='nota', color='nome_d', size='nota')
                
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="",
                    yaxis_title="Nota",
                    legend_title="",
                    margin=dict(l=0, r=0, t=20, b=0),
                    yaxis=dict(gridcolor='#eee', range=[0, 10])
                )
                if tipo_grafico == "Linha":
                    fig.update_traces(line=dict(width=3), marker=dict(size=8))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Cadastre notas nas atividades concluídas para visualizar o gráfico.")
        else:
            st.info("Cadastre dados para visualizar seu desempenho gráfico.")

    with col_side:
        # Card do Perfil do Usuário
        if profile:
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()

            if full_name:
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px;">
                    <h4 style="color: #333; margin: 0;">{full_name}</h4>
                </div>
                """, unsafe_allow_html=True)

        # Calendário
        st.subheader("Calendário")
        today = datetime.today()
        cal_html = get_custom_calendar(today.year, today.month, task_dates)
        st.markdown(cal_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Upcoming Events
        st.subheader("Próximas Tarefas")
        if upcoming_tasks:
            for task in upcoming_tasks[:4]: # Mostrar as 4 próximas
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #6c5ce7; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <p style="margin: 0; font-weight: bold; color: #333; font-size: 0.95em;">{task.get('nome')}</p>
                    <p style="margin: 0; color: #888; font-size: 0.8em; margin-top: 5px;">📅 {task['parsed_date'].strftime('%d/%m/%Y')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: #888; font-size: 0.9em;'>Nenhuma tarefa próxima pendente.</p>", unsafe_allow_html=True)

modulo_dashboard()

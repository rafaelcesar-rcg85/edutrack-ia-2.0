import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api import api_get

def modulo_dashboard():
    st.header('Resumo de Desempenho')
    tarefas = api_get('tarefas')
    discs = api_get('disciplinas')
    if not tarefas or not discs:
        st.info('Cadastre dados para visualizar seu desempenho gráfico.')
        return

    df_t = pd.DataFrame(tarefas)
    df_d = pd.DataFrame(discs)
    df_plot = df_t.merge(df_d, left_on='disc_id', right_on='id', suffixes=('_t', '_d'))
    
    if df_plot.empty:
        st.info('Nenhuma nota associada a uma disciplina ainda.')
        return

    fig = px.bar(df_plot, x='nome_t', y='nota', color='nome_d', 
                 title='Minhas Notas por Matéria', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

modulo_dashboard()

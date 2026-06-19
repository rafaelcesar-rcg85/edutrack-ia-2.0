import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import datetime
import requests
from utils.api import api_get, BASE_URL, USER_PROFILES_URL
from utils.theme import apply_theme

def calcular_media_disciplina(disc_id, df_tarefas, disc_info):
    """
    Calcula a média final ponderada de uma disciplina com base na fórmula:
    MF = (MAP * peso_map + PROVA_FINAL * peso_prova + PAI * peso_pai) / 100
    Se alguma categoria estiver sem notas, os pesos são redistribuídos proporcionalmente.
    """
    p_map = int(disc_info.get('peso_map') if disc_info.get('peso_map') is not None else 30)
    p_prova = int(disc_info.get('peso_prova') if disc_info.get('peso_prova') is not None else 50)
    p_pai = int(disc_info.get('peso_pai') if disc_info.get('peso_pai') is not None else 20)
    
    if df_tarefas.empty:
        return None, {}
        
    df_disc = df_tarefas[(df_tarefas['disc_id'] == disc_id) & (df_tarefas['status'] == 'Concluída')]
    if df_disc.empty:
        return None, {}
        
    notas_por_tipo = {}
    for _, row in df_disc.iterrows():
        t = str(row.get('tipo') or 'OUTRO').upper()
        nota = row.get('nota')
        if nota is not None and not pd.isna(nota):
            if t not in notas_por_tipo:
                notas_por_tipo[t] = []
            notas_por_tipo[t].append(float(nota))
            
    map_grades = notas_por_tipo.get('MAP', [])
    map_avg = sum(map_grades) / len(map_grades) if map_grades else None
    
    prova_grades = notas_por_tipo.get('PROVA', [])
    sub_grades = notas_por_tipo.get('SUB', [])
    
    prova_val = prova_grades[0] if prova_grades else None
    sub_val = sub_grades[0] if sub_grades else None
    
    prova_final_val = None
    if prova_val is not None and sub_val is not None:
        prova_final_val = max(prova_val, sub_val)
    elif prova_val is not None:
        prova_final_val = prova_val
    elif sub_val is not None:
        prova_final_val = sub_val
        
    pai_grades = notas_por_tipo.get('PAI', [])
    pai_val = pai_grades[0] if pai_grades else None
    
    pesos_ativos = []
    notas_ativas = []
    
    if map_avg is not None:
        pesos_ativos.append(p_map)
        notas_ativas.append(map_avg * p_map)
    if prova_final_val is not None:
        pesos_ativos.append(p_prova)
        notas_ativas.append(prova_final_val * p_prova)
    if pai_val is not None:
        pesos_ativos.append(p_pai)
        notas_ativas.append(pai_val * p_pai)
        
    soma_pesos = sum(pesos_ativos)
    if soma_pesos == 0:
        return None, {}
        
    mf = sum(notas_ativas) / soma_pesos
    
    detalhes = {
        'map_grades': map_grades,
        'map_avg': map_avg,
        'prova_original': prova_val,
        'sub_grade': sub_val,
        'prova_final': prova_final_val,
        'pai_grade': pai_val,
        'peso_map': p_map,
        'peso_prova': p_prova,
        'peso_pai': p_pai,
        'mf': mf,
        'soma_pesos': soma_pesos
    }
    return mf, detalhes

def get_situacao_freq(faltas_count, limite):
    if limite is None or limite == 0:
        return "⚪", "Limite não configurado", "#888888"
    if faltas_count >= limite:
        return "🔴", "Reprovado por Faltas", "#e74c3c"
    if faltas_count >= limite * 0.75:
        return "🟡", "Atenção — próximo do limite", "#f39c12"
    return "🟢", "Frequência Regular", "#27ae60"

def gerar_pdf_bytes(student_full_name, user_email, dob_str, media_geral, taxa_conclusao, num_tarefas, num_disciplinas, disciplinas, tarefas, professores, todas_faltas, df_filtrado_raw, cursos):
    from fpdf import FPDF
    import os
    import unicodedata
    import datetime
    
    def clean_text(text):
        if not text:
            return ""
        return "".join(
            c for c in unicodedata.normalize('NFD', str(text))
            if unicodedata.category(c) != 'Mn'
        )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Tenta carregar Arial Unicode do Windows, caso contrário usa Helvetica
    unicode_mode = False
    font_path = "C:\\Windows\\Fonts\\arial.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\arialbd.ttf"
    if os.path.exists(font_path) and os.path.exists(font_bold_path):
        try:
            pdf.add_font("Arial", "", font_path)
            pdf.add_font("Arial", "B", font_bold_path)
            pdf.set_font("Arial", size=10)
            unicode_mode = True
        except:
            pass
            
    if not unicode_mode:
        pdf.set_font("helvetica", size=10)
        
    def txt(s):
        if not unicode_mode:
            return clean_text(s)
        return str(s)

    # 1. HEADER BANNER
    pdf.set_fill_color(108, 92, 231) # #6c5ce7 -> RGB 108, 92, 231
    pdf.rect(0, 0, 210, 38, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 18)
    pdf.set_y(10)
    pdf.cell(0, 8, txt("EduTrack AI - Relatório Acadêmico"), ln=True, align="C")
    
    pdf.set_font("Arial" if unicode_mode else "helvetica", "", 10)
    pdf.cell(0, 6, txt(f"Gerado em: {datetime.date.today().strftime('%d/%m/%Y')}"), ln=True, align="C")
    pdf.ln(18)
    
    # 2. STUDENT INFO
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 12)
    pdf.cell(0, 8, txt("Informações do Estudante"), ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_font("Arial" if unicode_mode else "helvetica", "", 10)
    pdf.cell(90, 6, txt(f"Nome: {student_full_name}"), ln=False)
    pdf.cell(90, 6, txt(f"E-mail: {user_email or 'Não informado'}"), ln=True)
    pdf.cell(90, 6, txt(f"Nascimento: {dob_str}"), ln=True)
    pdf.ln(6)
    
    # 3. KPI CARDS
    pdf.set_fill_color(245, 245, 247)
    pdf.set_draw_color(220, 220, 220)
    
    w_card = 41.25
    h_card = 22
    y_start = pdf.get_y()
    
    # Card 1: Média Geral
    x1 = 15
    pdf.rect(x1, y_start, w_card, h_card, 'FD')
    pdf.set_xy(x1, y_start + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(w_card, 5, txt("MÉDIA GERAL"), align="C")
    pdf.set_xy(x1, y_start + 8)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 14)
    pdf.set_text_color(108, 92, 231)
    pdf.cell(w_card, 10, f"{media_geral:.2f}", align="C")
    
    # Card 2: Taxa de Conclusão
    x2 = 15 + w_card + 5
    pdf.rect(x2, y_start, w_card, h_card, 'FD')
    pdf.set_xy(x2, y_start + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(w_card, 5, txt("CONCLUSÃO"), align="C")
    pdf.set_xy(x2, y_start + 8)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 14)
    pdf.set_text_color(39, 174, 96)
    pdf.cell(w_card, 10, f"{taxa_conclusao:.1f}%", align="C")
    
    # Card 3: Atividades
    x3 = 15 + 2*w_card + 10
    pdf.rect(x3, y_start, w_card, h_card, 'FD')
    pdf.set_xy(x3, y_start + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(w_card, 5, txt("ATIVIDADES"), align="C")
    pdf.set_xy(x3, y_start + 8)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 14)
    pdf.set_text_color(230, 126, 34)
    pdf.cell(w_card, 10, f"{num_tarefas}", align="C")
    
    # Card 4: Disciplinas
    x4 = 15 + 3*w_card + 15
    pdf.rect(x4, y_start, w_card, h_card, 'FD')
    pdf.set_xy(x4, y_start + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(w_card, 5, txt("DISCIPLINAS"), align="C")
    pdf.set_xy(x4, y_start + 8)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 14)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(w_card, 10, f"{num_disciplinas}", align="C")
    
    pdf.set_xy(15, y_start + h_card + 8)
    
    # 4. BOLETIM DETALHADO TABLE
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 12)
    pdf.cell(0, 8, txt("Boletim Acadêmico Detalhado"), ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.cell(50, 8, txt("Disciplina"), border=1, fill=True)
    pdf.cell(15, 8, txt("MAP"), border=1, fill=True, align="C")
    pdf.cell(15, 8, txt("Prova"), border=1, fill=True, align="C")
    pdf.cell(15, 8, txt("PAI"), border=1, fill=True, align="C")
    pdf.cell(20, 8, txt("Faltas"), border=1, fill=True, align="C")
    pdf.cell(45, 8, txt("Cálculo Ponderado"), border=1, fill=True, align="C")
    pdf.cell(20, 8, txt("Média Final"), border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Arial" if unicode_mode else "helvetica", "", 8)
    if disciplinas:
        df_t_raw = pd.DataFrame(tarefas) if tarefas else pd.DataFrame()
        map_c = {c['id']: c.get('curso', c.get('name', 'Sem Curso')) for c in (cursos or [])}
        
        for d in disciplinas:
            mf, det = calcular_media_disciplina(d['id'], df_t_raw, d)
            c_nome = map_c.get(d.get('curso_id') or d.get('course_id'), 'Sem Curso')
            
            faltas_disc = [f for f in todas_faltas if f.get("disc_id") == d['id']] if todas_faltas else []
            total_faltas = sum(f.get("peso") or 1 for f in faltas_disc)
            limite_faltas = d.get('limite_faltas') or 0
            limite_txt = f"/{limite_faltas}" if limite_faltas > 0 else ""
            
            map_str = f"{det['map_avg']:.1f}" if det and det.get('map_avg') is not None else "-"
            prova_str = f"{det['prova_final']:.1f}" if det and det.get('prova_final') is not None else "-"
            pai_str = f"{det['pai_grade']:.1f}" if det and det.get('pai_grade') is not None else "-"
            
            formula = "-"
            if det:
                parts = []
                if det['map_avg'] is not None:
                    parts.append(f"({det['map_avg']:.1f}x{det['peso_map']})")
                if det['prova_final'] is not None:
                    parts.append(f"({det['prova_final']:.1f}x{det['peso_prova']})")
                if det['pai_grade'] is not None:
                    parts.append(f"({det['pai_grade']:.1f}x{det['peso_pai']})")
                formula = " + ".join(parts) + f" / {det['soma_pesos']}"
            
            mf_str = f"{mf:.2f}" if mf is not None else "-"
            
            pdf.cell(50, 8, txt(d['nome']), border=1)
            pdf.cell(15, 8, map_str, border=1, align="C")
            pdf.cell(15, 8, prova_str, border=1, align="C")
            pdf.cell(15, 8, pai_str, border=1, align="C")
            pdf.cell(20, 8, f"{total_faltas}{limite_txt}", border=1, align="C")
            pdf.cell(45, 8, txt(formula), border=1, align="C")
            pdf.cell(20, 8, mf_str, border=1, align="C")
            pdf.ln()
    else:
        pdf.cell(180, 8, txt("Nenhum boletim disponível."), border=1, align="C")
        pdf.ln()
    pdf.ln(5)

    # 4.5 GRÁFICOS DE ACOMPANHAMENTO (PDF)
    if pdf.get_y() > 210:
        pdf.add_page()
        
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 12)
    pdf.cell(0, 8, txt("Gráficos de Acompanhamento"), ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    y_charts = pdf.get_y()
    
    # Calcular contagens de status
    num_concluidas = len([t for t in tarefas if t.get('status') == 'Concluída']) if tarefas else 0
    num_pendentes = len([t for t in tarefas if t.get('status') == 'Para Entregar']) if tarefas else 0
    
    # Container para o Gráfico de Barras: Média Final por Disciplina (x: 15 a 100)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, y_charts, 85, 45, 'D')
    
    pdf.set_xy(15, y_charts + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(108, 92, 231)
    pdf.cell(85, 4, txt("Média Final por Disciplina"), align="C", ln=True)
    
    # Coletar médias para desenhar
    medias_pdf_disc = []
    if disciplinas and tarefas:
        df_t_pdf = pd.DataFrame(tarefas)
        for d in disciplinas:
            mf, _ = calcular_media_disciplina(d['id'], df_t_pdf, d)
            if mf is not None:
                medias_pdf_disc.append((d['nome'], mf))
                
    if medias_pdf_disc:
        y_axis_base = y_charts + 38
        max_bar_height = 28.0
        num_bars = len(medias_pdf_disc)
        bar_width = min(12.0, 50.0 / max(1, num_bars))
        spacing = 65.0 / max(1, num_bars)
        
        pdf.set_draw_color(180, 180, 180)
        pdf.line(20, y_axis_base, 95, y_axis_base) # Eixo X
        
        for idx, (d_nome, grade) in enumerate(medias_pdf_disc[:6]): # Limitar a 6
            x_bar = 22 + idx * spacing
            h_bar = (grade / 10.0) * max_bar_height
            
            # Desenhar barra
            pdf.set_fill_color(108, 92, 231)
            pdf.rect(x_bar, y_axis_base - h_bar, bar_width, h_bar, 'F')
            
            # Texto da nota no topo
            pdf.set_xy(x_bar - 2, y_axis_base - h_bar - 3.5)
            pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 6)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(bar_width + 4, 3, f"{grade:.1f}", align="C")
            
            # Texto do nome abaixo
            pdf.set_xy(x_bar - 4, y_axis_base + 1)
            pdf.set_font("Arial" if unicode_mode else "helvetica", "", 5)
            d_short = (d_nome[:8] + '..') if len(d_nome) > 9 else d_nome
            pdf.cell(bar_width + 8, 3, txt(d_short), align="C")
    else:
        pdf.set_xy(15, y_charts + 20)
        pdf.set_font("Arial" if unicode_mode else "helvetica", "", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(85, 5, txt("Sem médias disponíveis"), align="C")
        
    # Container para Distribuição de Status de Tarefas (x: 105 a 195)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(105, y_charts, 90, 45, 'D')
    
    pdf.set_xy(105, y_charts + 2)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.set_text_color(39, 174, 96)
    pdf.cell(90, 4, txt("Distribuição de Status de Tarefas"), align="C", ln=True)
    
    # Desenhar barra de progresso horizontal
    if num_tarefas > 0:
        pct_concluidas = (num_concluidas / num_tarefas) * 100
        
        # Barra base (Para Entregar / Laranja)
        pdf.set_fill_color(230, 126, 34)
        pdf.rect(115, y_charts + 15, 70, 8, 'F')
        
        # Barra sobreposta (Concluída / Verde)
        if pct_concluidas > 0:
            w_green = 70.0 * (pct_concluidas / 100.0)
            pdf.set_fill_color(39, 174, 96)
            pdf.rect(115, y_charts + 15, w_green, 8, 'F')
            
        # Legenda e porcentagem
        pdf.set_xy(115, y_charts + 26)
        pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 7)
        pdf.set_text_color(39, 174, 96)
        pdf.cell(35, 4, txt(f"Concluídas: {num_concluidas} ({pct_concluidas:.1f}%)"))
        
        pdf.set_xy(150, y_charts + 26)
        pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 7)
        pdf.set_text_color(230, 126, 34)
        pct_pend = 100.0 - pct_concluidas
        pdf.cell(35, 4, txt(f"Para Entregar: {num_pendentes} ({pct_pend:.1f}%)"), align="R")
        
        # Texto Informativo
        pdf.set_xy(115, y_charts + 34)
        pdf.set_font("Arial" if unicode_mode else "helvetica", "", 7)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(70, 4, txt(f"Total de {num_tarefas} atividades registradas no curso."), align="C")
    else:
        pdf.set_xy(105, y_charts + 20)
        pdf.set_font("Arial" if unicode_mode else "helvetica", "", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(90, 5, txt("Sem atividades registradas"), align="C")
        
    pdf.set_xy(15, y_charts + 50)
    pdf.ln(5)

    # 5. TAREFAS HISTORICO TABLE
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 12)
    pdf.cell(0, 8, txt("Histórico de Tarefas, Atividades e Notas"), ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.cell(50, 8, txt("Atividade"), border=1, fill=True)
    pdf.cell(45, 8, txt("Curso"), border=1, fill=True)
    pdf.cell(45, 8, txt("Disciplina"), border=1, fill=True)
    pdf.cell(15, 8, txt("Status"), border=1, fill=True, align="C")
    pdf.cell(15, 8, txt("Prazo"), border=1, fill=True, align="C")
    pdf.cell(10, 8, txt("Nota"), border=1, fill=True, align="C")
    pdf.ln()
    
    pdf.set_font("Arial" if unicode_mode else "helvetica", "", 7)
    if df_filtrado_raw is not None and not df_filtrado_raw.empty:
        for _, row in df_filtrado_raw.iterrows():
            nome_t = row.get('nome', '-')
            curso_n = row.get('nome_curso', '-')
            disc_n = row.get('nome_disc', '-')
            status_t = row.get('status', '-')
            
            d_val = row.get('data_entrega')
            prazo = "-"
            if d_val:
                try:
                    dt = datetime.datetime.fromisoformat(str(d_val).split('T')[0])
                    if dt.year > 1970:
                        prazo = dt.strftime('%d/%m/%Y')
                except:
                    pass
                    
            nota_val = row.get('nota')
            nota_desc = f"{float(nota_val):.1f}" if nota_val is not None and not pd.isna(nota_val) else "-"
            
            nome_t = (nome_t[:28] + '...') if len(str(nome_t)) > 30 else nome_t
            curso_n = (curso_n[:25] + '...') if len(str(curso_n)) > 27 else curso_n
            disc_n = (disc_n[:25] + '...') if len(str(disc_n)) > 27 else disc_n
            
            pdf.cell(50, 6, txt(nome_t), border=1)
            pdf.cell(45, 6, txt(curso_n), border=1)
            pdf.cell(45, 6, txt(disc_n), border=1)
            pdf.cell(15, 6, txt(status_t), border=1, align="C")
            pdf.cell(15, 6, prazo, border=1, align="C")
            pdf.cell(10, 6, nota_desc, border=1, align="C")
            pdf.ln()
    else:
        pdf.cell(180, 8, txt("Nenhuma atividade filtrada."), border=1, align="C")
        pdf.ln()
    pdf.ln(5)
    
    # 6. DOCENTES & CONTATOS
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 12)
    pdf.cell(0, 8, txt("Disciplinas, Professores & Contatos"), ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    
    # Cabeçalho Docentes
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial" if unicode_mode else "helvetica", "B", 8)
    pdf.cell(55, 8, txt("Disciplina"), border=1, fill=True)
    pdf.cell(60, 8, txt("Professor"), border=1, fill=True)
    pdf.cell(65, 8, txt("E-mail de Contato"), border=1, fill=True)
    pdf.ln()
    
    pdf.set_font("Arial" if unicode_mode else "helvetica", "", 8)
    if disciplinas:
        df_d = pd.DataFrame(disciplinas)
        df_p = pd.DataFrame(professores) if professores else pd.DataFrame()
        df_c = pd.DataFrame(cursos) if cursos else pd.DataFrame()
        
        if not df_p.empty:
            df_merged_d = df_d.merge(df_p[['id', 'nome', 'email']], left_on='prof_id', right_on='id', how='left', suffixes=('', '_prof'))
            df_merged_d['nome_prof'] = df_merged_d['nome_prof'].fillna('N/A')
            df_merged_d['email_prof'] = df_merged_d['email'].fillna('Nao informado')
        else:
            df_merged_d = df_d.copy()
            df_merged_d['nome_prof'] = 'N/A'
            df_merged_d['email_prof'] = 'Nao informado'
            
        for _, row in df_merged_d.iterrows():
            d_nome = row.get('nome', '-')
            p_nome = row.get('nome_prof', '-')
            p_email = row.get('email_prof', '-')
            
            pdf.cell(55, 7, txt(d_nome), border=1)
            pdf.cell(60, 7, txt(p_nome), border=1)
            pdf.cell(65, 7, txt(p_email), border=1)
            pdf.ln()
    else:
        pdf.cell(180, 8, txt("Nenhuma disciplina ou professor cadastrado."), border=1, align="C")
        pdf.ln()
    pdf.ln(5)

    # 7. FOOTER SYSTEM SIGNATURE
    pdf.set_font("Arial" if unicode_mode else "helvetica", "I", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 10, txt("EduTrack AI - Relatorio Academico. Gerado automaticamente pelo sistema."), align="C")
    
    return bytes(pdf.output())

def modulo_relatorios():
    apply_theme()
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
    professores = api_get('professores') or []
    disciplinas = api_get('disciplinas') or []
    tarefas = api_get('tarefas') or []
    cursos = api_get('curso') or []
    todas_faltas = api_get('faltas') or []
    
    if cursos:
        for c in cursos:
            c['curso'] = c.get('curso', c.get('name', 'Sem Nome'))

    # Se não houver disciplinas, professores ou cursos, orientar o usuário
    if not professores and not disciplinas and not tarefas and not cursos:
        st.info("Ainda não há dados registrados para gerar o relatório. Cadastre cursos, disciplinas e tarefas para começar!")
        return

    # Filtro Global de Curso no começo da página
    opcoes_cursos_filtro = ["Todos os Cursos"]
    if cursos:
        opcoes_cursos_filtro += sorted(list(set(c.get('curso', c.get('name', 'Sem Nome')) for c in cursos)))
        
    filtro_curso_global = st.selectbox("🎯 Filtrar Relatório por Curso", options=opcoes_cursos_filtro, key="filtro_relatorio_curso_global")
    
    # Aplicar filtro aos dados
    if filtro_curso_global != "Todos os Cursos":
        selected_curso_id = None
        for c in cursos:
            if c.get('curso') == filtro_curso_global:
                selected_curso_id = c['id']
                break
                
        if selected_curso_id is not None:
            cursos = [c for c in cursos if c['id'] == selected_curso_id]
            disciplinas = [d for d in disciplinas if (d.get('curso_id') == selected_curso_id or d.get('course_id') == selected_curso_id)]
            disc_ids = {d['id'] for d in disciplinas}
            tarefas = [t for t in tarefas if (t.get('curso_id') == selected_curso_id or t.get('course_id') == selected_curso_id or t.get('disc_id') in disc_ids)]
            todas_faltas = [f for f in todas_faltas if (f.get('course_id') == selected_curso_id or f.get('curso_id') == selected_curso_id or f.get('disc_id') in disc_ids)]
            prof_ids = {d.get('prof_id') for d in disciplinas if d.get('prof_id')}
            professores = [p for p in professores if p['id'] in prof_ids]

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
    
    # Calcular média geral com base nas médias finais ponderadas das disciplinas
    df_t_raw = pd.DataFrame(tarefas) if tarefas else pd.DataFrame()
    medias_validas = []
    if disciplinas and not df_t_raw.empty:
        for d in disciplinas:
            mf, det = calcular_media_disciplina(d['id'], df_t_raw, d)
            if mf is not None:
                medias_validas.append(mf)
    media_geral = sum(medias_validas) / len(medias_validas) if medias_validas else 0.0

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
    # Gráfico de Desempenho por Disciplina (Linha 1)
    if tarefas and disciplinas:
        df_t = pd.DataFrame(tarefas)
        
        # Calcular média final ponderada por disciplina
        medias_disciplinas = []
        for d in disciplinas:
            mf, _ = calcular_media_disciplina(d['id'], df_t, d)
            if mf is not None:
                medias_disciplinas.append({
                    'Disciplina': d['nome'],
                    'Média de Notas': round(mf, 2)
                })
        df_media_disc = pd.DataFrame(medias_disciplinas)
        
        if not df_media_disc.empty:
            disciplinas_list = df_media_disc['Disciplina'].tolist()
            medias_list = df_media_disc['Média de Notas'].tolist()
            
            bar_options = {
                "title": {
                    "text": "Média Final Ponderada por Disciplina",
                    "left": "center",
                    "textStyle": {"fontSize": 14, "color": "#4a3b8c"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"}
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "top": "15%",
                    "bottom": "10%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": disciplinas_list,
                    "axisLabel": {
                        "interval": 0,
                        "rotate": 15 if len(disciplinas_list) > 4 else 0
                    }
                },
                "yAxis": {
                    "type": "value",
                    "min": 0,
                    "max": 10,
                    "splitLine": {
                        "lineStyle": {
                            "type": "dashed",
                            "color": "#eee"
                        }
                    }
                },
                "series": [
                    {
                        "name": "Média",
                        "type": "bar",
                        "color": "#6c5ce7",
                        "barWidth": "40%",
                        "itemStyle": {
                            "borderRadius": [4, 4, 0, 0]
                        },
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}"
                        },
                        "data": medias_list
                    }
                ]
            }
            st_echarts(options=bar_options, height="350px", theme="streamlit", key="relatorio_media_disciplina_bar")
        else:
            st.info("Registre atividades concluídas com notas para gerar o gráfico de desempenho por disciplina.")
    else:
        st.info("Informações insuficientes para gerar o gráfico de barras.")

    st.markdown("<br><hr style='margin: 20px 0; border: 0; border-top: 1px dashed #eee;'><br>", unsafe_allow_html=True)

    # Distribuição de Status de Tarefas (Linha 2)
    if tarefas:
        concluidas_count = len([t for t in tarefas if t.get('status') == 'Concluída'])
        pendentes_count = len([t for t in tarefas if t.get('status') == 'Para Entregar'])
        
        if concluidas_count + pendentes_count > 0:
            pie_options = {
                "title": {
                    "text": "Distribuição de Status de Tarefas",
                    "left": "center",
                    "textStyle": {"fontSize": 14, "color": "#4a3b8c"}
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}: {c} ({d}%)"
                },
                "legend": {
                    "orient": "horizontal",
                    "bottom": "bottom"
                },
                "series": [
                    {
                        "name": "Status",
                        "type": "pie",
                        "radius": ["50%", "70%"],
                        "avoidLabelOverlap": False,
                        "itemStyle": {
                            "borderRadius": 8,
                            "borderColor": "#fff",
                            "borderWidth": 2
                        },
                        "label": {
                            "show": True,
                            "position": "outside",
                            "formatter": "{b}: {c} ({d}%)"
                        },
                        "emphasis": {
                            "label": {
                                "show": True,
                                "fontSize": "14",
                                "fontWeight": "bold"
                            }
                        },
                        "color": ["#27ae60", "#e67e22"],
                        "data": [
                            {"value": concluidas_count, "name": "Concluídas"},
                            {"value": pendentes_count, "name": "Para Entregar"}
                        ]
                    }
                ]
            }
            st_echarts(options=pie_options, height="350px", theme="streamlit", key="relatorio_status_tarefas_pie")
        else:
            st.info("Nenhuma tarefa para exibir a distribuição de status.")
    else:
        st.info("Registre tarefas para visualizar a distribuição de status.")

    st.markdown("<br><hr style='margin: 20px 0; border: 0; border-top: 1px dashed #eee;'><br>", unsafe_allow_html=True)

    # --- Novo Gráfico: Crescimento de Atividades Concluídas (Área Acumulativa) ---
    if tarefas:
        st.markdown("<h5 style='color: #4a3b8c; margin-top: 25px; text-align: center;'>Crescimento de Atividades Concluídas</h5>", unsafe_allow_html=True)
        
        # Processar dados cronologicamente
        concluidas_tasks = []
        for t in tarefas:
            if t.get('status') == 'Concluída' and t.get('data_entrega'):
                d_str = t.get('data_entrega')
                try:
                    if isinstance(d_str, int):
                        dt = datetime.datetime.fromtimestamp(d_str/1000.0).date()
                    else:
                        dt = datetime.datetime.fromisoformat(str(d_str).split('T')[0]).date()
                    if dt.year > 1970:
                        concluidas_tasks.append(dt)
                except:
                    pass
        
        if concluidas_tasks:
            # Ordenar datas
            concluidas_tasks.sort()
            
            # Contar tarefas concluidas por dia
            date_counts = {}
            for d in concluidas_tasks:
                date_counts[d] = date_counts.get(d, 0) + 1
                
            sorted_dates = sorted(date_counts.keys())
            
            # Calcular acúmulo (cumsum)
            cumulative_sum = 0
            cumulative_data = []
            x_dates = []
            
            for d in sorted_dates:
                cumulative_sum += date_counts[d]
                cumulative_data.append(cumulative_sum)
                x_dates.append(d.strftime('%d/%m/%Y'))
                
            growth_options = {
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "cross"}
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "top": "8%",
                    "bottom": "15%",
                    "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "boundaryGap": False,
                    "data": x_dates
                },
                "yAxis": {
                    "type": "value",
                    "minInterval": 1
                },
                "series": [
                    {
                        "name": "Concluídas (Total)",
                        "type": "line",
                        "smooth": True,
                        "symbolSize": 6,
                        "color": "#6c5ce7",
                        "areaStyle": {
                            "opacity": 0.2
                        },
                        "data": cumulative_data
                    }
                ]
            }
            st_echarts(options=growth_options, height="300px", theme="streamlit", key="relatorio_growth_tarefas_line")
        else:
            st.caption("Nenhuma tarefa concluída para exibir o crescimento.")

    st.markdown("<br><hr style='border-top: 1px solid #eee;'><br>", unsafe_allow_html=True)

    # 4.5 BOLETIM ACADÊMICO DETALHADO PONDERADO
    st.subheader('🎓 Boletim Acadêmico Detalhado')
    st.write('Detalhamento da Média Final (MF) de cada disciplina com base nas notas parciais e respectivos pesos.')
    
    if disciplinas and tarefas:
        df_t_calc = pd.DataFrame(tarefas)
        map_c = {c['id']: c.get('curso', c.get('name', 'Sem Curso')) for c in (cursos or [])}
        
        for d in disciplinas:
            mf, det = calcular_media_disciplina(d['id'], df_t_calc, d)
            c_nome = map_c.get(d.get('curso_id') or d.get('course_id'), 'Sem Curso')
            
            # Calcular faltas da disciplina
            faltas_disc = [f for f in todas_faltas if f.get("disc_id") == d['id']] if todas_faltas else []
            total_faltas = sum(f.get("peso") or 1 for f in faltas_disc)
            limite_faltas = d.get('limite_faltas') or 0
            limite_texto = f" / {limite_faltas}" if limite_faltas > 0 else ""
            
            with st.container():
                border_color = "#27ae60" if (mf is not None and mf >= 6.0) else ("#e74c3c" if mf is not None else "#ccc")
                bg_color = "#f4fcf7" if (mf is not None and mf >= 6.0) else ("#fdf5f5" if mf is not None else "#fafafa")
                status_text = "🟢 Aprovado" if (mf is not None and mf >= 6.0) else ("🔴 Reprovado" if mf is not None else "⏳ Em andamento")
                
                st.markdown(f"""
                <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-left: 6px solid {border_color}; padding: 18px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <h4 style="margin: 0; color: #333;">{d['nome']}</h4>
                            <p style="margin: 0; color: #777; font-size: 0.85em;">🎓 Curso: {c_nome}</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.85em; font-weight: bold; color: {border_color}; padding: 3px 8px; border-radius: 9999px; background-color: {border_color}1a;">{status_text}</span>
                            <h3 style="margin: 5px 0 0 0; color: #333;">MF: {f"{mf:.2f}" if mf is not None else "N/A"}</h3>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibe os cards de frequência para cada disciplina
                t_theme = st.session_state.get("theme", {})
                primary = t_theme.get("primary", "#6c5ce7")
                total_aulas = d.get("total_aulas") or 0
                total_presencas = max(0, total_aulas - total_faltas) if total_aulas > 0 else None
                pct_presenca = (total_presencas / total_aulas * 100) if total_aulas > 0 else None
                valor_pct = f"{pct_presenca:.1f}%" if pct_presenca is not None else "—"
                icone_f, label_f, cor_f = get_situacao_freq(total_faltas, limite_faltas if limite_faltas > 0 else None)
                lim_texto = str(limite_faltas) if limite_faltas > 0 else "—"
                
                fc1, fc2, fc3, fc4 = st.columns(4)
                with fc1:
                    st.markdown(
                        f"""<div style='background: {primary}18; border: 1px solid {primary}44;
                            border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;'>
                            <p style='font-size: 13px; color: #888; margin: 0;'>Total de Aulas</p>
                            <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: {primary};'>
                                {total_aulas if total_aulas > 0 else "—"}
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )
                with fc2:
                    st.markdown(
                        f"""<div style='background: #e74c3c18; border: 1px solid #e74c3c44;
                            border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;'>
                            <p style='font-size: 13px; color: #888; margin: 0;'>Faltas Registradas</p>
                            <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: #e74c3c;'>
                                {total_faltas}
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )
                with fc3:
                    st.markdown(
                        f"""<div style='background: #27ae6018; border: 1px solid #27ae6044;
                            border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;'>
                            <p style='font-size: 13px; color: #888; margin: 0;'>% de Presença</p>
                            <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: #27ae60;'>
                                {valor_pct}
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )
                with fc4:
                    st.markdown(
                        f"""<div style='background: {cor_f}18; border: 1px solid {cor_f}55;
                            border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;'>
                            <p style='font-size: 13px; color: #888; margin: 0;'>Situação</p>
                            <p style='font-size: 18px; font-weight: 700; margin: 4px 0; color: {cor_f}; line-height: 1.25;'>
                                {icone_f} {label_f}
                            </p>
                            <p style='font-size: 11px; color: #aaa; margin: 0;'>
                                Limite: {lim_texto} faltas
                            </p>
                        </div>""",
                        unsafe_allow_html=True
                    )
                
                if det:
                    bc1, bc2, bc3 = st.columns(3)
                    with bc1:
                        st.markdown("**Composição das Notas**")
                        # MAP
                        map_lbl = ", ".join([f"{n:.1f}" for n in det['map_grades']]) if det['map_grades'] else "-"
                        st.markdown(f"**MAPs**: {map_lbl}")
                        if det['map_avg'] is not None:
                            st.markdown(f"👉 *Média MAP:* `{det['map_avg']:.2f}`")
                            
                        # Provas
                        prova_lbl = f"{det['prova_original']:.1f}" if det['prova_original'] is not None else "-"
                        sub_lbl = f"{det['sub_grade']:.1f}" if det['sub_grade'] is not None else "-"
                        st.markdown(f"**Regular**: {prova_lbl} | **SUB**: {sub_lbl}")
                        if det['prova_final'] is not None:
                            st.markdown(f"👉 *Prova Considerada:* `{det['prova_final']:.2f}`")
                            
                        # PAI
                        pai_lbl = f"{det['pai_grade']:.1f}" if det['pai_grade'] is not None else "-"
                        st.markdown(f"**PAI**: {pai_lbl}")
                        
                    with bc2:
                        st.markdown("**Configuração de Pesos**")
                        st.markdown(f"- **Peso MAP**: `{det['peso_map']}%`")
                        st.markdown(f"- **Peso Prova**: `{det['peso_prova']}%`")
                        st.markdown(f"- **Peso PAI**: `{det['peso_pai']}%`")
                        
                    with bc3:
                        st.markdown("**Cálculo Ponderado**")
                        parts = []
                        if det['map_avg'] is not None:
                            parts.append(f"({det['map_avg']:.2f} × {det['peso_map']})")
                        if det['prova_final'] is not None:
                            parts.append(f"({det['prova_final']:.2f} × {det['peso_prova']})")
                        if det['pai_grade'] is not None:
                            parts.append(f"({det['pai_grade']:.2f} × {det['peso_pai']})")
                            
                        formula_str = " + ".join(parts)
                        if formula_str:
                            st.markdown(f"`({formula_str}) / {det['soma_pesos']}`")
                            st.markdown(f"**Média Calculada:** `{det['mf']:.2f}`")
                        else:
                            st.markdown("Nenhum cálculo disponível")
                else:
                    st.info("Nenhuma nota lançada para esta disciplina.")
                st.markdown("<hr style='border-top: 1px dashed #eee; margin: 15px 0;'>", unsafe_allow_html=True)
    else:
        st.info("Cadastre disciplinas e notas para visualizar o boletim.")

    st.markdown("<br><hr style='border-top: 1px solid #eee;'><br>", unsafe_allow_html=True)

    # 5. QUADROS DETALHADOS E FILTROS
    st.subheader('📝 Quadro Geral e Filtros do Relatório')
    
    # ---------------------------------------------------------
    # PREPARAÇÃO DOS DADOS E FILTROS GLOBAIS PARA TAREFAS
    # ---------------------------------------------------------
    df_filtrado_raw = pd.DataFrame()
    if tarefas:
        df_t = pd.DataFrame(tarefas)
        df_d = pd.DataFrame(disciplinas) if disciplinas else pd.DataFrame()
        df_c = pd.DataFrame(cursos) if cursos else pd.DataFrame()
        
        # Formatação de datas e junção de disciplina e curso
        if not df_d.empty:
            df_t_view = df_t.merge(df_d[['id', 'nome']], left_on='disc_id', right_on='id', how='left', suffixes=('', '_disc'))
            df_t_view['nome_disc'] = df_t_view['nome_disc'].fillna('N/A')
        else:
            df_t_view = df_t.copy()
            df_t_view['nome_disc'] = 'N/A'

        if not df_c.empty and 'curso_id' in df_t_view.columns:
            df_t_view = df_t_view.merge(df_c[['id', 'curso']], left_on='curso_id', right_on='id', how='left', suffixes=('', '_curso_t'))
            df_t_view['nome_curso'] = df_t_view['curso'].fillna('S/ Curso')
        else:
            df_t_view['nome_curso'] = 'S/ Curso'

        st.write("🔍 **Filtros Globais para Tarefas (Tabela e Exportação)**")
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        
        with f_col1:
            curso_options = ['Todos'] + list(df_t_view['nome_curso'].unique())
            filtro_curso = st.selectbox('Curso', options=curso_options, key='filtro_curso_rep')
            
        with f_col2:
            disc_options = ['Todas'] + list(df_t_view['nome_disc'].unique())
            filtro_disc = st.selectbox('Disciplina', options=disc_options, key='filtro_disc_rep')
            
        with f_col3:
            status_options = ['Todos', 'Concluída', 'Para Entregar']
            filtro_status = st.selectbox('Status', options=status_options, key='filtro_status_rep')
            
        with f_col4:
            filtro_data_inicio = st.date_input("Data Entrega (De)", value=None, key='filtro_data_ini_rep', format="DD/MM/YYYY")
            
        with f_col5:
            filtro_data_fim = st.date_input("Data Entrega (Até)", value=None, key='filtro_data_fim_rep', format="DD/MM/YYYY")
        
        # Aplicar filtros
        df_filtrado_raw = df_t_view.copy()
        if filtro_curso != 'Todos':
            df_filtrado_raw = df_filtrado_raw[df_filtrado_raw['nome_curso'] == filtro_curso]
        if filtro_disc != 'Todas':
            df_filtrado_raw = df_filtrado_raw[df_filtrado_raw['nome_disc'] == filtro_disc]
        if filtro_status != 'Todos':
            df_filtrado_raw = df_filtrado_raw[df_filtrado_raw['status'] == filtro_status]
            
        if filtro_data_inicio and filtro_data_fim:
            def parse_date(d):
                if pd.isna(d): return None
                try:
                    if isinstance(d, int):
                        return datetime.datetime.fromtimestamp(d/1000.0).date()
                    return datetime.datetime.fromisoformat(str(d).split('T')[0]).date()
                except:
                    return None
            df_dates = df_filtrado_raw['data_entrega'].apply(parse_date)
            # handle NaT
            mask = df_dates.between(filtro_data_inicio, filtro_data_fim)
            df_filtrado_raw = df_filtrado_raw[mask.fillna(False)]

    # ---------------------------------------------------------
    # TABS DE EXIBIÇÃO
    # ---------------------------------------------------------
    tab_tarefas, tab_disciplinas, tab_professores, tab_cursos = st.tabs(['Tarefas e Notas', 'Disciplinas', 'Professores', 'Cursos'])
    
    with tab_tarefas:
        if not df_filtrado_raw.empty:
            df_filtrado_ui = df_filtrado_raw.copy()
            # Formatar a data para UI, ocultando data padrão (1970)
            def format_date_ui(d):
                if not d or pd.isna(d): return "-"
                try:
                    if isinstance(d, int):
                        dt = datetime.datetime.fromtimestamp(d/1000.0)
                    else:
                        dt = datetime.datetime.fromisoformat(str(d).split('T')[0])
                    if dt.year <= 1970:
                        return "-"
                    return dt.strftime('%d/%m/%Y')
                except:
                    return str(d)
            
            if 'data_entrega' in df_filtrado_ui.columns:
                df_filtrado_ui['data_entrega_format'] = df_filtrado_ui['data_entrega'].apply(format_date_ui)
            else:
                df_filtrado_ui['data_entrega_format'] = "-"
                
            if 'nota' not in df_filtrado_ui.columns:
                df_filtrado_ui['nota'] = "-"
            else:
                df_filtrado_ui['nota'] = df_filtrado_ui['nota'].apply(lambda x: f"{float(x):.1f}" if x is not None and not pd.isna(x) else "-")

            df_filtrado_ui = df_filtrado_ui.rename(columns={
                'nome': 'Tarefa/Atividade',
                'nome_disc': 'Disciplina',
                'nome_curso': 'Curso',
                'status': 'Status',
                'data_entrega_format': 'Prazo/Entrega',
                'nota': 'Nota'
            })
            
            cols_exibicao = ['Tarefa/Atividade', 'Curso', 'Disciplina', 'Status', 'Prazo/Entrega', 'Nota']
            cols_exibicao = [c for c in cols_exibicao if c in df_filtrado_ui.columns]
            
            st.dataframe(df_filtrado_ui[cols_exibicao], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma tarefa encontrada com os filtros aplicados.")

    with tab_disciplinas:
        if disciplinas:
            df_d = pd.DataFrame(disciplinas)
            df_p = pd.DataFrame(professores) if professores else pd.DataFrame()
            df_c = pd.DataFrame(cursos) if cursos else pd.DataFrame()
            
            if not df_p.empty:
                df_d_view = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', how='left', suffixes=('', '_prof'))
                df_d_view['nome_prof'] = df_d_view['nome_prof'].fillna('N/A')
            else:
                df_d_view = df_d.copy()
                df_d_view['nome_prof'] = 'N/A'
                
            if not df_c.empty and 'curso_id' in df_d_view.columns:
                df_d_view = df_d_view.merge(df_c[['id', 'curso']], left_on='curso_id', right_on='id', how='left', suffixes=('', '_curso_d'))
                df_d_view['nome_curso'] = df_d_view['curso'].fillna('S/ Curso')
            else:
                df_d_view['nome_curso'] = 'S/ Curso'
                
            df_d_view = df_d_view.rename(columns={
                'id': 'ID Disciplina',
                'nome': 'Nome da Matéria',
                'nome_curso': 'Curso',
                'nome_prof': 'Professor Responsável'
            })
            
            st.dataframe(df_d_view[['ID Disciplina', 'Nome da Matéria', 'Curso', 'Professor Responsável']], use_container_width=True, hide_index=True)
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

    with tab_cursos:
        if cursos:
            df_c = pd.DataFrame(cursos)
            df_c_view = df_c.copy()
            
            def format_date_c(d):
                if not d or pd.isna(d): return "-"
                try:
                    return datetime.datetime.fromisoformat(str(d).split('T')[0]).strftime('%d/%m/%Y')
                except:
                    return str(d)
                    
            if 'data_inicio' in df_c_view.columns:
                df_c_view['Início'] = df_c_view['data_inicio'].apply(format_date_c)
            else:
                df_c_view['Início'] = "-"
                
            if 'data_fim' in df_c_view.columns:
                df_c_view['Fim'] = df_c_view['data_fim'].apply(format_date_c)
            else:
                df_c_view['Fim'] = "-"
                
            df_c_view = df_c_view.rename(columns={
                'id': 'ID Curso',
                'curso': 'Nome do Curso',
                'instituicao': 'Instituição',
                'status': 'Status'
            })
            
            cols_c = ['ID Curso', 'Nome do Curso', 'Instituição', 'Status', 'Início', 'Fim']
            cols_c = [c for c in cols_c if c in df_c_view.columns]
            st.dataframe(df_c_view[cols_c], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum curso cadastrado.")

    st.markdown("<br><hr style='border-top: 1px solid #eee;'><br>", unsafe_allow_html=True)

    # 6. GERAÇÃO DE EXPORTAÇÃO PREMIUM EM HTML (PRONTO PARA IMPRESSÃO EM PDF)
    st.subheader('📥 Central de Exportação')
    st.write('Baixe o relatório consolidado para impressão ou análise externa.')

    # Prepara Cursos por Status para o HTML
    cursos_formado = [c['curso'] for c in cursos if c.get('status') == 'formado'] if cursos else []
    cursos_cursando = [c['curso'] for c in cursos if c.get('status') == 'cursando'] if cursos else []
    cursos_matriculado = [c['curso'] for c in cursos if c.get('status') == 'matriculado'] if cursos else []

    html_cursos_status = ""
    if cursos_formado or cursos_cursando or cursos_matriculado:
        html_cursos_status = "<div class='student-courses'>"
        if cursos_formado:
            c_str = "<br>".join(cursos_formado)
            html_cursos_status += f"<div><span>🎓 FORMADO EM</span><p>{c_str}</p></div>"
        if cursos_cursando:
            c_str = "<br>".join(cursos_cursando)
            html_cursos_status += f"<div><span>📘 CURSANDO</span><p>{c_str}</p></div>"
        if cursos_matriculado:
            c_str = "<br>".join(cursos_matriculado)
            html_cursos_status += f"<div><span>📅 MATRICULADO</span><p>{c_str}</p></div>"
        html_cursos_status += "</div>"

    # Prepara Boletim Ponderado para o HTML
    html_boletim_rows = ""
    if disciplinas and not df_t_raw.empty:
        map_c = {c['id']: c.get('curso', c.get('name', 'Sem Curso')) for c in (cursos or [])}
        for d in disciplinas:
            mf, det = calcular_media_disciplina(d['id'], df_t_raw, d)
            c_nome = map_c.get(d.get('curso_id') or d.get('course_id'), 'Sem Curso')
            
            # Calcular faltas para o HTML
            faltas_disc_html = [f for f in todas_faltas if f.get("disc_id") == d['id']] if todas_faltas else []
            total_faltas_html = sum(f.get("peso") or 1 for f in faltas_disc_html)
            limite_faltas_html = d.get('limite_faltas') or 0
            limite_txt_html = f"/{limite_faltas_html}" if limite_faltas_html > 0 else ""
            
            if mf is not None:
                sit = "APROVADO" if mf >= 6.0 else "REPROVADO"
                sit_class = "nota-badge aprovado" if mf >= 6.0 else "nota-badge reprovado"
                
                map_str = f"{det['map_avg']:.1f}" if det['map_avg'] is not None else "-"
                prova_str = f"{det['prova_final']:.1f}" if det['prova_final'] is not None else "-"
                pai_str = f"{det['pai_grade']:.1f}" if det['pai_grade'] is not None else "-"
                
                parts = []
                if det['map_avg'] is not None:
                    parts.append(f"({det['map_avg']:.1f}x{det['peso_map']})")
                if det['prova_final'] is not None:
                    parts.append(f"({det['prova_final']:.1f}x{det['peso_prova']})")
                if det['pai_grade'] is not None:
                    parts.append(f"({det['pai_grade']:.1f}x{det['peso_pai']})")
                formula = " + ".join(parts) + f" / {det['soma_pesos']}"
                
                html_boletim_rows += f"""
                <tr>
                    <td style="font-weight: 500;">
                        {d['nome']}<br>
                        <span style="font-size: 11px; color: #888;">{c_nome}</span><br>
                        <span style="font-size: 11px; color: #e74c3c;">❌ Faltas: {total_faltas_html}{limite_txt_html}</span>
                    </td>
                    <td>{map_str}</td>
                    <td>{prova_str}</td>
                    <td>{pai_str}</td>
                    <td style="font-family: monospace; font-size: 11px;">{formula}</td>
                    <td style="font-weight: bold; font-size: 14px;">{mf:.2f}</td>
                    <td><span class="{sit_class}">{sit}</span></td>
                </tr>"""
            else:
                html_boletim_rows += f"""
                <tr>
                    <td style="font-weight: 500;">
                        {d['nome']}<br>
                        <span style="font-size: 11px; color: #888;">{c_nome}</span><br>
                        <span style="font-size: 11px; color: #e74c3c;">❌ Faltas: {total_faltas_html}{limite_txt_html}</span>
                    </td>
                    <td colspan="5" style="text-align: center; color: #999;">Nenhuma nota lançada</td>
                    <td><span class="badge entrega">CURSANDO</span></td>
                </tr>"""
    else:
        html_boletim_rows = """<tr><td colspan="7" style="text-align: center; color: #a0aec0;">Nenhum boletim disponível.</td></tr>"""

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
        
        .student-courses {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        .student-courses span {{
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 5px;
            display: block;
        }}
        .student-courses p {{
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
            .student-info, .student-courses {{
                border-top: 1px solid #999;
            }}
            .student-info div span, .student-info div p,
            .student-courses div span, .student-courses div p {{
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
            {html_cursos_status}
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

        <!-- Boletim Escolar Ponderado -->
        <div class="section-title">
            <span>Boletim de Médias Finais Ponderadas</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Disciplina</th>
                    <th>Média MAP</th>
                    <th>Nota Prova</th>
                    <th>Nota PAI</th>
                    <th>Fórmula / Pesos</th>
                    <th>Média Final</th>
                    <th>Situação</th>
                </tr>
            </thead>
            <tbody>
                {html_boletim_rows}
            </tbody>
        </table>"""

    # --- Calcular médias para o gráfico HTML ---
    medias_html_disc = []
    if disciplinas and not df_t_raw.empty:
        for d in disciplinas:
            mf, _ = calcular_media_disciplina(d['id'], df_t_raw, d)
            if mf is not None:
                medias_html_disc.append((d['nome'], mf))
                
    bars_html = ""
    if medias_html_disc:
        for disc_nome, grade in medias_html_disc[:6]: # Limitar a 6
            h_px = max(0, min(140, int(grade * 14)))
            bars_html += f"""
            <div style="flex: 1; display: flex; flex-direction: column; align-items: center; min-width: 60px;">
                <div style="font-size: 11px; font-weight: bold; margin-bottom: 5px; color: #4a3b8c;">{grade:.2f}</div>
                <div style="width: 100%; max-width: 35px; height: {h_px}px; background: linear-gradient(180deg, #6c5ce7 0%, #4a3b8c 100%); border-top-left-radius: 6px; border-top-right-radius: 6px; box-shadow: 0 2px 4px rgba(108,92,231,0.2);"></div>
                <div style="font-size: 10px; margin-top: 8px; text-align: center; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 80px; color: #718096;" title="{disc_nome}">{disc_nome}</div>
            </div>"""
    else:
        bars_html = "<div style='text-align: center; color: #a0aec0; width: 100%; padding: 20px;'>Nenhuma média de notas registrada ainda.</div>"

    completed_percentage = (num_concluidas / num_tarefas * 100) if num_tarefas > 0 else 0.0
    pendentes_percentage = (num_pendentes / num_tarefas * 100) if num_tarefas > 0 else 0.0
    stroke_completed = f"{completed_percentage:.1f} {100 - completed_percentage:.1f}"

    html_content += f"""
        <!-- Gráficos de Acompanhamento no HTML -->
        <div class="section-title">
            <span>Visualização de Desempenho e Progresso</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
            <!-- Bar Chart Card -->
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                <h4 style="margin: 0 0 20px 0; text-align: center; font-size: 14px; color: #4a3b8c; font-weight: 600;">Média Final Ponderada por Disciplina</h4>
                <div style="display: flex; align-items: flex-end; justify-content: space-around; height: 180px; padding: 10px 0; border-bottom: 2px solid #edf2f7;">
                    {bars_html}
                </div>
            </div>
            
            <!-- Pie Chart Card -->
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; background: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: space-between;">
                <h4 style="margin: 0 0 10px 0; text-align: center; font-size: 14px; color: #4a3b8c; font-weight: 600;">Distribuição de Status de Tarefas</h4>
                <div style="display: flex; align-items: center; justify-content: center; gap: 20px; flex-grow: 1;">
                    <svg width="120" height="120" viewBox="0 0 42 42" style="transform: rotate(-90deg);">
                        <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#edf2f7" stroke-width="4"></circle>
                        <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#e67e22" stroke-width="4"></circle>
                        <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#27ae60" stroke-width="4" stroke-dasharray="{stroke_completed}" stroke-dashoffset="0"></circle>
                    </svg>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 12px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #27ae60; border-radius: 50%;"></span>
                            <span style="font-weight: 500;">Concluídas: {num_concluidas} ({completed_percentage:.1f}%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px; font-size: 12px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #e67e22; border-radius: 50%;"></span>
                            <span style="font-weight: 500;">Para Entregar: {num_pendentes} ({pendentes_percentage:.1f}%)</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""

    # --- Continuar com a tabela de tarefas ---
    html_content += """
        <!-- Tabela de Tarefas e Notas -->
        <div class="section-title">
            <span>Histórico de Tarefas, Atividades e Notas</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Atividade</th>
                    <th>Curso</th>
                    <th>Disciplina</th>
                    <th>Status</th>
                    <th>Prazo/Entrega</th>
                    <th>Nota</th>
                </tr>
            </thead>
            <tbody>"""

    # Adicionar as tarefas dinamicamente no HTML (Aplicando os Filtros)
    if not df_filtrado_raw.empty:
        for _, row in df_filtrado_raw.iterrows():
            nome_t = row.get('nome', '-')
            curso_n = row.get('nome_curso', '-')
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
                    dt = datetime.datetime.fromisoformat(str(d_val).split('T')[0])
                    if dt.year <= 1970:
                        prazo = "-"
                    else:
                        prazo = dt.strftime('%d/%m/%Y')
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
                    <td style="font-size: 12px; color: #718096;">{curso_n}</td>
                    <td>{disc_n}</td>
                    <td><span class="{badge_class}">{status_desc}</span></td>
                    <td>{prazo}</td>
                    <td>{nota_desc}</td>
                </tr>"""
    else:
        html_content += """<tr><td colspan="6" style="text-align: center; color: #a0aec0;">Nenhuma tarefa/nota cadastrada ainda.</td></tr>"""

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
                            <th>Curso</th>
                            <th>Professor</th>
                        </tr>
                    </thead>
                    <tbody>"""
                    
    # Adicionar disciplinas dinamicamente
    if disciplinas:
        df_d = pd.DataFrame(disciplinas)
        df_p = pd.DataFrame(professores) if professores else pd.DataFrame()
        df_c = pd.DataFrame(cursos) if cursos else pd.DataFrame()
        
        if not df_p.empty:
            df_merged_d = df_d.merge(df_p[['id', 'nome']], left_on='prof_id', right_on='id', how='left', suffixes=('', '_prof'))
            df_merged_d['nome_prof'] = df_merged_d['nome_prof'].fillna('N/A')
        else:
            df_merged_d = df_d.copy()
            df_merged_d['nome_prof'] = 'N/A'
            
        if not df_c.empty and 'curso_id' in df_merged_d.columns:
            df_merged_d = df_merged_d.merge(df_c[['id', 'curso']], left_on='curso_id', right_on='id', how='left', suffixes=('', '_curso_d'))
            df_merged_d['nome_curso'] = df_merged_d['curso'].fillna('S/ Curso')
        else:
            df_merged_d['nome_curso'] = 'S/ Curso'

        for _, row in df_merged_d.iterrows():
            d_nome = row.get('nome', '-')
            c_nome = row.get('nome_curso', '-')
            p_nome = row.get('nome_prof', '-')
            html_content += f"""
                        <tr>
                            <td style="font-weight: 500;">{d_nome}</td>
                            <td style="font-size: 12px; color: #718096;">{c_nome}</td>
                            <td>{p_nome}</td>
                        </tr>"""
    else:
        html_content += """<tr><td colspan="3" style="text-align: center; color: #a0aec0;">Nenhuma disciplina cadastrada.</td></tr>"""

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
    if not df_filtrado_raw.empty:
        # Formatar a data para CSV, ocultando data padrão (1970)
        def format_date_simple(d):
            if not d or pd.isna(d): return ""
            try:
                if isinstance(d, int):
                    dt = datetime.datetime.fromtimestamp(d/1000.0)
                else:
                    dt = datetime.datetime.fromisoformat(str(d).split('T')[0])
                if dt.year <= 1970:
                    return ""
                return dt.strftime('%Y-%m-%d')
            except:
                return str(d)
        
        df_export = pd.DataFrame()
        df_export['ID'] = df_filtrado_raw.get('id', '')
        df_export['Tarefa_Atividade'] = df_filtrado_raw.get('nome', '')
        df_export['Curso'] = df_filtrado_raw.get('nome_curso', '')
        df_export['Disciplina'] = df_filtrado_raw.get('nome_disc', '')
        df_export['Status'] = df_filtrado_raw.get('status', '')
        df_export['Prazo_Entrega'] = df_filtrado_raw['data_entrega'].apply(format_date_simple) if 'data_entrega' in df_filtrado_raw.columns else ""
        df_export['Nota'] = df_filtrado_raw.get('nota', '')
        
        csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')

    # Opções de downloads na UI do Streamlit
    ex_col1, ex_col2, ex_col3 = st.columns(3)
    
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
        try:
            pdf_bytes = gerar_pdf_bytes(
                student_full_name=student_full_name,
                user_email=user_email,
                dob_str=dob_str,
                media_geral=media_geral,
                taxa_conclusao=taxa_conclusao,
                num_tarefas=num_tarefas,
                num_disciplinas=num_disciplinas,
                disciplinas=disciplinas,
                tarefas=tarefas,
                professores=professores,
                todas_faltas=todas_faltas,
                df_filtrado_raw=df_filtrado_raw,
                cursos=cursos
            )
        except Exception as e:
            pdf_bytes = None
            st.error(f"Erro ao renderizar PDF: {e}")

        if pdf_bytes:
            st.download_button(
                label="📕 Baixar Relatório Premium (PDF)",
                data=pdf_bytes,
                file_name=f"Relatorio_Academico_{student_full_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                help="Baixa o relatório consolidado pronto para impressão em PDF.",
                use_container_width=True
            )
        else:
            st.button("📕 Baixar Relatório Premium (PDF)", disabled=True, use_container_width=True)

    with ex_col3:
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

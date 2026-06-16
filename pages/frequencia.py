"""
=============================================================
 pages/frequencia.py — Módulo de Controle de Frequência
=============================================================
 Permite ao aluno registrar e acompanhar suas faltas por
 disciplina. Exibe resumo visual (cards) com situação de
 risco baseada no limite de faltas configurado.

 Fluxo:
   1. Seleciona a disciplina
   2. Vê cards: total aulas, faltas, presenças, % e situação
   3. Registra nova falta (data + justificativa opcional)
   4. Consulta e remove faltas do histórico
=============================================================
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api import api_get, api_post, api_delete
from utils.theme import apply_theme


# ─── Dialog de confirmação de remoção ───────────────────────
@st.dialog("Confirmar Remoção")
def confirmar_remocao_falta(falta_id):
    st.warning("Tem certeza que deseja remover este registro de falta? Esta ação não pode ser desfeita.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Confirmar Remoção", type="primary", use_container_width=True):
            res = api_delete("faltas", falta_id)
            if res.status_code == 200:
                st.success("Falta removida com sucesso!")
                st.rerun()
            else:
                st.error(f"Erro ao remover: {res.text}")


# ─── Cores e ícones por situação ────────────────────────────
def get_situacao(faltas_count, limite):
    """
    Retorna (ícone, label, cor_hex) baseado na proporção de faltas.
    - Verde  🟢: dentro do limite
    - Amarelo 🟡: ≥ 75% do limite (zona de atenção)
    - Vermelho 🔴: limite atingido ou ultrapassado
    """
    if limite is None or limite == 0:
        return "⚪", "Limite não configurado", "#888888"
    if faltas_count >= limite:
        return "🔴", "Reprovado por Faltas", "#e74c3c"
    if faltas_count >= limite * 0.75:
        return "🟡", "Atenção — próximo do limite", "#f39c12"
    return "🟢", "Frequência Regular", "#27ae60"


# ─── Módulo principal ───────────────────────────────────────
def modulo_frequencia():
    apply_theme()
    t = st.session_state.get("theme", {})
    primary = t.get("primary", "#6c5ce7")

    st.header("📅 Frequência / Faltas")

    # ── Busca as disciplinas do aluno ────────────────────────
    discs = api_get("disciplinas")
    if not discs:
        st.info("Nenhuma disciplina cadastrada. Cadastre disciplinas antes de registrar faltas.")
        return

    # ── Busca cursos para resolver o nome do curso da disciplina ─
    cursos = api_get("curso")
    cursos_map = {}  # {id: nome_do_curso}
    if cursos:
        for c in cursos:
            cursos_map[c["id"]] = c.get("curso") or c.get("name") or "Sem nome"

    # ── Seletor de disciplina ────────────────────────────────
    opcoes_disc = {f"{d['nome']}": d for d in discs}
    disc_nome = st.selectbox(
        "Selecione a Disciplina",
        options=list(opcoes_disc.keys()),
        key="freq_disc_select"
    )

    if not disc_nome:
        return

    disc = opcoes_disc[disc_nome]
    disc_id = disc["id"]
    total_aulas = disc.get("total_aulas") or 0
    limite_faltas = disc.get("limite_faltas") or 0

    # ── Resolve e exibe o curso da disciplina ────────────────
    # Tenta "course_id" (nome correto do campo no banco) e
    # "curso_id" (nome incorreto que o frontend enviava antes da correção)
    course_id = disc.get("curso_id") or disc.get("course_id")
    nome_curso = cursos_map.get(course_id) if course_id else None
    if nome_curso:
        t_theme = st.session_state.get("theme", {})
        p = t_theme.get("primary", "#6c5ce7")
        st.markdown(
            f"<div style='display:inline-block; background:{p}18; border:1px solid {p}44; "
            f"border-radius:8px; padding:4px 12px; font-size:13px; color:{p}; margin-bottom:6px;'>"
            f"🎓 Curso: <strong>{nome_curso}</strong></div>",
            unsafe_allow_html=True
        )
    else:
        st.caption("ℹ️ Esta disciplina não está vinculada a um curso.")

    # ── Busca as faltas da disciplina selecionada ────────────
    todas_faltas = api_get("faltas")
    faltas_disc = [f for f in todas_faltas if f.get("disc_id") == disc_id] if todas_faltas else []
    # Contagem ponderada: cada falta vale seu "peso" (padrão 1)
    # Ex: 3 registros com pesos [1, 2, 1] = 4 aulas perdidas
    total_faltas = sum(f.get("peso") or 1 for f in faltas_disc)
    total_presencas = max(0, total_aulas - total_faltas) if total_aulas > 0 else None
    pct_presenca = (total_presencas / total_aulas * 100) if total_aulas > 0 else None

    icone, label, cor = get_situacao(total_faltas, limite_faltas if limite_faltas > 0 else None)


    # ── Cards de resumo ──────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""<div style='background: {primary}18; border: 1px solid {primary}44;
                border-radius: 12px; padding: 16px; text-align: center;'>
                <p style='font-size: 13px; color: #888; margin: 0;'>Total de Aulas</p>
                <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: {primary};'>
                    {total_aulas if total_aulas > 0 else "—"}
                </p>
            </div>""",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""<div style='background: #e74c3c18; border: 1px solid #e74c3c44;
                border-radius: 12px; padding: 16px; text-align: center;'>
                <p style='font-size: 13px; color: #888; margin: 0;'>Faltas Registradas</p>
                <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: #e74c3c;'>
                    {total_faltas}
                </p>
            </div>""",
            unsafe_allow_html=True
        )

    with c3:
        valor_pct = f"{pct_presenca:.1f}%" if pct_presenca is not None else "—"
        st.markdown(
            f"""<div style='background: #27ae6018; border: 1px solid #27ae6044;
                border-radius: 12px; padding: 16px; text-align: center;'>
                <p style='font-size: 13px; color: #888; margin: 0;'>% de Presença</p>
                <p style='font-size: 32px; font-weight: 700; margin: 4px 0; color: #27ae60;'>
                    {valor_pct}
                </p>
            </div>""",
            unsafe_allow_html=True
        )

    with c4:
        lim_texto = str(limite_faltas) if limite_faltas > 0 else "—"
        st.markdown(
            f"""<div style='background: {cor}18; border: 1px solid {cor}55;
                border-radius: 12px; padding: 16px; text-align: center;'>
                <p style='font-size: 13px; color: #888; margin: 0;'>Situação</p>
                <p style='font-size: 22px; font-weight: 700; margin: 4px 0; color: {cor};'>
                    {icone} {label}
                </p>
                <p style='font-size: 11px; color: #aaa; margin: 0;'>
                    Limite: {lim_texto} faltas
                </p>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Barra de progresso visual ────────────────────────────
    if total_aulas > 0 and limite_faltas > 0:
        pct_do_limite = min(total_faltas / limite_faltas, 1.0)
        st.markdown(f"**Aulas perdidas:** {total_faltas} / {limite_faltas}")
        st.progress(pct_do_limite)

    # ── Formulário: registrar nova falta ─────────────────────
    with st.expander("➕ Registrar Nova Falta"):
        with st.form("form_nova_falta"):
            col_data, col_peso = st.columns([3, 1])
            with col_data:
                data_falta = st.date_input(
                    "Data da Aula que Faltou",
                    value=date.today(),
                    max_value=date.today(),
                    format="DD/MM/YYYY"
                )
            with col_peso:
                peso = st.number_input(
                    "Aulas perdidas",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    help="Quantas aulas foram perdidas neste dia? Ex: se a disciplina tem 2 aulas seguidas, coloque 2."
                )
            justificativa = st.text_area(
                "Justificativa / Observação (opcional)",
                placeholder="Ex.: Consulta médica, problema no transporte…",
                max_chars=300
            )
            submitted = st.form_submit_button("📌 Registrar Falta", type="primary", use_container_width=True)

            if submitted:
                # Converte date para ISO string compatível com Xano timestamp
                data_iso = datetime.combine(data_falta, datetime.min.time()).isoformat()
                payload = {
                    "disc_id": disc_id,
                    "data_falta": data_iso,
                    "peso": int(peso),
                }
                # Resolve course_id tentando os dois nomes de campo possíveis:
                # "course_id" (nome correto) ou "curso_id" (nome legado do frontend)
                course_id = disc.get("curso_id") or disc.get("course_id")
                if course_id:
                    payload["course_id"] = int(course_id)

                if justificativa.strip():
                    payload["justificativa"] = justificativa.strip()

                res = api_post("faltas", payload)
                if res.status_code in [200, 201]:
                    aulas_txt = f"{peso} aula{'s' if peso > 1 else ''}"
                    st.success(f"✅ Falta registrada para {data_falta.strftime('%d/%m/%Y')} ({aulas_txt})!")
                    st.rerun()
                else:
                    st.error(f"Erro ao registrar falta: {res.text}")

    # ── Histórico de faltas ──────────────────────────────────
    st.markdown("### 📋 Histórico de Faltas")

    if not faltas_disc:
        st.success("🎉 Nenhuma falta registrada nesta disciplina!")
    else:
        for falta in faltas_disc:
            falta_id = falta["id"]
            # Formata data para exibição amigável
            try:
                dt_raw = falta.get("data_falta", "")
                if dt_raw:
                    # Xano retorna timestamps como inteiro em milissegundos
                    if isinstance(dt_raw, (int, float)):
                        dt_obj = datetime.fromtimestamp(dt_raw / 1000)
                    else:
                        # Fallback: tenta ISO string (ex: "2024-06-15T00:00:00Z")
                        dt_obj = datetime.fromisoformat(str(dt_raw).replace("Z", ""))
                    data_fmt = dt_obj.strftime("%d/%m/%Y")
                else:
                    data_fmt = "Data não informada"
            except Exception:
                data_fmt = "Data inválida"

            justif = falta.get("justificativa") or "Sem justificativa"

            # Resolve nome do curso vinculado à falta
            falta_course_id = falta.get("course_id") or falta.get("curso_id")
            nome_curso_falta = cursos_map.get(falta_course_id, "") if falta_course_id else ""
            curso_badge = (
                f"<span style='background:{primary}22; color:{primary}; "
                f"border:1px solid {primary}44; border-radius:6px; "
                f"font-size:11px; padding:2px 8px; margin-left:10px;'>"
                f"🎓 {nome_curso_falta}</span>"
                if nome_curso_falta else ""
            )

            # Badge do peso (aulas perdidas neste registro)
            peso_val = falta.get("peso") or 1
            peso_label = f"{peso_val} aula{'s' if peso_val > 1 else ''}"
            peso_cor = "#e74c3c" if peso_val > 1 else "#888"
            peso_badge = (
                f"<span style='background:{peso_cor}22; color:{peso_cor}; "
                f"border:1px solid {peso_cor}44; border-radius:6px; "
                f"font-size:11px; padding:2px 8px; margin-left:8px;'>"
                f"⚖️ {peso_label}</span>"
            )

            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"""<div style='background: #ffffff08; border: 1px solid #ffffff15;
                        border-radius: 8px; padding: 10px 14px; margin-bottom: 6px;'>
                        <span style='font-weight: 600;'>📅 {data_fmt}</span>
                        {curso_badge}
                        {peso_badge}
                        <div style='margin-top: 6px;'>
                            <span style='color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;'>Justificativa:</span>
                            <span style='color: #f23030; font-size: 14px; margin-left: 6px;'>{justif}</span>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
            with col_btn:
                st.markdown("<div style='padding-top: 2px;'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_falta_{falta_id}", help="Remover esta falta"):
                    confirmar_remocao_falta(falta_id)
                st.markdown("</div>", unsafe_allow_html=True)


modulo_frequencia()

"""
=============================================================
 pages/configuracoes.py — Personalização de Aparência
=============================================================
 Esta página permite ao usuário escolher o tema visual
 do EduTrack AI com:
   - Temas predefinidos com preview visual (cards clicáveis)
   - Personalização avançada com seletores de cor individuais
   - Preview ao vivo das cores escolhidas
   - Botão de restauração ao padrão

 As preferências são salvas em st.session_state.theme e
 aplicadas imediatamente via apply_theme() em todas as páginas.
=============================================================
"""

import streamlit as st
from utils.theme import (
    apply_theme,
    get_theme,
    save_theme_to_session,
    DEFAULT_THEMES,
    DEFAULT_THEME_KEY,
    AVAILABLE_FONTS,
    DEFAULT_FONT_KEY,
)


def pagina_configuracoes():
    """
    Renderiza a interface completa de personalização de aparência.
    Dividida em três seções:
      1. Temas Rápidos (cards predefinidos)
      2. Personalização Avançada (color pickers)
      3. Preview ao vivo
    """
    apply_theme()

    # ── CSS extra desta página ────────────────────────────────
    st.markdown("""
    <style>
    /* Cards de tema clicáveis */
    .theme-card {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
        background: white;
    }
    .theme-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .theme-card.active {
        border-width: 3px;
    }
    /* Swatch de cor */
    .color-swatch {
        width: 100%;
        height: 40px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    .swatch-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.6);
    }
    /* Preview banner */
    .preview-section {
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎨 Aparência e Tema")
    st.markdown(
        "<p style='color: var(--text-muted); margin-top: -10px; margin-bottom: 25px;'>"
        "Personalize as cores do EduTrack AI ao seu gosto. As alterações são aplicadas imediatamente em todas as páginas."
        "</p>",
        unsafe_allow_html=True
    )

    # ── Diagnóstico de Persistência no Xano ──────────────────
    if st.session_state.get('user_role') == 'admin':
        with st.expander("🔍 Diagnóstico de salvamento no Xano", expanded=False):
            from utils.api import api_load_theme, api_save_theme

            diag_col1, diag_col2 = st.columns(2)

            with diag_col1:
                st.markdown("**Status do último save:**")
                save_ok  = st.session_state.get('_theme_save_ok')
                save_msg = st.session_state.get('_theme_save_msg', '(nenhum save realizado ainda)')
                if save_ok is None:
                    st.info("Nenhum tema foi aplicado ainda nesta sessão.")
                elif save_ok:
                    st.success(f"✅ Salvo com sucesso no Xano!")
                else:
                    st.error(f"❌ Falha ao salvar: `{save_msg}`")

                if st.button("🧪 Testar save agora", key="diag_test_save"):
                    test_theme = get_theme()
                    ok, msg = api_save_theme(test_theme)
                    if ok:
                        st.success("✅ Save de teste OK!")
                        if isinstance(msg, dict):
                            st.markdown("**Resposta do /update_theme:**")
                            st.json(msg)
                        else:
                            st.info(f"Retorno: {msg}")
                    else:
                        st.error(f"❌ Erro: {msg}")

            with diag_col2:
                st.markdown("**Status do carregamento:**")
                loaded = api_load_theme()
                if loaded:
                    st.success(f"✅ Tema encontrado no Xano: **{loaded.get('name', '?')}**")
                else:
                    st.warning("⚠️ Nenhum tema salvo encontrado no Xano (campo vazio ou null).")

                st.markdown(f"**user_id:** `{st.session_state.get('user_id', 'N/A')}`")
                st.markdown(f"**auth_token:** `{'✅ presente' if st.session_state.get('auth_token') else '❌ ausente'}`")

                # Mostra o JSON bruto de /auth/me para identificar quais campos são retornados
                if st.button("🔎 Ver campos retornados por /auth/me", key="diag_show_me"):
                    import requests as _req
                    from utils.api import BASE_URL, get_headers
                    r = _req.get(f"{BASE_URL}/auth/me", headers=get_headers())
                    if r.status_code == 200:
                        data = r.json()
                        campos = list(data.keys())
                        tem_theme = "theme_preferences" in data
                        st.markdown(f"**Campos retornados ({len(campos)}):**")
                        st.code(", ".join(campos))
                        if tem_theme:
                            st.success("✅ `theme_preferences` está na resposta!")
                            st.json(data.get("theme_preferences"))
                        else:
                            st.error("❌ `theme_preferences` **NÃO** está na resposta do /auth/me")
                            st.caption("O Xano salva o dado, mas não o inclui na resposta deste endpoint.")
                    else:
                        st.error(f"Erro ao chamar /auth/me: {r.status_code}")


    current_theme_key = st.session_state.get("theme_key", DEFAULT_THEME_KEY)
    current_theme = get_theme()

    # ==================================================================
    # SEÇÃO 1 — TEMAS RÁPIDOS
    # ==================================================================
    st.subheader("⚡ Temas Rápidos")
    st.caption("Escolha um tema predefinido para aplicar instantaneamente.")


    # Exibimos 3 temas por linha (2 linhas)
    theme_keys = list(DEFAULT_THEMES.keys())
    col_size = 3

    for row_start in range(0, len(theme_keys), col_size):
        row_keys = theme_keys[row_start:row_start + col_size]
        cols = st.columns(len(row_keys))

        for col, tkey in zip(cols, row_keys):
            t = DEFAULT_THEMES[tkey]
            is_active = (tkey == current_theme_key)
            active_style = f"border-color: {t['primary']}; box-shadow: 0 0 0 3px {t['primary']}33;" if is_active else ""
            active_badge = "✅ Ativo" if is_active else ""

            with col:
                # Mini preview do tema com pontos coloridos
                st.markdown(f"""
                <div class="theme-card" style="{active_style}">
                    <div class="color-swatch" style="background: {t['banner_grad']};">
                        <div class="swatch-dot" style="background: {t['primary']};"></div>
                        <div class="swatch-dot" style="background: {t['secondary']};"></div>
                        <div class="swatch-dot" style="background: {t['accent']};"></div>
                    </div>
                    <p style="margin: 0; font-weight: 600; font-size: 0.9em; color: #333;">{t['emoji']} {t['name']}</p>
                    <p style="margin: 2px 0 0 0; font-size: 0.75em; color: #888;">{active_badge}</p>
                </div>
                """, unsafe_allow_html=True)

                # Botão de aplicação
                btn_label = "✅ Aplicado" if is_active else "Aplicar"
                btn_type = "primary" if is_active else "secondary"
                if st.button(
                    btn_label,
                    key=f"apply_theme_{tkey}",
                    use_container_width=True,
                    type=btn_type,
                    disabled=is_active,
                ):
                    save_theme_to_session(DEFAULT_THEMES[tkey], tkey)
                    st.success(f"Tema **{t['name']}** aplicado! ✨")
                    st.rerun()

    st.divider()

    # ==================================================================
    # SEÇÃO 2 — PERSONALIZAÇÃO AVANÇADA
    # ==================================================================
    st.subheader("🔧 Personalização Avançada")
    st.caption("Defina cores individuais para criar seu próprio tema.")

    with st.expander("🎨 Abrir seletor de cores avançado", expanded=False):
        adv_col1, adv_col2 = st.columns(2)

        with adv_col1:
            st.markdown("**Cores Principais**")
            new_primary = st.color_picker(
                "🎯 Cor Principal (botões, destaques)",
                value=current_theme.get("primary", "#6c5ce7"),
                key="adv_primary"
            )
            new_secondary = st.color_picker(
                "🌑 Cor Secundária (variação escura)",
                value=current_theme.get("secondary", "#4a3b8c"),
                key="adv_secondary"
            )
            new_accent = st.color_picker(
                "✨ Cor de Destaque (cards, bordas)",
                value=current_theme.get("accent", "#a29bfe"),
                key="adv_accent"
            )
            new_btn_text = st.color_picker(
                "🔤 Cor do Texto dos Botões",
                value=current_theme.get("btn_text_color", "#ffffff"),
                key="adv_btn_text"
            )

        with adv_col2:
            st.markdown("**Cores da Interface**")
            new_sidebar_bg = st.color_picker(
                "📋 Fundo da Sidebar",
                value=current_theme.get("sidebar_bg", "#f8f6ff"),
                key="adv_sidebar_bg"
            )
            new_sidebar_text = st.color_picker(
                "📝 Texto da Sidebar",
                value=current_theme.get("sidebar_text", "#4a3b8c"),
                key="adv_sidebar_text"
            )
            new_banner_title = st.color_picker(
                "🏷️ Cor do Título do Banner",
                value=current_theme.get("banner_title", "#4a3b8c"),
                key="adv_banner_title"
            )

        st.markdown("**Tipografia**")
        # Identifica a fonte atual para pré-selecionar no selectbox
        current_font_key = DEFAULT_FONT_KEY
        current_family = current_theme.get("font_family", AVAILABLE_FONTS[DEFAULT_FONT_KEY]["family"])
        for fname, fdata in AVAILABLE_FONTS.items():
            if fdata["family"] == current_family:
                current_font_key = fname
                break

        font_options = list(AVAILABLE_FONTS.keys())
        font_idx = font_options.index(current_font_key) if current_font_key in font_options else 0
        new_font_key = st.selectbox(
            "🔡 Tipo de Fonte",
            options=font_options,
            index=font_idx,
            key="adv_font_family",
            help="Escolha a família tipográfica aplicada em toda a interface."
        )
        # Preview da fonte selecionada
        preview_font_url = AVAILABLE_FONTS[new_font_key]["url"]
        preview_font_family = AVAILABLE_FONTS[new_font_key]["family"]
        st.markdown(
            f"<link href='{preview_font_url}' rel='stylesheet'>"
            f"<p style='font-family: {preview_font_family}; font-size: 1em; margin: 4px 0; "
            f"padding: 8px 12px; background: #f7f7fc; border-radius: 8px; border: 1px solid #e2e8f0;'>"
            f"Exemplo: The quick brown fox jumps over the lazy dog. "
            f"<strong>AaBbCcDd 0123</strong></p>",
            unsafe_allow_html=True
        )

        st.markdown("**Modo Escuro**")
        dark_mode = st.toggle(
            "🌑 Ativar modo escuro (fundo escuro geral)",
            value=current_theme.get("dark_mode", False),
            key="adv_dark_mode"
        )

        st.markdown("---")

        apply_col, reset_col = st.columns([2, 1])
        with apply_col:
            if st.button("🎨 Aplicar Cores Personalizadas", type="primary", use_container_width=True):
                # Monta o gradient baseado nas novas cores
                banner_grad = f"linear-gradient(90deg, {new_primary}22 0%, {new_secondary}44 100%)"
                bg_main  = "#1a1a2e" if dark_mode else "#f7f7fc"
                text_main  = "#ecf0f1" if dark_mode else "#2d3748"
                text_muted = "#bdc3c7" if dark_mode else "#718096"

                custom_theme = {
                    "name": "Personalizado",
                    "emoji": "🎨",
                    "primary": new_primary,
                    "secondary": new_secondary,
                    "accent": new_accent,
                    "sidebar_bg": new_sidebar_bg,
                    "sidebar_text": new_sidebar_text,
                    "banner_grad": banner_grad,
                    "banner_title": new_banner_title,
                    "card_top": new_primary,
                    "text_main": text_main,
                    "text_muted": text_muted,
                    "bg_main": bg_main,
                    "btn_text_color": new_btn_text,
                    "font_family": AVAILABLE_FONTS[new_font_key]["family"],
                    "font_url": AVAILABLE_FONTS[new_font_key]["url"],
                    "dark_mode": dark_mode,
                }
                save_theme_to_session(custom_theme, "custom")
                st.success("Tema personalizado aplicado! ✨")
                st.rerun()

        with reset_col:
            if st.button("↩️ Restaurar Padrão", use_container_width=True):
                save_theme_to_session(DEFAULT_THEMES[DEFAULT_THEME_KEY], DEFAULT_THEME_KEY)
                st.success("Tema padrão restaurado!")
                st.rerun()

    st.divider()

    # ==================================================================
    # SEÇÃO 3 — PREVIEW AO VIVO
    # ==================================================================
    st.subheader("👁️ Preview do Tema Atual")
    t = current_theme

    # Moldura externa do preview
    st.markdown(
        "<div style='border: 2px dashed #e2e8f0; border-radius: 12px; padding: 20px; margin-top: 10px;'>",
        unsafe_allow_html=True
    )

    # Banner de boas-vindas simulado
    st.markdown(
        f"<div style='background: {t['banner_grad']}; padding: 20px; border-radius: 12px; margin-bottom: 15px;'>"
        f"<h3 style='color: {t['banner_title']}; margin: 0 0 5px 0;'>Bem-vindo(a) de volta, Estudante! 👋</h3>"
        f"<p style='color: {t['text_muted']}; margin: 0; font-size: 0.9em;'>Acompanhe seu desempenho e mantenha o ritmo.</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Cards de KPI simulados — um por coluna para evitar problemas de grid
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    with kpi_c1:
        st.markdown(
            f"<div style='background: white; padding: 15px; border-radius: 10px; text-align: center; "
            f"border-top: 4px solid {t['card_top']}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>"
            f"<p style='color: {t['text_muted']}; font-size: 0.8em; margin: 0 0 4px 0;'>Cursos</p>"
            f"<h3 style='color: {t['primary']}; margin: 0;'>3</h3></div>",
            unsafe_allow_html=True
        )
    with kpi_c2:
        st.markdown(
            f"<div style='background: white; padding: 15px; border-radius: 10px; text-align: center; "
            f"border-top: 4px solid {t['accent']}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>"
            f"<p style='color: {t['text_muted']}; font-size: 0.8em; margin: 0 0 4px 0;'>Disciplinas</p>"
            f"<h3 style='color: {t['secondary']}; margin: 0;'>8</h3></div>",
            unsafe_allow_html=True
        )
    with kpi_c3:
        st.markdown(
            f"<div style='background: white; padding: 15px; border-radius: 10px; text-align: center; "
            f"border-top: 4px solid #27ae60; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>"
            f"<p style='color: {t['text_muted']}; font-size: 0.8em; margin: 0 0 4px 0;'>Concluídas</p>"
            f"<h3 style='color: #27ae60; margin: 0;'>12</h3></div>",
            unsafe_allow_html=True
        )
    with kpi_c4:
        st.markdown(
            f"<div style='background: white; padding: 15px; border-radius: 10px; text-align: center; "
            f"border-top: 4px solid #e67e22; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>"
            f"<p style='color: {t['text_muted']}; font-size: 0.8em; margin: 0 0 4px 0;'>Pendentes</p>"
            f"<h3 style='color: #e67e22; margin: 0;'>4</h3></div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar simulada + painel de tarefas
    sb_col, tasks_col = st.columns([1, 2])
    with sb_col:
        st.markdown(
            f"<div style='background: {t['sidebar_bg']}; padding: 15px; border-radius: 10px; "
            f"border: 1px solid {t['accent']}44; height: 100%;'>"
            f"<p style='color: {t['sidebar_text']}; font-weight: 700; margin: 0 0 8px 0; font-size: 0.9em;'>EduTrack AI</p>"
            f"<p style='color: {t['primary']}; font-size: 0.8em; margin: 4px 0;'>📊 Painel Geral</p>"
            f"<p style='color: {t['sidebar_text']}; font-size: 0.8em; margin: 4px 0; opacity: 0.7;'>🎓 Cursos</p>"
            f"<p style='color: {t['sidebar_text']}; font-size: 0.8em; margin: 4px 0; opacity: 0.7;'>📚 Disciplinas</p>"
            f"<p style='color: {t['sidebar_text']}; font-size: 0.8em; margin: 4px 0; opacity: 0.7;'>📝 Tarefas</p>"
            f"<p style='color: {t['sidebar_text']}; font-size: 0.8em; margin: 4px 0; opacity: 0.7;'>🎨 Aparência</p>"
            f"<hr style='border-color: {t['accent']}44; margin: 8px 0;'>"
            f"<p style='font-size: 0.7em; color: {t['text_muted']}; text-align: center; margin: 0;'>📌 EduTrack-IA</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with tasks_col:
        st.markdown(
            f"<div style='background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;'>"
            f"<p style='color: {t['text_muted']}; font-size: 0.85em; margin: 0 0 8px 0;'>Próximas Tarefas</p>"
            f"<div style='background: {t['bg_main']}; padding: 10px; border-radius: 8px; "
            f"border-left: 4px solid {t['primary']}; margin-bottom: 8px;'>"
            f"<p style='color: {t['text_main']}; font-size: 0.85em; font-weight: 600; margin: 0;'>Prova de Cálculo III</p>"
            f"<p style='color: {t['text_muted']}; font-size: 0.75em; margin: 2px 0 0 0;'>📅 15/06/2026</p>"
            f"</div>"
            f"<div style='background: {t['bg_main']}; padding: 10px; border-radius: 8px; "
            f"border-left: 4px solid {t['accent']};'>"
            f"<p style='color: {t['text_main']}; font-size: 0.85em; font-weight: 600; margin: 0;'>Trabalho de TCC</p>"
            f"<p style='color: {t['text_muted']}; font-size: 0.75em; margin: 2px 0 0 0;'>📅 20/06/2026</p>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True
        )

    # Fecha a moldura externa
    st.markdown("</div>", unsafe_allow_html=True)

    # Nome e informações do tema atual
    theme_name = t.get("name", "Personalizado")
    theme_emoji = t.get("emoji", "🎨")
    st.markdown(
        f"<p style='text-align: center; color: var(--text-muted); margin-top: 12px; font-size: 0.85em;'>"
        f"Tema atual: <strong>{theme_emoji} {theme_name}</strong></p>",
        unsafe_allow_html=True
    )


    st.divider()

    # ==================================================================
    # SEÇÃO 4 — BOTÃO DE RESET NO RODAPÉ
    # ==================================================================
    footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
    with footer_col2:
        if st.button(
            "↩️ Restaurar Tema Padrão (Roxo EduTrack)",
            use_container_width=True,
            key="footer_reset_btn"
        ):
            save_theme_to_session(DEFAULT_THEMES[DEFAULT_THEME_KEY], DEFAULT_THEME_KEY)
            st.success("✅ Tema padrão restaurado com sucesso!")
            st.rerun()


# ─── Ponto de entrada desta página ──────────────────────────
pagina_configuracoes()

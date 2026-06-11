"""
=============================================================
 utils/theme.py — Sistema de Temas e Personalização Visual
=============================================================
 Este módulo centraliza toda a lógica de temas do EduTrack AI.
 
 Responsabilidades:
   - Definir os temas predefinidos disponíveis
   - Aplicar o tema ativo via injeção de CSS dinâmico
   - Persistir as preferências do usuário na sessão
 
 Como funciona:
   1. Cada página chama apply_theme() no topo
   2. apply_theme() injeta um bloco <style> com variáveis CSS
   3. Todos os elementos HTML da página usam essas variáveis
   4. Quando o usuário troca o tema, st.rerun() reaplica o CSS
=============================================================
"""

import streamlit as st

# ============================================================
# FONTES DISPONÍVEIS PARA SELEÇÃO
# ============================================================
# Mapeamento: nome amigável -> família CSS + URL do Google Fonts
AVAILABLE_FONTS = {
    "Inter (Padrão)"        : {"family": "'Inter', sans-serif",         "url": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"},
    "Roboto"                : {"family": "'Roboto', sans-serif",         "url": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap"},
    "Poppins"               : {"family": "'Poppins', sans-serif",        "url": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"},
    "Outfit"                : {"family": "'Outfit', sans-serif",         "url": "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"},
    "Nunito"                : {"family": "'Nunito', sans-serif",         "url": "https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap"},
    "Montserrat"            : {"family": "'Montserrat', sans-serif",     "url": "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap"},
    "Lato"                  : {"family": "'Lato', sans-serif",           "url": "https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap"},
    "Source Code Pro (Mono)": {"family": "'Source Code Pro', monospace", "url": "https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;500;600&display=swap"},
}

DEFAULT_FONT_KEY = "Inter (Padrão)"

# ============================================================
# TEMAS PREDEFINIDOS
# ============================================================
# Cada tema é um dicionário com as seguintes chaves:
#   name           — Nome exibido na interface
#   emoji          — Emoji representativo do tema
#   primary        — Cor principal (botões, títulos, destaques)
#   secondary      — Cor secundária (variação mais escura do primário)
#   accent         — Cor de destaque (cards, bordas, gráficos)
#   sidebar_bg     — Cor de fundo da sidebar
#   sidebar_text   — Cor do texto da sidebar
#   banner_grad    — Gradiente CSS do banner de boas-vindas
#   card_top       — Cor da borda superior dos cards de KPI
#   text_main      — Cor do texto principal
#   text_muted     — Cor do texto secundário/esmaecido
#   bg_main        — Cor de fundo principal da página
#   btn_text_color — Cor do texto dentro dos botões primários
#   font_family    — Família tipográfica aplicada globalmente
#   font_url       — URL do Google Fonts para importar a fonte
#   dark_mode      — Se True, usa esquema escuro
DEFAULT_THEMES = {
    "roxo_edutrack": {
        "name": "Roxo EduTrack",
        "emoji": "🟣",
        "primary": "#6c5ce7",
        "secondary": "#4a3b8c",
        "accent": "#a29bfe",
        "sidebar_bg": "#f8f6ff",
        "sidebar_text": "#4a3b8c",
        "banner_grad": "linear-gradient(90deg, #f3f0ff 0%, #e0d8ff 100%)",
        "banner_title": "#4a3b8c",
        "card_top": "#6c5ce7",
        "text_main": "#2d3748",
        "text_muted": "#718096",
        "bg_main": "#f7f7fc",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": False,
    },
    "azul_oceano": {
        "name": "Azul Oceano",
        "emoji": "🔵",
        "primary": "#2980b9",
        "secondary": "#1a5276",
        "accent": "#5dade2",
        "sidebar_bg": "#eaf4fb",
        "sidebar_text": "#1a5276",
        "banner_grad": "linear-gradient(90deg, #d6eaf8 0%, #aed6f1 100%)",
        "banner_title": "#1a5276",
        "card_top": "#2980b9",
        "text_main": "#1a2a3a",
        "text_muted": "#5d8aa8",
        "bg_main": "#f0f8ff",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": False,
    },
    "verde_natureza": {
        "name": "Verde Natureza",
        "emoji": "🟢",
        "primary": "#27ae60",
        "secondary": "#1e8449",
        "accent": "#58d68d",
        "sidebar_bg": "#eafaf1",
        "sidebar_text": "#1e8449",
        "banner_grad": "linear-gradient(90deg, #d5f5e3 0%, #a9dfbf 100%)",
        "banner_title": "#1e8449",
        "card_top": "#27ae60",
        "text_main": "#1a2e1a",
        "text_muted": "#5d8a6a",
        "bg_main": "#f0faf4",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": False,
    },
    "rosa_suave": {
        "name": "Rosa Suave",
        "emoji": "🌸",
        "primary": "#e91e8c",
        "secondary": "#ad1457",
        "accent": "#f48fb1",
        "sidebar_bg": "#fce4f0",
        "sidebar_text": "#ad1457",
        "banner_grad": "linear-gradient(90deg, #fce4ec 0%, #f8bbd9 100%)",
        "banner_title": "#ad1457",
        "card_top": "#e91e8c",
        "text_main": "#2a0a1a",
        "text_muted": "#8a4a6a",
        "bg_main": "#fff5f8",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": False,
    },
    "laranja_vibrante": {
        "name": "Laranja Vibrante",
        "emoji": "🟠",
        "primary": "#e67e22",
        "secondary": "#ca6f1e",
        "accent": "#f0b27a",
        "sidebar_bg": "#fef5e7",
        "sidebar_text": "#ca6f1e",
        "banner_grad": "linear-gradient(90deg, #fdebd0 0%, #fad7a0 100%)",
        "banner_title": "#ca6f1e",
        "card_top": "#e67e22",
        "text_main": "#2a1a00",
        "text_muted": "#8a6a3a",
        "bg_main": "#fffaf0",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": False,
    },
    "modo_escuro": {
        "name": "Modo Escuro",
        "emoji": "🌑",
        "primary": "#7f8c8d",
        "secondary": "#2c3e50",
        "accent": "#95a5a6",
        "sidebar_bg": "#1e1e2e",
        "sidebar_text": "#ecf0f1",
        "banner_grad": "linear-gradient(90deg, #2c3e50 0%, #1a252f 100%)",
        "banner_title": "#ecf0f1",
        "card_top": "#95a5a6",
        "text_main": "#ecf0f1",
        "text_muted": "#bdc3c7",
        "bg_main": "#1a1a2e",
        "btn_text_color": "#ffffff",
        "font_family": AVAILABLE_FONTS["Inter (Padrão)"]["family"],
        "font_url": AVAILABLE_FONTS["Inter (Padrão)"]["url"],
        "dark_mode": True,
    },
}

# Tema aplicado por padrão (primeiro uso)
DEFAULT_THEME_KEY = "roxo_edutrack"


# ============================================================
# FUNÇÕES DE GERENCIAMENTO DE TEMA
# ============================================================

def get_theme() -> dict:
    """
    Retorna o tema atualmente ativo do session_state.
    Se não existir, inicializa com o tema padrão.
    """
    if "theme" not in st.session_state or not st.session_state.theme:
        st.session_state.theme = DEFAULT_THEMES[DEFAULT_THEME_KEY].copy()
        st.session_state.theme_key = DEFAULT_THEME_KEY
    return st.session_state.theme


def save_theme_to_session(theme_dict: dict, theme_key: str = "custom") -> None:
    """
    Salva um tema no session_state E persiste no Xano (campo theme_preferences).
    
    Parâmetros:
        theme_dict — dicionário com os valores do tema
        theme_key  — chave identificadora do tema (ex: 'azul_oceano' ou 'custom')
    
    A persistência no Xano é silenciosa: falhas não bloqueiam a UI,
    o tema ainda funciona na sessão atual mesmo se o save falhar.
    """
    st.session_state.theme = theme_dict.copy()
    st.session_state.theme_key = theme_key

    # Persiste no Xano de forma silenciosa (não bloqueia se falhar)
    try:
        from utils.api import api_save_theme
        ok, msg = api_save_theme(theme_dict)
        # Armazena o resultado para diagnóstico (visível na página de configurações)
        st.session_state['_theme_save_ok']  = ok
        st.session_state['_theme_save_msg'] = msg
    except Exception as e:
        st.session_state['_theme_save_ok']  = False
        st.session_state['_theme_save_msg'] = str(e)


def apply_theme() -> None:
    """
    Injeta o CSS do tema ativo em toda a página atual.
    
    DEVE ser chamada no início de cada página/função de módulo.
    Usa st.markdown com unsafe_allow_html=True para injetar um bloco
    <style> com variáveis CSS que sobrescrevem os estilos padrão do Streamlit.
    
    Variáveis CSS definidas:
      --primary        : cor principal (botões, títulos)
      --secondary      : variação mais escura do primário
      --accent         : cor de destaque (bordas, gráficos)
      --sidebar-bg     : fundo da sidebar
      --text-main      : texto principal
      --text-muted     : texto secundário
      --bg-main        : fundo da página
      --banner-grad    : gradiente do banner de boas-vindas
      --btn-text-color : cor do texto dos botões primários
      --font-family    : família tipográfica global
    """
    t = get_theme()

    # Valores com fallback para compatibilidade com temas salvos sem esses campos
    btn_text   = t.get("btn_text_color", "#ffffff")
    font_family = t.get("font_family", AVAILABLE_FONTS[DEFAULT_FONT_KEY]["family"])
    font_url    = t.get("font_url",    AVAILABLE_FONTS[DEFAULT_FONT_KEY]["url"])

    dark_overrides = ""
    if t.get("dark_mode"):
        dark_overrides = f"""
            /* Overrides para Modo Escuro */
            .stApp {{
                background-color: {t['bg_main']} !important;
            }}
            .stMarkdown, .stText, p, span, label, h1, h2, h3, h4, h5, h6 {{
                color: {t['text_main']} !important;
            }}
            [data-testid="stMetricValue"] {{
                color: {t['text_main']} !important;
            }}
        """

    sidebar_text_css = f"""
        /* Texto da Sidebar */
        [data-testid="stSidebar"] * {{
            color: {t['sidebar_text']} !important;
        }}
        [data-testid="stSidebar"] .stButton > button {{
            background-color: {t['primary']} !important;
            color: {btn_text} !important;
            border: none !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {t['secondary']} !important;
            color: {btn_text} !important;
            opacity: 0.9;
        }}
    """

    css = f"""
    <style>
    /* ── Importação de Fonte via Google Fonts ── */
    @import url('{font_url}');

    /* ── Variáveis CSS do Tema EduTrack AI ── */
    :root {{
        --primary:         {t['primary']};
        --secondary:       {t['secondary']};
        --accent:          {t['accent']};
        --sidebar-bg:      {t['sidebar_bg']};
        --sidebar-text:    {t['sidebar_text']};
        --text-main:       {t['text_main']};
        --text-muted:      {t['text_muted']};
        --bg-main:         {t['bg_main']};
        --banner-grad:     {t['banner_grad']};
        --banner-title:    {t['banner_title']};
        --card-top:        {t['card_top']};
        --btn-text-color:  {btn_text};
        --font-family:     {font_family};
    }}

    /* ── Tipografia Global (apenas elementos de texto, não ícones internos) ── */
    html, body, .stApp {{
        font-family: {font_family} !important;
    }}
    p, h1, h2, h3, h4, h5, h6, label,
    input, select, textarea,
    .stMarkdown, .stText,
    .stButton > button,
    .stSelectbox, .stTextInput, .stNumberInput,
    .stExpander summary p,
    [data-testid="stMarkdownContainer"] {{
        font-family: {font_family} !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']} !important;
        border-right: 1px solid {t['accent']}44 !important;
    }}
    {sidebar_text_css}

    /* ── Botões Principais — estado normal (borda colorida, texto escuro) ── */
    .stButton > button {{
        border-color: {t['primary']} !important;
        font-family: {font_family} !important;
        transition: all 0.2s ease !important;
    }}
    /* ── Botões ao passar o mouse (fundo primário, texto do tema) ── */
    .stButton > button:hover {{
        background-color: {t['primary']} !important;
        color: {btn_text} !important;
        border-color: {t['primary']} !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px {t['primary']}44 !important;
    }}
    /* ── Botões tipo "primary" (sempre fundo cheio) ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background-color: {t['primary']} !important;
        color: {btn_text} !important;
        border-color: {t['primary']} !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {{
        background-color: {t['secondary']} !important;
        color: {btn_text} !important;
    }}

    /* ── Links e Seleções Ativas ── */
    a {{
        color: {t['primary']} !important;
    }}

    /* ── Tabs Ativas ── */
    [data-baseweb="tab"][aria-selected="true"] {{
        border-bottom-color: {t['primary']} !important;
        color: {t['primary']} !important;
    }}

    /* ── Inputs com Foco ── */
    [data-baseweb="input"]:focus-within {{
        border-color: {t['primary']} !important;
        box-shadow: 0 0 0 2px {t['primary']}33 !important;
    }}

    /* ── Progress e Spinners ── */
    .stProgress > div > div {{
        background-color: {t['primary']} !important;
    }}

    /* ── Cabeçalho do App ── */
    header[data-testid="stHeader"] {{
        background-color: {t['sidebar_bg']}dd !important;
    }}

    {dark_overrides}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

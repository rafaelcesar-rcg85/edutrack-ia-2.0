import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.api import api_get_all_events, api_get_users

st.title("Atividade dos Usuários")

if st.session_state.get('user_role') != 'admin':
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

# ── Carrega dados ──────────────────────────────────────────────────────────────
with st.spinner("Carregando dados do event log..."):
    events = api_get_all_events()
    users  = api_get_users()

if not events:
    st.info("Nenhum evento encontrado no event log.")
    st.stop()

# ── Prepara o DataFrame base ───────────────────────────────────────────────────
def extract_uid(val):
    return val.get('id') if isinstance(val, dict) else val

def parse_ts(val):
    if val is None:
        return pd.NaT
    try:
        return pd.to_datetime(int(val), unit='ms', utc=True)
    except Exception:
        return pd.to_datetime(val, errors='coerce', utc=True)

users_map = {u['id']: u for u in users} if users else {}

df = pd.DataFrame(events)
df['uid']        = df['user_id'].apply(extract_uid)
df['created_at'] = df['created_at'].apply(parse_ts)
df['action']     = df['action'].astype(str)
df['Nome']       = df['uid'].apply(lambda x: users_map.get(x, {}).get('name',  f'ID {x}'))
df['E-mail']     = df['uid'].apply(lambda x: users_map.get(x, {}).get('email', ''))

# Separações por tipo de ação
df_login  = df[df['action'] == 'login'].copy()
df_signup = df[df['action'] == 'signup'].copy()

# ── 1. Ranking de Logins ───────────────────────────────────────────────────────
st.subheader("🏆 Ranking de Logins")
login_rank = (
    df_login.groupby(['uid', 'Nome', 'E-mail'])
    .agg(total_logins=('created_at', 'count'), ultimo_login=('created_at', 'max'))
    .reset_index()
    .sort_values('total_logins', ascending=False)
)
login_rank['Último Login'] = login_rank['ultimo_login'].dt.strftime('%d/%m/%Y %H:%M')
login_rank = login_rank.rename(columns={'total_logins': 'Total de Logins'})
st.dataframe(login_rank[['Nome', 'E-mail', 'Total de Logins', 'Último Login']], use_container_width=True)

# ── 2. Crescimento de Usuários ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Crescimento de Usuários (Cadastros por Mês)")
if not df_signup.empty:
    df_signup['mes'] = df_signup['created_at'].dt.to_period('M').astype(str)
    growth = df_signup.groupby('mes').size().reset_index(name='Novos Usuários')
    growth = growth.rename(columns={'mes': 'Mês'}).set_index('Mês')
    st.line_chart(growth)
else:
    st.info("Sem dados de cadastro encontrados.")

# ── 3. Usuários Inativos (sem login nos últimos 30 dias) ───────────────────────
st.markdown("---")
st.subheader("😴 Usuários Inativos (sem login nos últimos 30 dias)")
limite = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
ultimo_login_por_user = (
    df_login.groupby('uid')['created_at'].max().reset_index()
)
ultimo_login_por_user.columns = ['uid', 'ultimo_login']

# Todos os usuários que aparecem no event_log
todos_uids = df['uid'].unique()
inativos = []
for uid in todos_uids:
    row = ultimo_login_por_user[ultimo_login_por_user['uid'] == uid]
    if row.empty or row.iloc[0]['ultimo_login'] < limite:
        u = users_map.get(uid, {})
        last = row.iloc[0]['ultimo_login'].strftime('%d/%m/%Y') if not row.empty else 'Nunca'
        inativos.append({
            'Nome':        u.get('name', f'ID {uid}'),
            'E-mail':      u.get('email', ''),
            'Último Login': last
        })

if inativos:
    st.dataframe(pd.DataFrame(inativos), use_container_width=True)
else:
    st.success("Todos os usuários fizeram login nos últimos 30 dias! ✅")

# ── 4. Horários de Pico ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⏰ Horários de Pico de Acesso")
if not df_login.empty:
    df_login['hora'] = df_login['created_at'].dt.hour
    pico = df_login.groupby('hora').size().reset_index(name='Logins')
    pico['Hora'] = pico['hora'].apply(lambda h: f"{h:02d}:00")
    pico = pico[['Hora', 'Logins']].set_index('Hora')
    st.bar_chart(pico)
else:
    st.info("Sem dados de login para calcular picos.")

# ── 5. Perfil de Uso por Usuário ───────────────────────────────────────────────
st.markdown("---")
st.subheader("👤 Perfil de Uso por Usuário")
perfil = (
    df.groupby(['Nome', 'action'])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
st.dataframe(perfil, use_container_width=True)

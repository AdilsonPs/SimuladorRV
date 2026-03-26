# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# Configuração da página para um visual de App
st.set_page_config(page_title="Sales Pulse | Softys", layout="wide")

# --- ESTILO CUSTOMIZADO (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 5px 5px 0 0;
        padding: 0 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NEGÓCIO ---
def calc_payout(atig):
    if atig < 90: return 0.0
    if atig >= 115: return 1.50
    return 0.8 + (atig - 90) * (0.02) if atig < 100 else 1.0 + (atig - 100) * (0.0333)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ SalesPulse")
    st.subheader("Configurações Base")
    sal_fixo = st.number_input("Salário Base (R$)", value=7990.84)
    target_p = st.number_input("Target RV (%)", value=43.0) / 100
    st.divider()
    page = st.radio("Navegar por:", ["📊 Dashboard de Ganhos", "📝 Lançar Metas"])

# --- DATABASE EM SESSÃO ---
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
cats = ["NS Adulto", "NS Infantil", "NS Toiletries", "Vol Adulto", "Vol Infantil", "Vol Toiletries"]
pesos = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]

if 'db' not in st.session_state:
    # Iniciando com 100% de atingimento para visualização inicial
    st.session_state.db = {m: {c: {"meta": 100.0, "real": 100.0} for c in cats} for m in meses}

# --- TELAS ---

if page == "📝 Lançar Metas":
    st.header("Lançamento de Performance")
    m_sel = st.selectbox("Selecione o Mês", meses)
    
    with st.container():
        cols = st.columns(3)
        for i, c in enumerate(cats):
            with cols[i % 3]:
                st.markdown(f"**{c}**")
                st.session_state.db[m_sel][c]["meta"] = st.number_input("Meta", key=f"m{i}", value=st.session_state.db[m_sel][c]["meta"])
                st.session_state.db[m_sel][c]["real"] = st.number_input("Real", key=f"r{i}", value=st.session_state.db[m_sel][c]["real"])
    st.success("Dados atualizados automaticamente.")

else:
    st.title("📊 Resumo de Remuneração")
    
    # Processar dados
    res = []
    for m in meses:
        fator_payout = 0
        for i, c in enumerate(cats):
            meta = st.session_state.db[m][c]["meta"]
            real = st.session_state.db[m][c]["real"]
            atig = (real/meta)*100 if meta > 0 else 0
            fator_payout += (calc_payout(atig) * pesos[i])
        
        rv = (sal_fixo * target_p) * fator_payout
        res.append({"Mês": m, "Fixo": sal_fixo, "Variável": rv, "Total": sal_fixo + rv})
    
    df = pd.DataFrame(res)
    
    # KPIs SUPERIORES (Clean Cards)
    c1, c2, c3 = st.columns(3)
    c1.metric("Receita Total Ano (Bruto)", f"R$ {df['Total'].sum():,.2f}")
    c2.metric("Média Mensal (Fixo + RV)", f"R$ {df['Total'].mean():,.2f}")
    c3.metric("Total Variável (Bônus)", f"R$ {df['Variável'].sum():,.2f}")

    st.divider()

    # ABAS DE VISUALIZAÇÃO
    tab_graf, tab_tri = st.tabs(["📉 Evolução Mensal", "🏢 Visão por Quarter (Q)"])
    
    with tab_graf:
        st.subheader("Composição de Renda Mensal")
        st.bar_chart(df.set_index("Mês")[["Fixo", "Variável"]])
    
    with tab_tri:
        st.subheader("Fechamento de Recuperação Trimestral")
        df['Q'] = ["Q1", "Q1", "Q1", "Q2", "Q2", "Q2", "Q3", "Q3", "Q3", "Q4", "Q4", "Q4"]
        q_view = df.groupby('Q')[["Fixo", "Variável", "Total"]].sum()
        st.dataframe(q_view.style.format("R$ {:,.2f}"), use_container_width=True)

st.divider()
st.caption("SalesPulse v2.0 | Dados baseados na Política Softys 2026")

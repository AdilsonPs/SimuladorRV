# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Sales Pulse Prime", layout="wide")

# --- ESTILO DASHBOARD CLEAN ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 12px;
    }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CÁLCULO POLÍTICA 2026 ---
def calc_payout(atig):
    if atig < 90: return 0.0
    if atig >= 115: return 1.50
    return 0.8 + (atig - 90) * 0.02 if atig < 100 else 1.0 + (atig - 100) * 0.0333

# --- ESTRUTURA FIXA ---
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
# Categorias simplificadas para evitar erros de digitação
categorias = ["NS Adulto", "NS Infantil", "NS Toiletries", "Vol Adulto", "Vol Infantil", "Vol Toiletries"]
pesos = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]

# Inicialização do Banco de Dados
if 'db' not in st.session_state:
    st.session_state.db = {m: {c: {"meta": 100.0, "real": 100.0} for c in categorias} for m in meses}

# --- MENU LATERAL ---
with st.sidebar:
    st.title("🛡️ SalesPulse")
    salario_fixo = st.number_input("Salário Fixo (R$)", value=7990.84)
    target_rv_p = st.number_input("Target RV (%)", value=43.0) / 100
    st.divider()
    page = st.radio("Navegação", ["📊 Dashboard", "📝 Lançar Dados"])

# --- PÁGINA: LANÇAMENTO ---
if page == "📝 Lançar Dados":
    st.header("Entrada de Resultados")
    m_sel = st.selectbox("Escolha o Mês", meses)
    
    with st.container():
        st.subheader(f"Indicadores de {m_sel}")
        col1, col2 = st.columns(2)
        for i, c in enumerate(categorias):
            target_col = col1 if i < 3 else col2
            with target_col:
                st.write(f"**{c}**")
                st.session_state.db[m_sel][c]["meta"] = st.number_input("Meta", key=f"m_{m_sel}_{i}", value=st.session_state.db[m_sel][c]["meta"])
                st.session_state.db[m_sel][c]["real"] = st.number_input("Real", key=f"r_{m_sel}_{i}", value=st.session_state.db[m_sel][c]["real"])

# --- PÁGINA: DASHBOARD ---
else:
    st.title("📊 Resumo de Performance")
    
    # Processamento
    dados_proc = []
    for m in meses:
        fator_mes = 0
        for i, c in enumerate(categorias):
            m_val = st.session_state.db[m][c]["meta"]
            r_val = st.session_state.db[m][c]["real"]
            ating = (r_val / m_val) * 100 if m_val > 0 else 0
            fator_mes += (calc_payout(ating) * pesos[i])
        
        rv_valor = (salario_fixo * target_rv_p) * fator_mes
        dados_proc.append({"Mês": m, "Fixo": salario_fixo, "RV": rv_valor, "Total": salario_fixo + rv_valor})
    
    df = pd.DataFrame(dados_proc)
    
    # KPIs DE TOPO
    c1, c2, c3 = st.columns(3)
    c1.metric("Fixo + RV (Acumulado Ano)", f"R$ {df['Total'].sum():,.2f}")
    c2.metric("Média Mensal", f"R$ {df['Total'].mean():,.2f}")
    c3.metric("Total Bônus (RV)", f"R$ {df['RV'].sum():,.2f}")

    st.divider()

    # ABAS
    t_evol, t_tri = st.tabs(["📉 Evolução Mensal", "🏢 Fechamento Quarter (Q)"])
    
    with t_evol:
        st.subheader("Ganhos por Mês")
        # Gráfico limpo
        st.bar_chart(df.set_index("Mês")[["Fixo", "RV"]], color=["#94a3b8", "#3b82f6"])
        
        # Tabela Detalhada Mensal
        st.dataframe(df.style.format({"Fixo": "R$ {:.2f}", "RV": "R$ {:.2f}", "Total": "R$ {:.2f}"}), use_container_width=True)

    with t_tri:
        st.subheader("Simulação de Recuperação Trimestral")
        df['Q'] = ["Q1", "Q1", "Q1", "Q2", "Q2", "Q2", "Q3", "Q3", "Q3", "Q4", "Q4", "Q4"]
        # Agrupando por Quarter
        df_q = df.groupby('Q')[["Fixo", "RV", "Total"]].sum()
        st.table(df_q.style.format("R$ {:,.2f}"))

st.divider()
st.caption("Sales Pulse Prime | Versão 3.0 | Softys Falcon")

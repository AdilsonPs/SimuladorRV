# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime

# Configurações de layout estilo Web App
st.set_page_config(page_title="Sales Pulse Prime", layout="wide", initial_sidebar_state="expanded")

# --- ESTILIZAÇÃO CSS (Para parecer um App moderno) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

# --- LÓGICA DE CURVA SOFTYS ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100: return 0.8 + (atingimento - 90) * (0.02)
    return 1.0 + (atingimento - 100) * (0.0333)

# --- SIDEBAR (MENU DE NAVEGAÇÃO) ---
with st.sidebar:
    st.title("🚀 SalesPulse")
    menu = st.radio("Navegação", ["Dashboard Geral", "Lançar Resultados", "Configurações"])
    st.divider()
    salario_base = st.number_input("Salário Fixo (R$)", value=7990.84)
    target_rv = st.slider("Target RV (%)", 0, 100, 43) / 100
    st.caption(f"Target calculado: R$ {(salario_base * target_rv):,.2f}")

# --- ESTRUTURA DE DADOS ---
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
categorias = ["Net Sales Adulto", "Net Sales Infantil", "Net Sales Toiletries", "Vol Adulto", "Vol Infantil", "Vol Toiletries"]
pesos = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]

if 'db' not in st.session_state:
    st.session_state.db = {m: {cat: {"meta": 100000.0, "real": 105000.0} for cat in categorias} for m in meses}

# --- TELAS ---

if menu == "Lançar Resultados":
    st.header("📝 Lançamento de Performance")
    col_m, _ = st.columns([2, 4])
    mes_ref = col_m.selectbox("Mês de Referência", meses)
    
    with st.form("form_dados"):
        st.subheader(f"Indicadores de {mes_ref}")
        for i, cat in enumerate(categorias):
            c1, c2 = st.columns(2)
            st.session_state.db[mes_ref][cat]["meta"] = c1.number_input(f"Meta {cat}", value=st.session_state.db[mes_ref][cat]["meta"])
            st.session_state.db[mes_ref][cat]["real"] = c2.number_input(f"Real {cat}", value=st.session_state.db[mes_ref][cat]["real"])
        st.form_submit_button("Salvar e Atualizar Dashboard")

elif menu == "Dashboard Geral":
    st.header("📊 Executive Overview")
    
    # Processar dados para o dashboard
    resumo = []
    for m in meses:
        ganho_rv_mes = 0
        for i, cat in enumerate(categorias):
            m_val = st.session_state.db[m][cat]["meta"]
            r_val = st.session_state.db[m][cat]["real"]
            ating = (r_val / m_val) * 100 if m_val > 0 else 0
            ganho_rv_mes += (calcular_payout(ating) * pesos[i] * (salario_base * target_rv))
        
        resumo.append({"Mês": m, "Fixo": salario_base, "Variável": ganho_rv_mes, "Total": salario_base + ganho_rv_mes})
    
    df = pd.DataFrame(resumo)
    
    # KPIs Superiores
    k1, k2, k3, k4 = st.columns(4)
    total_ano = df["Total"].sum()
    rv_media = df["Variável"].mean()
    k1.metric("Renda Total Ano", f"R$ {total_ano:,.2f}")
    k2.metric("Média RV Mensal", f"R$ {rv_media:,.2f}")
    k3.metric("Melhor Mês", df.loc[df['Total'].idxmax()]['Mês'])
    k4.metric("Target RV", f"{target_rv*100:.1f}%")

    # Gráficos
    st.subheader("Tendência de Recebimento (Fixo vs Variável)")
    st.bar_chart(df.set_index("Mês")[["Fixo", "Variável"]])

    # Tabela de Detalhes Estilizada
    st.subheader("Detalhamento por Quarter")
    df['Quarter'] = [f"Q{(i//3)+1}" for i in range(12)]
    tabela_q = df.groupby('Quarter')[["Fixo", "Variável", "Total"]].sum()
    st.table(tabela_q.style.format("R$ {:,.2f}"))

elif menu == "Configurações":
    st.header("⚙️ Configurações do Sistema")
    st.write("Aqui você pode ajustar parâmetros globais da política.")
    st.checkbox("Habilitar Recuperação Trimestral Automática", value=True)
    st.button("Limpar Todos os Dados")

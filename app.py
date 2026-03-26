# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# Layout configurado para modo Wide (estilo Dashboard Profissional)
st.set_page_config(page_title="Sales Pulse Prime", layout="wide", initial_sidebar_state="expanded")

# --- CORREÇÃO DO ESTILO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 22px; color: #1e293b; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #0f172a; }
    </style>
    """, unsafe_allow_html=True) # <-- AQUI ESTAVA O ERRO (CORRIGIDO)

# --- FUNÇÕES DE CÁLCULO ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100: return 0.8 + (atingimento - 90) * (0.02)
    return 1.0 + (atingimento - 100) * (0.0333)

# --- SIDEBAR (CONFIGURAÇÃO) ---
with st.sidebar:
    st.title("📂 Menu")
    aba = st.radio("Ir para:", ["📊 Dashboard Prime", "📝 Lançar Resultados", "⚙️ Ajustes de Salário"])
    st.divider()
    
    # Valores globais
    salario_fixo = st.number_input("Meu Salário Fixo (R$)", value=7990.84)
    target_rv_p = st.number_input("Meu Target RV (%)", value=43.0) / 100
    st.caption(f"Valor do Target: R$ {(salario_fixo * target_rv_p):,.2f}")

# --- BANCO DE DADOS TEMPORÁRIO ---
meses_lista = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
cats = ["Net Sales Adulto", "Net Sales Infantil", "Net Sales Toiletries", "Vol Adulto", "Vol Infantil", "Vol Toiletries"]
pesos = [0.20, 0.15, 0.15, 0.20, 0.15, 0.15]

if 'db' not in st.session_state:
    st.session_state.db = {m: {c: {"meta": 100.0, "real": 100.0} for c in cats} for m in meses_lista}

# --- TELAS ---

if aba == "📝 Lançar Resultados":
    st.header("Lançamento de Metas e Realizados")
    m_ref = st.selectbox("Selecione o Mês", meses_lista)
    
    with st.form("form_vendas"):
        cols = st.columns(2)
        for i, c in enumerate(cats):
            col_idx = 0 if i < 3 else 1
            with cols[col_idx]:
                st.write(f"**{c}**")
                st.session_state.db[m_ref][c]["meta"] = st.number_input(f"Meta ({c})", value=st.session_state.db[m_ref][c]["meta"], key=f"m{i}")
                st.session_state.db[m_ref][c]["real"] = st.number_input(f"Real ({c})", value=st.session_state.db[m_ref][c]["real"], key=f"r{i}")
        st.form_submit_button("Atualizar Sistema")

elif aba == "📊 Dashboard Prime":
    st.title("📈 Performance Sales Pulse")
    
    # Processamento dos Dados
    resumo_mês = []
    for m in meses_lista:
        soma_fator_payout = 0
        for i, c in enumerate(cats):
            meta = st.session_state.db[m][c]["meta"]
            real = st.session_state.db[m][c]["real"]
            ating = (real/meta)*100 if meta > 0 else 0
            soma_fator_payout += (calcular_payout(ating) * pesos[i])
        
        v_rv = (salario_fixo * target_rv_p) * soma_fator_payout
        resumo_mês.append({"Mês": m, "Fixo": salario_fixo, "Variável": v_rv, "Total": salario_fixo + v_rv})
    
    df = pd.DataFrame(resumo_mês)
    
    # Cards Superiores
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ganhos Totais (Ano)", f"R$ {df['Total'].sum():,.2f}")
    c2.metric("Média Mensal", f"R$ {df['Total'].mean():,.2f}")
    c3.metric("Total Variável", f"R$ {df['Variável'].sum():,.2f}")
    c4.metric("Atingimento Médio", f"{((df['Variável'].sum()/(salario_fixo*target_rv_p*12))*100):,.1f}%")

    st.divider()
    
    # Gráfico Principal
    st.subheader("Evolução Mensal: Salário + Variável")
    st.bar_chart(df.set_index("Mês")[["Fixo", "Variável"]])

    # Tabela de Quarters (Recuperação)
    st.subheader("Consolidado Trimestral (Recuperação Q)")
    df['Q'] = ["Q1", "Q1", "Q1", "Q2", "Q2", "Q2", "Q3", "Q3", "Q3", "Q4", "Q4", "Q4"]
    df_q = df.groupby('Q')[["Fixo", "Variável", "Total"]].sum()
    st.table(df_q.style.format("R$ {:,.2f}"))

elif aba == "⚙️ Ajustes de Salário":
    st.header("Configurações do Perfil")
    st.write("Ajuste aqui seus dados contratuais para que o simulador reflita sua realidade.")
    st.info("As regras de curva (90% a 115%) seguem a Política Softys 2026.")

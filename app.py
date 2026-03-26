# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Remuneração Softys", layout="wide")

# --- FUNÇÕES DE CÁLCULO ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100:
        return 0.8 + (atingimento - 90) * (0.2 / 10)
    else:
        return 1.0 + (atingimento - 100) * (0.5 / 15)

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    salario_base = st.number_input("Salário Fixo Mensal (R$)", value=7990.84, step=100.0)
    target_percentual = st.number_input("Target da Variável (%)", value=43.0, step=1.0) / 100
    st.info(f"Seu Target é de {target_percentual:.2%} do salário.")

# --- ESTRUTURA DE DADOS ---
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
categorias = [
    {"nome": "Net Sales Adulto", "peso": 0.20},
    {"nome": "Net Sales Infantil", "peso": 0.15},
    {"nome": "Net Sales Toiletries", "peso": 0.15},
    {"nome": "Volume Adulto", "peso": 0.20},
    {"nome": "Volume Infantil", "peso": 0.15},
    {"nome": "Volume Toiletries", "peso": 0.15},
]

dados_calculados = []

# --- ABAS ---
tab_meses, tab_trimestres, tab_anual = st.tabs(["📅 Lançamento Mensal", "📊 Recuperação Trimestral (Q)", "🏆 Resumo Anual"])

# ABA 1: LANÇAMENTO MENSAL
with tab_meses:
    col_sel_mes, _ = st.columns([1, 2])
    mes_selecionado = col_sel_mes.selectbox("Selecione o mês para editar:", meses)
    
    for i, nome_mes in enumerate(meses):
        soma_payout_mes = 0
        with st.expander(f"Dados de {nome_mes}", expanded=(nome_mes == mes_selecionado)):
            c1, c2 = st.columns(2)
            for idx, cat in enumerate(categorias):
                col = c1 if idx < 3 else c2
                with col:
                    st.write(f"**{cat['nome']}**")
                    m = st.number_input("Meta", key=f"m_{i}_{idx}", value=100.0)
                    r = st.number_input("Real", key=f"r_{i}_{idx}", value=100.0)
                    ating = (r / m) * 100 if m > 0 else 0
                    payout_f = calcular_payout(ating)
                    soma_payout_mes += (payout_f * cat['peso'])
            
            # Cálculo financeiro do mês
            valor_variavel = (salario_base * target_percentual) * soma_payout_mes
            total_recebido = salario_base + valor_variavel
            
            dados_calculados.append({
                "Mês": nome_mes,
                "Atingimento Médio": soma_payout_mes,
                "Salário Fixo": salario_base,
                "Variável Bruta": valor_variavel,
                "Total (Fixo + RV)": total_recebido,
                "Tri": (i // 3) + 1
            })
            
            st.success(f"**{nome_mes}:** Fixo R$ {salario_base:,.2f} + RV R$ {valor_variavel:,.2f} = **Total: R$ {total_recebido:,.2f}**")

df = pd.DataFrame(dados_calculados)

# ABA 2: RECUPERAÇÃO TRIMESTRAL (Q)
with tab_trimestres:
    st.header("Análise de Recuperação por Quarter")
    
    for q in range(1, 5):
        df_q = df[df["Tri"] == q]
        st.subheader(f"{q}º Trimestre (Q{q})")
        
        # Simulação de Recuperação: 
        # Na regra da Softys, se o atingimento do tri for maior que a soma dos meses, paga-se a diferença.
        total_fixo_q = df_q["Salário Fixo"].sum()
        total_rv_q = df_q["Variável Bruta"].sum()
        total_geral_q = df_q["Total (Fixo + RV)"].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Total Fixo Q{q}", f"R$ {total_fixo_q:,.2f}")
        c2.metric(f"Total Variável Q{q}", f"R$ {total_rv_q:,.2f}")
        c3.metric(f"Recebimento Total Q{q}", f"R$ {total_geral_q:,.2f}")
        st.divider()

# ABA 3: RESUMO ANUAL
with tab_anual:
    st.header("Resultado Consolidado 2026")
    
    total_fixo_ano = df["Salário Fixo"].sum()
    total_rv_ano = df["Variável Bruta"].sum()
    total_ano = df["Total (Fixo + RV)"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Salário Fixo Anual", f"R$ {total_fixo_ano:,.2f}")
    col2.metric("Variável Total Anual", f"R$ {total_rv_ano:,.2f}")
    col3.metric("RENDA TOTAL ANUAL", f"R$ {total_ano:,.2f}", delta="Estimado")

    st.subheader("Gráfico de Recebimento Mensal")
    st.bar_chart(df.set_index("Mês")[["Salário Fixo", "Variável Bruta"]])

st.divider()
st.caption("Nota: Este simulador considera valores brutos. Descontos de folha (INSS/IRRF) não estão inclusos.")

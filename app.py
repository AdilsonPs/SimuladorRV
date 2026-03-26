# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Softys Falcon 2026", layout="wide")

# --- LÓGICA DE CÁLCULO (POLÍTICA 2026) ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100:
        return 0.8 + (atingimento - 90) * (0.2 / 10)
    else:
        return 1.0 + (atingimento - 100) * (0.5 / 15)

def calcular_bloco(meta, realizado, peso_relativo):
    atingimento = (realizado / meta) * 100 if meta > 0 else 0
    payout_fator = calcular_payout(atingimento)
    # O peso final no salário depende do target (0.43) e do peso da categoria
    salarios = 0.43 * peso_relativo * payout_fator
    return atingimento, salarios

# --- INTERFACE ---
st.title("🚀 Simulador de Performance Comercial Softys")
st.sidebar.header("Configurações de Perfil")
salario_base = st.sidebar.number_input("Salário Base (R$)", value=7990.84)

# Estrutura de dados para armazenar os meses
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
categorias = [
    {"nome": "Net Sales Adulto", "peso": 0.20},
    {"nome": "Net Sales Infantil", "peso": 0.15},
    {"nome": "Net Sales Toiletries", "peso": 0.15},
    {"nome": "Volume Adulto", "peso": 0.20},
    {"nome": "Volume Infantil", "peso": 0.15},
    {"nome": "Volume Toiletries", "peso": 0.15},
]

historico = []

# Abas por Trimestre
abas_tri = st.tabs(["1º Trimestre", "2º Trimestre", "3º Trimestre", "4º Trimestre", "Resumo Anual"])

for i, tri in enumerate(abas_tri[:4]):
    with tri:
        cols_meses = st.columns(3)
        for j in range(3):
            mes_idx = i * 3 + j
            nome_mes = meses[mes_idx]
            
            with cols_meses[j]:
                with st.expander(f"📊 Dados de {nome_mes}", expanded=(j==0)):
                    salario_acumulado_mes = 0
                    for cat in categorias:
                        st.caption(f"**{cat['nome']}** (Peso {int(cat['peso']*100)}%)")
                        m = st.number_input(f"Meta", key=f"m_{mes_idx}_{cat['nome']}", value=100.0)
                        r = st.number_input(f"Real", key=f"r_{mes_idx}_{cat['nome']}", value=100.0)
                        
                        atig, sal = calcular_bloco(m, r, cat['peso'])
                        salario_acumulado_mes += sal
                    
                    st.metric("Total Mês (Salários)", f"{salario_acumulado_mes:.3f}")
                    historico.append({"mes": nome_mes, "salarios": salario_acumulado_mes, "tri": i+1})

# --- ABA RESUMO ANUAL E RECUPERAÇÃO ---
with abas_tri[4]:
    st.header("Análise Consolidada")
    df = pd.DataFrame(historico)
    
    col_an1, col_an2 = st.columns(2)
    
    total_salarios_ano = df['salarios'].sum()
    col_an1.metric("Acumulado do Ano (Salários)", f"{total_salarios_ano:.3f}")
    col_an1.metric("Total em Dinheiro", f"R$ {(total_salarios_ano * salario_base):,.2f}")

    # Gráfico simples de evolução
    st.subheader("Evolução Mensal")
    st.line_chart(df.set_index('mes')['salarios'])

    st.info("""
    **Nota sobre Recuperação:** O sistema de recuperação trimestral compara a média do seu atingimento no bloco de 3 meses 
    contra o que foi pago individualmente. Se o consolidado for maior, a diferença é paga no fechamento do trimestre.
    """)

# Rodapé Fixo
st.divider()
st.markdown(f"**Target Simulado:** 0.43 salários | **Status:** Aguardando fechamento oficial.")

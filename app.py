# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Softys 2026", layout="wide")

# --- LÓGICA DE CÁLCULO (POLÍTICA 2026) ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100:
        return 0.8 + (atingimento - 90) * (0.2 / 10)
    else:
        return 1.0 + (atingimento - 100) * (0.5 / 15)

# --- INTERFACE ---
st.title("📊 Simulador de Pagamentos Softys")
st.sidebar.header("Dados Cadastrais")
salario_base = st.sidebar.number_input("Salário Base (R$)", value=7990.84)
target_rv = 0.43 # Conforme extrato

meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
categorias = [
    {"nome": "Net Sales Adulto", "peso": 0.20},
    {"nome": "Net Sales Infantil", "peso": 0.15},
    {"nome": "Net Sales Toiletries", "peso": 0.15},
    {"nome": "Volume Adulto", "peso": 0.20},
    {"nome": "Volume Infantil", "peso": 0.15},
    {"nome": "Volume Toiletries", "peso": 0.15},
]

# Dicionário para guardar os resultados
resultados_mensais = []

# Abas por Trimestre
abas_tri = st.tabs(["1º Tri", "2º Tri", "3º Tri", "4º Tri", "💰 Resumo de Recebimento"])

for i, tri_aba in enumerate(abas_tri[:4]):
    with tri_aba:
        cols = st.columns(3)
        for j in range(3):
            mes_idx = i * 3 + j
            nome_mes = meses[mes_idx]
            with cols[j]:
                with st.expander(f"Editar {nome_mes}", expanded=False):
                    soma_payout_pesado = 0
                    for cat in categorias:
                        st.write(f"**{cat['nome']}**")
                        m = st.number_input("Meta", key=f"m_{mes_idx}_{cat['nome']}", value=100.0)
                        r = st.number_input("Real", key=f"r_{mes_idx}_{cat['nome']}", value=100.0)
                        
                        ating = (r / m) * 100 if m > 0 else 0
                        payout_fator = calcular_payout(ating)
                        soma_payout_pesado += (payout_fator * cat['peso'])
                    
                    # Cálculo final do mês
                    total_salarios_mes = target_rv * soma_payout_pesado
                    valor_reais_mes = total_salarios_mes * salario_base
                    
                    resultados_mensais.append({
                        "Mês": nome_mes,
                        "Salários": round(total_salarios_mes, 3),
                        "Valor (R$)": round(valor_reais_mes, 2),
                        "Previsão PGTO": "Mês seguinte"
                    })
                    st.metric("Total no Mês", f"R$ {valor_reais_mes:,.2f}")

# --- ABA DE PAGAMENTOS (A MAIS IMPORTANTE AGORA) ---
with abas_tri[4]:
    st.header("Cronograma de Recebimento")
    df_pagos = pd.DataFrame(resultados_mensais)
    
    # Exibir Tabela Detalhada
    st.table(df_pagos)
    
    # Resumos em Cards
    c1, c2, c3 = st.columns(3)
    total_acumulado = df_pagos["Valor (R$)"].sum()
    c1.metric("Total Acumulado (Ano)", f"R$ {total_acumulado:,.2f}")
    c2.metric("Média Mensal", f"R$ {(total_acumulado/12):,.2f}")
    c3.metric("Maior Recebimento", f"R$ {df_pagos['Valor (R$)'].max():,.2f}")

    st.subheader("Visualização por Mês de Caixa")
    st.bar_chart(df_pagos.set_index("Mês")["Valor (R$)"])
    
    st.warning("⚠️ Lembre-se: Os valores acima são brutos. Incidem descontos de IRRF e INSS conforme a folha.")

# Rodapé
st.divider()
st.caption("Desenvolvido para simulação de metas Softys Falcon 2026.")

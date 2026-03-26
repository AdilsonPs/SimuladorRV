# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Simulador de RV - Softys Falcon", layout="wide")

def calcular_payout(atingimento):
    """Aplica a curva de atingimento da política 2026"""
    if atingimento < 90:
        return 0.0
    elif atingimento >= 115:
        return 1.50
    else:
        if atingimento < 100:
            return 0.8 + (atingimento - 90) * (0.2 / 10)
        else:
            return 1.0 + (atingimento - 100) * (0.5 / 15)

st.title("📊 Simulador de Remuneração Variável")
st.markdown("Baseado na Política 2026 - Softys")

with st.sidebar:
    st.header("Configurações Base")
    salario_base = st.number_input("Salário Base (R$)", value=7990.84)
    target_rv = 0.43 
    st.info(f"Target: {target_rv} salários")

# Interface Simples para teste
mes = st.selectbox("Selecione o Mês", ["Janeiro", "Fevereiro", "Março"])
meta = st.number_input(f"Meta de Net Sales ({mes})", min_value=1.0, value=240500.0)
real = st.number_input(f"Realizado de Net Sales ({mes})", min_value=0.0, value=317140.0)

atig = (real / meta) * 100
payout = calcular_payout(atig)
resultado = (salario_base * target_rv) * payout

st.metric("Atingimento", f"{atig:.2f}%")
st.success(f"Valor Estimado: R$ {resultado:,.2f}")

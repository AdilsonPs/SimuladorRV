import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PriceLens - Resumo Anual", layout="wide")

# --- SIMULAÇÃO DE DADOS (Substitua pela sua chamada de API/Base44) ---
def load_data():
    # Simulando os meses
    months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    # Dados fictícios de exemplo (Substitua pelos dados do seu profile/results)
    data = {
        "Mês": months,
        "Meta_RV": [10000, 10000, 12000, 12000, 12000, 15000, 15000, 15000, 18000, 18000, 20000, 25000],
        "Real_RV": [9500, 10500, 11000, 13000, 11500, 14000, 16000, 15500, 17000, 19000, 21000, 24000],
        "Salarios": [1.0, 1.1, 1.0, 1.2, 0.9, 1.0, 1.3, 1.2, 1.1, 1.4, 1.5, 1.8]
    }
    return pd.DataFrame(data)

df = load_data()

# --- CÁLCULOS ESTRATÉGICOS ---
total_real = df["Real_RV"].sum()
total_meta = df["Meta_RV"].sum()
atingimento_anual = (total_real / total_meta) * 100
recuperacao_total = total_real * 0.75  # Exemplo de regra de 75%

# --- CABEÇALHO ---
st.title("📊 Resumo Anual de Performance")
st.markdown(f"Consolidado de metas e recuperação - {datetime.now().year}")

# --- CARDS DE RESUMO (Summary Cards) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("RV Anual (Real)", f"R$ {total_real:,.2f}")
with col2:
    st.metric("Atingimento Global", f"{atingimento_anual:.1f}%", delta=f"{atingimento_anual-100:.1f}%")
with col3:
    st.metric("Total Salários", f"{df['Salarios'].sum():.3f} sal.")
with col4:
    st.metric("Net Recovery (75%)", f"R$ {recuperacao_total:,.2f}")

st.divider()

# --- GRÁFICO META VS REAL (PriceLens View) ---
st.subheader("Realizado vs Meta (Mensal)")

fig = go.Figure()

# Barra de Realizado
fig.add_trace(go.Bar(
    x=df["Mês"],
    y=df["Real_RV"],
    name="RV Real",
    marker_color='#3B82F6'
))

# Linha de Meta
fig.add_trace(go.Scatter(
    x=df["Mês"],
    y=df["Meta_RV"],
    name="Meta Estipulada",
    line=dict(color='#F59E0B', width=4),
    mode='lines+markers'
))

fig.update_layout(
    hovermode="x unified",
    template="plotly_white",
    height=400,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# --- TABELA DE RESULTADOS POR TRIMESTRE (Qs) ---
st.subheader("Detalhamento por Trimestre")

# Lógica para agrupar por Q
df['Q'] = ['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q3', 'Q3', 'Q3', 'Q4', 'Q4', 'Q4']
df_q = df.groupby('Q').agg({
    'Meta_RV': 'sum',
    'Real_RV': 'sum',
    'Salarios': 'sum'
}).reset_index()

df_q['Atingimento (%)'] = (df_q['Real_RV'] / df_q['Meta_RV']) * 100
df_q['Recuperação'] = df_q['Real_RV'] * 0.75

# Formatação para exibição
df_display = df_q.copy()
df_display['Meta_RV'] = df_display['Meta_RV'].map("R$ {:,.2f}".format)
df_display['Real_RV'] = df_display['Real_RV'].map("R$ {:,.2f}".format)
df_display['Recuperação'] = df_display['Recuperação'].map("R$ {:,.2f}".format)
df_display['Atingimento (%)'] = df_display['Atingimento (%)'].map("{:.1f}%".format)

st.table(df_display)

# --- RODAPÉ ---
st.info("💡 Dica: Os valores de recuperação são baseados no atingimento dos gatilhos contratuais de 2026.")

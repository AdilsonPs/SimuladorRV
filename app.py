# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Remuneração Softys", layout="wide")

# --- LÓGICA DE CURVA (POLÍTICA 2026) ---
def calcular_payout(atingimento):
    if atingimento < 90: return 0.0
    if atingimento >= 115: return 1.50
    if atingimento < 100:
        return 0.8 + (atingimento - 90) * (0.2 / 10)
    else:
        return 1.0 + (atingimento - 100) * (0.5 / 15)

# --- CONFIGURAÇÕES NA SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações de Contrato")
    salario_base = st.number_input("Salário Fixo Mensal (R$)", value=7990.84, step=100.0)
    target_rv_percentual = st.number_input("Target da Variável (%)", value=43.0, step=1.0) / 100
    st.info(f"Seu Target é de {target_rv_percentual:.2%} do seu salário base.")

# --- ESTRUTURA DE DADOS ---
meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
categorias = [
    {"nome": "Net Sales Adulto", "peso": 0.20},
    {"nome": "Net Sales Infantil", "peso": 0.15},
    {"nome": "Net Sales Toiletries", "peso": 0.15},
    {"nome": "Volume Adulto", "peso": 0.20},
    {"nome": "Volume Infantil", "peso": 0.15},
    {"nome": "Volume Toiletries", "peso": 0.15},
]

# Inicialização de dados persistentes na sessão (enquanto o navegador estiver aberto)
if 'dados' not in st.session_state:
    st.session_state.dados = {m: {c['nome']: {"meta": 100.0, "real": 100.0} for c in categorias} for m in meses_nomes}

# --- INTERFACE ---
st.title("🚀 Simulador Falcon: Mensal, Trimestral (Q) e Anual")

tab_mensal, tab_trimestral, tab_anual = st.tabs(["📅 Lançamento Mensal", "📊 Recuperação Trimestral (Q)", "🏆 Resultado Anual"])

# --- ABA 1: LANÇAMENTO MENSAL ---
with tab_mensal:
    mes_foco = st.selectbox("Selecione o mês para preencher:", meses_nomes)
    
    st.subheader(f"Entradas de {mes_foco}")
    col1, col2 = st.columns(2)
    
    for idx, cat in enumerate(categorias):
        col = col1 if idx < 3 else col2
        with col:
            st.write(f"**{cat['nome']}** (Peso {int(cat['peso']*100)}%)")
            st.session_state.dados[mes_foco][cat['nome']]["meta"] = st.number_input("Meta", key=f"m_{mes_foco}_{idx}", value=st.session_state.dados[mes_foco][cat['nome']]["meta"])
            st.session_state.dados[mes_foco][cat['nome']]["real"] = st.number_input("Realizado", key=f"r_{mes_foco}_{idx}", value=st.session_state.dados[mes_foco][cat['nome']]["real"])

# --- PROCESSAMENTO DE DADOS ---
lista_meses_proc = []
for m in meses_nomes:
    soma_payout_ponderado = 0
    for cat in categorias:
        meta = st.session_state.dados[m][cat['nome']]["meta"]
        real = st.session_state.dados[m][cat['nome']]["real"]
        ating = (real / meta) * 100 if meta > 0 else 0
        soma_payout_ponderado += (calcular_payout(ating) * cat['peso'])
    
    val_rv = (salario_base * target_rv_percentual) * soma_payout_ponderado
    lista_meses_proc.append({
        "Mês": m,
        "Fixo": salario_base,
        "RV": val_rv,
        "Total": salario_base + val_rv,
        "Payout_Fator": soma_payout_ponderado
    })

df_meses = pd.DataFrame(lista_meses_proc)

# --- ABA 2: RECUPERAÇÃO TRIMESTRAL (Q) ---
with tab_trimestral:
    st.header("Cálculo de Quarter (Q)")
    
    for q in range(4):
        inicio, fim = q*3, q*3 + 3
        meses_q = meses_nomes[inicio:fim]
        df_q = df_meses.iloc[inicio:fim]
        
        # Lógica de Consolidação: Soma as metas e realizados de todas as categorias no tri
        soma_payout_tri = 0
        for cat in categorias:
            m_tri = sum([st.session_state.dados[m][cat['nome']]["meta"] for m in meses_q])
            r_tri = sum([st.session_state.dados[m][cat['nome']]["real"] for m in meses_q])
            atig_tri = (r_tri / m_tri) * 100 if m_tri > 0 else 0
            soma_payout_tri += (calcular_payout(atig_tri) * cat['peso'])
        
        val_rv_tri_total = (salario_base * target_rv_percentual) * soma_payout_tri * 3
        ja_pago_no_tri = df_q["RV"].sum()
        recuperacao = max(0, val_rv_tri_total - ja_pago_no_tri)
        
        with st.expander(f"Q{q+1} ({', '.join(meses_q)})", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Fixo no Q", f"R$ {df_q['Fixo'].sum():,.2f}")
            c2.metric("RV Acumulada", f"R$ {ja_pago_no_tri:,.2f}")
            c3.metric("Recuperação Estimada", f"R$ {recuperacao:,.2f}", delta="A Receber")
            c4.metric("Total Q", f"R$ {(df_q['Total'].sum() + recuperacao):,.2f}")

# --- ABA 3: RESUMO ANUAL ---
with tab_anual:
    st.header("Visão Geral do Ano")
    
    total_fixo = df_meses["Fixo"].sum()
    total_rv = df_meses["RV"].sum()
    
    # Adicionando recuperações ao total anual (simplificado)
    # Aqui você poderia somar as recuperações calculadas na aba anterior
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Salário Fixo Total", f"R$ {total_fixo:,.2f}")
    c2.metric("Variável Total", f"R$ {total_rv:,.2f}")
    c3.metric("RENDA TOTAL ESTIMADA", f"R$ {(total_fixo + total_rv):,.2f}")
    
    st.subheader("Gráfico de Composição de Renda")
    st.bar_chart(df_meses.set_index("Mês")[["Fixo", "RV"]])

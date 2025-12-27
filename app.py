import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, adicionar_transacao, obter_todas_transacoes
from datetime import date

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinDash", layout="wide")

# Inicializar Banco de Dados
init_db()

# --- SIDEBAR: Entrada de Dados ---
st.sidebar.header("Nova Transação")
with st.sidebar.form("form_transacao", clear_on_submit=True):
    data_input = st.date_input("Data", date.today())
    tipo_input = st.selectbox("Tipo", ["Despesa", "Receita"])
    categoria_input = st.selectbox("Categoria", [
        "Alimentação", "Transporte", "Moradia", "Salário",
        "Lazer", "Investimentos", "Saúde", "Outros"
    ])
    descricao_input = st.text_input("Descrição (Opcional)")
    valor_input = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Salvar")

    if submitted:
        adicionar_transacao(data_input, tipo_input,
                            categoria_input, descricao_input, valor_input)
        st.sidebar.success("Adicionado com sucesso!")

# --- CORPO PRINCIPAL: Dashboard ---
st.title("💰 FinDash - Controle Financeiro")

# Carregar Dados do Banco
dados = obter_todas_transacoes()

if dados:
    # Converter para DataFrame do Pandas para facilitar a análise
    df = pd.DataFrame(
        dados, columns=['ID', 'Data', 'Tipo', 'Categoria', 'Descrição', 'Valor'])
    df['Data'] = pd.to_datetime(df['Data'])  # Garantir formato de data

    # --- KPI SECTION (Indicadores) ---
    receita_total = df[df['Tipo'] == 'Receita']['Valor'].sum()
    despesa_total = df[df['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = receita_total - despesa_total

    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas", f"R$ {receita_total:,.2f}")
    col2.metric("Despesas", f"R$ {despesa_total:,.2f}", delta_color="inverse")
    col3.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")

    st.divider()

    # --- GRÁFICOS (Visualização) ---
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("Despesas por Categoria")
        # Filtrar apenas despesas para este gráfico
        df_despesas = df[df['Tipo'] == 'Despesa']
        if not df_despesas.empty:
            fig_pie = px.pie(df_despesas, values='Valor',
                             names='Categoria', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sem despesas registradas para o gráfico.")

    with col_graf2:
        st.subheader("Evolução no Tempo")
        # Agrupar por data e tipo
        df_evolucao = df.groupby(['Data', 'Tipo'])['Valor'].sum().reset_index()
        fig_bar = px.bar(df_evolucao, x='Data', y='Valor',
                         color='Tipo', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- MÓDULO DE ORÇAMENTO (BUDGET) ---
    st.subheader("🎯 Metas do Mês Atual")

    # 1. Definição de Metas
    # (ATENÇÃO: Certifique-se de copiar o fechamento "}" deste dicionário abaixo)
    metas = {
        "Alimentação": 1500.00,
        "Transporte": 800.00,
        "Lazer": 500.00,
        "Moradia": 2500.00
    }

    # 2. Filtrar dados apenas do mês atual
    mes_atual = date.today().month
    ano_atual = date.today().year

    # Criamos colunas auxiliares para filtrar pelo mês
    df['mes'] = df['Data'].dt.month
    df['ano'] = df['Data'].dt.year

    # Filtra apenas despesas do mês e ano correntes
    df_mes_atual = df[(df['mes'] == mes_atual) & (
        df['ano'] == ano_atual) & (df['Tipo'] == 'Despesa')]

    # 3. Gerar Barras de Progresso
    col_meta1, col_meta2 = st.columns(2)

    # Loop para exibir cada meta
    for i, (categoria, valor_meta) in enumerate(metas.items()):
        # Calcula quanto foi gasto nessa categoria no mês
        gasto_atual = df_mes_atual[df_mes_atual['Categoria']
                                   == categoria]['Valor'].sum()

        # Calcula % (evita divisão por zero)
        percentual = gasto_atual / valor_meta if valor_meta > 0 else 0

        # Trava visual em 100% (1.0) para não quebrar o componente
        valor_barra = min(percentual, 1.0)

        aviso = ""
        if percentual >= 1.0:
            aviso = "⚠️ **ORÇAMENTO ESTOURADO!**"
        elif percentual >= 0.8:
            aviso = "⚠️ *Atenção: Perto do limite.*"

        # Exibição (Alterna entre coluna 1 e 2)
        with col_meta1 if i % 2 == 0 else col_meta2:
            st.write(f"**{categoria}**")
            st.progress(valor_barra)
            st.caption(
                f"Gasto: R$ {gasto_atual:.2f} / Meta: R$ {valor_meta:.2f} ({percentual*100:.1f}%)")
            if aviso:
                st.markdown(aviso)
            st.write("---")

    # ---

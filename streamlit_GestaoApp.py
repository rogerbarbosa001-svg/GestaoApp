import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Sistema de Gestão Financeira - Salão de Festas",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilização CSS Profissional ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .big-font { font-size:24px !important; font-weight: bold; color: #2C3E50; }
    .metric-container {
        background-color: #ffffff;
        border-left: 5px solid #3498db;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sim-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 4px 4px 0px 0px;
        box-shadow: 0 -1px 2px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #eef2f6;
        color: #2980b9;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Inicialização de Estado ---
if "custos_fixos_lista" not in st.session_state:
    st.session_state.custos_fixos_lista = []
if "catalogo_produtos" not in st.session_state:
    st.session_state.catalogo_produtos = []
if "vendas_registradas" not in st.session_state:
    st.session_state.vendas_registradas = []
if "meta_faturamento" not in st.session_state:
    st.session_state.meta_faturamento = 35000.00
if "temp_custos_produto" not in st.session_state:
    st.session_state.temp_custos_produto = []

# --- Funções Auxiliares ---
def converter_dados_para_json():
    dados = {
        "custos_fixos": st.session_state.custos_fixos_lista,
        "produtos": st.session_state.catalogo_produtos,
        "vendas": st.session_state.vendas_registradas,
        "meta": st.session_state.meta_faturamento
    }
    return json.dumps(dados, default=str)

def carregar_dados_json(arquivo):
    try:
        dados = json.load(arquivo)
        st.session_state.custos_fixos_lista = dados.get("custos_fixos", [])
        st.session_state.catalogo_produtos = dados.get("produtos", [])
        st.session_state.vendas_registradas = dados.get("vendas", [])
        st.session_state.meta_faturamento = dados.get("meta", 35000.00)
        return True
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return False

# --- SIDEBAR: CONTROLE E BACKUP ---
with st.sidebar:
    st.title("💎 Gestão Premium")
    st.caption("Painel de Controle Financeiro")
    st.markdown("---")
    
    st.markdown("### 🎯 Metas")
    nova_meta = st.number_input("Meta Mensal (R$)", value=float(st.session_state.meta_faturamento), step=1000.0, format="%.2f")
    if nova_meta != st.session_state.meta_faturamento:
        st.session_state.meta_faturamento = nova_meta
        st.rerun()

    st.markdown("---")
    st.markdown("### 💾 Banco de Dados")
    
    col_dl, col_ul = st.columns(2)
    with col_dl:
        json_data = converter_dados_para_json()
        st.download_button(
            label="⬇️ Backup",
            data=json_data,
            file_name=f"backup_salao_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("Restaurar Dados", type="json", label_visibility="collapsed")
    if uploaded_file is not None:
        if st.button("Carregar Arquivo", use_container_width=True):
            if carregar_dados_json(uploaded_file):
                st.success("Sistema atualizado!")
                st.rerun()
    
    st.divider()
    if st.button("⚠️ Resetar Sistema", type="primary", use_container_width=True):
        st.session_state.custos_fixos_lista = []
        st.session_state.catalogo_produtos = []
        st.session_state.vendas_registradas = []
        st.rerun()

# --- TABS PRINCIPAIS ---
st.title("📊 Dashboard Financeiro Integrado")
tab_dash, tab_lancamentos, tab_produtos, tab_relatorios, tab_simulador = st.tabs([
    "📈 Visão Geral", 
    "📝 Lançamentos (Vendas/Custos)", 
    "📦 Catálogo de Produtos", 
    "📑 Relatórios Avançados",
    "🔮 Simulador & Ponto de Equilíbrio"
])

# ==========================================
# TAB 1: DASHBOARD EXECUTIVO (VISÃO GERAL)
# ==========================================
with tab_dash:
    # Filtro de Mês para o Dashboard
    df_vendas = pd.DataFrame(st.session_state.vendas_registradas)
    custo_fixo_total = sum(item['valor'] for item in st.session_state.custos_fixos_lista)
    
    col_ano, col_mes, col_vazio = st.columns([1, 1, 3])
    with col_ano:
        ano_atual = datetime.now().year
        if not df_vendas.empty:
            lista_anos = sorted(list(set(df_vendas["ano"])))
            sel_ano = st.selectbox("Ano de Referência", lista_anos, index=len(lista_anos)-1)
        else:
            sel_ano = ano_atual
            st.selectbox("Ano de Referência", [ano_atual])
            
    with col_mes:
        mes_atual = datetime.now().month
        lista_meses = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho", 
                       7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
        sel_mes = st.selectbox("Mês de Referência", options=list(lista_meses.keys()), format_func=lambda x: lista_meses[x], index=mes_atual-1)

    # Cálculos do Mês Selecionado
    receita_mes = 0.0
    custo_var_mes = 0.0
    lucro_mes = -custo_fixo_total # Começa negativo pelo custo fixo
    ponto_equilibrio_mes = 0.0
    
    if not df_vendas.empty:
        mask = (df_vendas["ano"] == sel_ano) & (df_vendas["mes"] == sel_mes)
        df_filtrado = df_vendas[mask]
        
        if not df_filtrado.empty:
            receita_mes = df_filtrado["faturamento"].sum()
            custo_var_mes = df_filtrado["custo_total"].sum()
            margem_contrib = receita_mes - custo_var_mes
            lucro_mes = margem_contrib - custo_fixo_total
            
            # Cálculo do Ponto de Equilíbrio
            # PE = Custo Fixo / Margem de Contribuição Percentual
            margem_perc_mes = (margem_contrib / receita_mes) if receita_mes > 0 else 0
            if margem_perc_mes > 0:
                ponto_equilibrio_mes = custo_fixo_total / margem_perc_mes
    
    # --- CARDS DE KPI ---
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        meta_val = st.session_state.meta_faturamento if st.session_state.meta_faturamento > 0 else 1
        meta_div = receita_mes/meta_val
        st.metric("Faturamento", f"R$ {receita_mes:,.2f}", delta=f"{(meta_div-1)*100:.1f}% Meta")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="metric-container" style="border-left-color: #e74c3c;">', unsafe_allow_html=True)
        st.metric("Custos Totais", f"R$ {(custo_fixo_total + custo_var_mes):,.2f}", help=f"Fixo: {custo_fixo_total} | Var: {custo_var_mes}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c3:
        cor_lucro = "normal" if lucro_mes >= 0 else "inverse"
        st.markdown(f'<div class="metric-container" style="border-left-color: {"#27ae60" if lucro_mes >=0 else "#c0392b"};">', unsafe_allow_html=True)
        st.metric("Lucro Líquido", f"R$ {lucro_mes:,.2f}", delta_color=cor_lucro)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c4:
        margem_liq = (lucro_mes / receita_mes * 100) if receita_mes > 0 else 0
        st.markdown('<div class="metric-container" style="border-left-color: #f1c40f;">', unsafe_allow_html=True)
        st.metric("Margem Líq. %", f"{margem_liq:.1f}%", help="% que sobra no bolso")
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        # Card Ponto de Equilíbrio
        st.markdown('<div class="metric-container" style="border-left-color: #8e44ad;">', unsafe_allow_html=True)
        delta_pe = receita_mes - ponto_equilibrio_mes
        label_pe = "Acima do PE" if delta_pe >= 0 else "Abaixo do PE"
        st.metric("Ponto Equilíbrio", f"R$ {ponto_equilibrio_mes:,.2f}", delta=f"{delta_pe:,.2f} ({label_pe})", help="Faturamento mínimo para não ter prejuízo")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- GRÁFICOS DO DASHBOARD ---
    g1, g2 = st.columns([2, 1])
    
    with g1:
        st.subheader("Evolução Anual: Realizado vs Meta")
        if not df_vendas.empty:
            df_ano_full = df_vendas[df_vendas["ano"] == sel_ano]
            df_agrupado = df_ano_full.groupby("mes")["faturamento"].sum().reindex(range(1, 13), fill_value=0).reset_index()
            df_agrupado["nome_mes"] = df_agrupado["mes"].map(lista_meses).str[:3]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_agrupado["nome_mes"], y=df_agrupado["faturamento"], name="Faturamento", marker_color="#3498db"))
            fig.add_trace(go.Scatter(x=df_agrupado["nome_mes"], y=[st.session_state.meta_faturamento]*12, name="Meta", line=dict(color="red", dash="dash")))
            fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados para exibir gráfico anual.")

    with g2:
        st.subheader("Composição de Custos")
        if (custo_fixo_total + custo_var_mes) > 0:
            labels = ["Custos Fixos", "Custos Variáveis (Vendas)"]
            values = [custo_fixo_total, custo_var_mes]
            fig_pie = px.pie(names=labels, values=values, hole=0.4, color_discrete_sequence=["#95a5a6", "#e74c3c"])
            fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), showlegend=True, legend=dict(orientation="h"))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sem custos registrados.")

# ==========================================
# TAB 2: LANÇAMENTOS (VENDAS E CUSTOS FIXOS)
# ==========================================
with tab_lancamentos:
    st.markdown("### 📝 Central de Lançamentos")
    
    subtab_vendas, subtab_fixos = st.tabs(["💰 Registrar Venda", "🏢 Gerenciar Custos Fixos"])
    
    # --- REGISTRO DE VENDAS ---
    with subtab_vendas:
        col_form, col_hist = st.columns([1, 2])
        
        with col_form:
            with st.container(border=True):
                st.subheader("Nova Venda")
                if not st.session_state.catalogo_produtos:
                    st.warning("⚠️ Cadastre produtos primeiro!")
                else:
                    dt_venda = st.date_input("Data do Evento", datetime.now())
                    
                    lista_prods = [p['nome'] for p in st.session_state.catalogo_produtos]
                    if lista_prods:
                        prod_sel = st.selectbox("Produto/Serviço", lista_prods)
                        qtd_sel = st.number_input("Quantidade", 1, 100, 1)
                        
                        prod_obj = next((p for p in st.session_state.catalogo_produtos if p['nome'] == prod_sel), None)
                        
                        if prod_obj:
                            st.caption(f"Valor Unit: R$ {prod_obj['preco_venda']:.2f} | Custo Unit: R$ {prod_obj['custo_total']:.2f}")
                            
                            if st.button("Confirmar Lançamento", type="primary", use_container_width=True):
                                registro = {
                                    "id_venda": datetime.now().timestamp(),
                                    "data": dt_venda.strftime("%Y-%m-%d"),
                                    "mes": dt_venda.month,
                                    "ano": dt_venda.year,
                                    "produto": prod_sel,
                                    "qtd": qtd_sel,
                                    "preco_unitario": prod_obj['preco_venda'],
                                    "custo_unitario": prod_obj['custo_total'],
                                    "faturamento": prod_obj['preco_venda'] * qtd_sel,
                                    "custo_total": prod_obj['custo_total'] * qtd_sel,
                                    "margem_total": (prod_obj['preco_venda'] - prod_obj['custo_total']) * qtd_sel
                                }
                                st.session_state.vendas_registradas.append(registro)
                                st.success("Venda Registrada!")
                                st.rerun()
                        else:
                            st.error("Erro ao recuperar dados do produto.")
                    else:
                        st.warning("Nenhum produto cadastrado.")

        with col_hist:
            st.subheader("Histórico de Vendas")
            if st.session_state.vendas_registradas:
                df_hist = pd.DataFrame(st.session_state.vendas_registradas)
                df_hist = df_hist.sort_values("data", ascending=False)
                
                st.dataframe(
                    df_hist[["data", "produto", "qtd", "faturamento", "margem_total"]],
                    column_config={
                        "data": "Data",
                        "faturamento": st.column_config.NumberColumn("Total (R$)", format="R$ %.2f"),
                        "margem_total": st.column_config.NumberColumn("Lucro Bruto", format="R$ %.2f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                if st.button("🗑️ Excluir Último Lançamento"):
                    st.session_state.vendas_registradas.pop()
                    st.rerun()
            else:
                st.info("Nenhuma venda lançada.")

    # --- CUSTOS FIXOS ---
    with subtab_fixos:
        st.markdown("**Custos Fixos Mensais (Recorrentes)**")
        st.info("Edite diretamente na tabela abaixo. As alterações são salvas automaticamente.")
        
        df_fixos = pd.DataFrame(st.session_state.custos_fixos_lista)
        if df_fixos.empty:
            df_fixos = pd.DataFrame([{"descricao": "", "valor": 0.0}])
        
        edited_fixos = st.data_editor(
            df_fixos,
            num_rows="dynamic",
            column_config={
                "descricao": "Descrição da Conta",
                "valor": st.column_config.NumberColumn("Valor Mensal (R$)", format="R$ %.2f", min_value=0)
            },
            use_container_width=True,
            key="editor_fixos_pro"
        )
        
        novos_fixos = []
        for idx, row in edited_fixos.iterrows():
            if row["descricao"]:
                novos_fixos.append({"descricao": row["descricao"], "valor": float(row["valor"] or 0.0)})
        
        st.session_state.custos_fixos_lista = novos_fixos

        # --- NOVA ÁREA: ANÁLISE DE CUSTOS FIXOS ---
        if st.session_state.custos_fixos_lista:
            st.divider()
            st.subheader("📊 Análise de Custos Fixos")
            
            df_analise_fixos = pd.DataFrame(st.session_state.custos_fixos_lista)
            
            # Totais
            total_mensal = df_analise_fixos["valor"].sum()
            total_anual = total_mensal * 12
            
            # Colunas de Métricas
            col_tot1, col_tot2 = st.columns(2)
            col_tot1.metric("Total Mensal Comprometido", f"R$ {total_mensal:,.2f}")
            col_tot2.metric("Projeção Anual (12 meses)", f"R$ {total_anual:,.2f}", help="Quanto sua empresa gasta por ano só para existir")
            
            # Gráfico de Barras Horizontais
            st.markdown("**Distribuição por Conta**")
            fig_cf_bar = px.bar(
                df_analise_fixos.sort_values("valor", ascending=True), 
                x="valor", 
                y="descricao", 
                orientation='h',
                text_auto="R$ .2f",
                title="Ranking de Custos Fixos"
            )
            fig_cf_bar.update_layout(xaxis_title="Valor Mensal (R$)", yaxis_title="Conta")
            fig_cf_bar.update_traces(marker_color="#3498db")
            st.plotly_chart(fig_cf_bar, use_container_width=True)

# ==========================================
# TAB 3: CATÁLOGO DE PRODUTOS (EDITÁVEL)
# ==========================================
with tab_produtos:
    st.markdown("### 📦 Gestão de Produtos e Custos")
    
    col_lista, col_detalhe = st.columns([1, 2])
    
    # Seletor de Produto
    opcoes = ["➕ Novo Produto"] + [p['nome'] for p in st.session_state.catalogo_produtos]
    selecao = col_lista.radio("Selecione o Produto", options=opcoes)
    
    idx_edit = -1
    dados = {"nome": "", "preco": 0.0, "custos": []}
    
    if selecao != "➕ Novo Produto":
        for i, p in enumerate(st.session_state.catalogo_produtos):
            if p['nome'] == selecao:
                dados = {"nome": p['nome'], "preco": p['preco_venda'], "custos": p['custos_lista']}
                idx_edit = i
                break
    
    with col_detalhe:
        with st.container(border=True):
            st.subheader(f"Editando: {selecao}")
            
            nome = st.text_input("Nome do Produto", value=dados['nome'])
            preco = st.number_input("Preço de Venda (R$)", value=float(dados['preco']), step=10.0)
            
            st.markdown("---")
            st.markdown("**Composição de Custos (Ficha Técnica)**")
            
            # Carregar custos na sessão temporária
            if "last_prod_sel" not in st.session_state or st.session_state.last_prod_sel != selecao:
                st.session_state.temp_custos_produto = list(dados['custos'])
                st.session_state.last_prod_sel = selecao

            df_custos_temp = pd.DataFrame(st.session_state.temp_custos_produto)
            if df_custos_temp.empty:
                df_custos_temp = pd.DataFrame(columns=["item", "valor"])
            
            edited_custos = st.data_editor(
                df_custos_temp,
                num_rows="dynamic",
                column_config={
                    "item": "Insumo / Custo",
                    "valor": st.column_config.NumberColumn("Custo (R$)", format="R$ %.2f")
                },
                use_container_width=True,
                key="editor_custos_prod"
            )
            
            custo_total = edited_custos["valor"].sum() if not edited_custos.empty else 0
            margem = preco - custo_total
            margem_perc = (margem/preco*100) if preco > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.info(f"Custo Total: R$ {custo_total:.2f}")
            c2.success(f"Margem: R$ {margem:.2f}")
            c3.metric("Margem %", f"{margem_perc:.1f}%")
            
            st.divider()
            
            col_save, col_del = st.columns([4, 1])
            
            with col_save:
                if st.button("💾 Salvar Produto", type="primary", use_container_width=True):
                    if nome and preco > 0:
                        nova_lista_custos = edited_custos.to_dict('records')
                        nova_lista_custos = [x for x in nova_lista_custos if x['item'] and x['valor'] >= 0]
                        
                        prod_obj = {
                            "nome": nome,
                            "preco_venda": preco,
                            "custos_lista": nova_lista_custos,
                            "custo_total": custo_total,
                            "margem": margem
                        }
                        
                        if idx_edit >= 0:
                            st.session_state.catalogo_produtos[idx_edit] = prod_obj
                            st.toast("Produto Atualizado!")
                        else:
                            st.session_state.catalogo_produtos.append(prod_obj)
                            st.toast("Produto Criado!")
                        st.rerun()
            
            with col_del:
                if idx_edit >= 0:
                    if st.button("🗑️ Excluir", type="secondary", use_container_width=True):
                         st.session_state.catalogo_produtos.pop(idx_edit)
                         st.toast("Produto removido com sucesso!")
                         st.rerun()

# ==========================================
# TAB 4: RELATÓRIOS AVANÇADOS (BI)
# ==========================================
with tab_relatorios:
    st.markdown("### 📑 Relatórios Contábeis e Gerenciais")
    
    if not st.session_state.vendas_registradas:
        st.info("Registre vendas para gerar relatórios.")
    else:
        df_full = pd.DataFrame(st.session_state.vendas_registradas)
        custo_fixo_mensal = sum(c['valor'] for c in st.session_state.custos_fixos_lista)
        
        # 1. DRE Gerencial
        st.subheader("DRE Gerencial (Visão Acumulada Anual)")
        
        receita_total = df_full["faturamento"].sum()
        custo_var_total = df_full["custo_total"].sum()
        margem_total = receita_total - custo_var_total
        
        meses_ativos = df_full["mes"].nunique()
        custo_fixo_acumulado = custo_fixo_mensal * (meses_ativos if meses_ativos > 0 else 1)
        
        lucro_liquido_total = margem_total - custo_fixo_acumulado
        div_receita = receita_total if receita_total > 0 else 1
        
        margem_media_perc = (margem_total / div_receita)
        pe_acumulado = 0.0
        if margem_media_perc > 0:
            pe_acumulado = custo_fixo_acumulado / margem_media_perc
            
        col_pe1, col_pe2 = st.columns([1, 3])
        with col_pe1:
             st.metric("Ponto de Equilíbrio (Acumulado)", f"R$ {pe_acumulado:,.2f}", help="Valor total que precisaria ter vendido no período para cobrir todos os custos.")

        dre_data = {
            "Conceito": [
                "1. Faturamento Bruto", 
                "2. (-) Custos Variáveis (Produtos)", 
                "= 3. Margem de Contribuição", 
                "4. (-) Custos Fixos", 
                "= 5. Resultado Líquido (Lucro/Prejuízo)"
            ],
            "Valor (R$)": [
                receita_total, 
                -custo_var_total, 
                margem_total, 
                -custo_fixo_acumulado, 
                lucro_liquido_total
            ],
            "Análise Vertical (%)": [
                100.0, 
                (custo_var_total/div_receita*100), 
                (margem_total/div_receita*100), 
                (custo_fixo_acumulado/div_receita*100), 
                (lucro_liquido_total/div_receita*100)
            ]
        }
        st.dataframe(pd.DataFrame(dre_data).style.format({
            "Valor (R$)": "R$ {:,.2f}", 
            "Análise Vertical (%)": "{:.1f}%"
        }), use_container_width=True)
        
        st.divider()
        
        # --- GRÁFICOS DO DRE ---
        st.subheader("🔍 Raio-X dos Custos")
        col_dre_g1, col_dre_g2 = st.columns(2)
        with col_dre_g1:
            st.markdown("**Para onde vai o dinheiro? (Visão Macro)**")
            labels_macro = ["Custos Variáveis (Operação)", "Custos Fixos (Estrutura)", "Lucro Líquido (Bolso)"]
            vals_macro = [custo_var_total, custo_fixo_acumulado, max(0, lucro_liquido_total)]
            fig_macro = px.pie(names=labels_macro, values=vals_macro, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_macro, use_container_width=True)
            
        with col_dre_g2:
            st.markdown("**Top Ofensores: Custos Fixos**")
            if st.session_state.custos_fixos_lista:
                df_cf = pd.DataFrame(st.session_state.custos_fixos_lista)
                df_cf = df_cf.sort_values("valor", ascending=True)
                fig_cf = px.bar(
                    df_cf, 
                    x="valor", 
                    y="descricao", 
                    orientation='h',
                    title="Peso de cada conta no orçamento mensal",
                    labels={"valor": "Valor Mensal (R$)", "descricao": "Conta"},
                    text_auto=".2s"
                )
                fig_cf.update_traces(marker_color='#e74c3c')
                st.plotly_chart(fig_cf, use_container_width=True)
            else:
                st.info("Nenhum custo fixo cadastrado para análise.")

        st.divider()
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.subheader("🏆 Ranking de Produtos (Lucro Bruto)")
            df_prod_rank = df_full.groupby("produto")[["faturamento", "margem_total", "qtd"]].sum().reset_index()
            df_prod_rank = df_prod_rank.sort_values("margem_total", ascending=True)
            fig_rank = px.bar(
                df_prod_rank, 
                x="margem_total", 
                y="produto", 
                orientation='h',
                text_auto='.2s',
                color="margem_total",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_rank, use_container_width=True)
            
        with col_g2:
            st.subheader("📊 Matriz de Eficiência")
            df_eficiencia = df_full.groupby("produto").agg({
                "faturamento": "sum",
                "margem_total": "sum",
                "qtd": "sum"
            }).reset_index()
            
            df_eficiencia["margem_perc"] = df_eficiencia.apply(lambda x: (x["margem_total"] / x["faturamento"] * 100) if x["faturamento"] > 0 else 0, axis=1)
            
            fig_scatter = px.scatter(
                df_eficiencia,
                x="margem_perc",
                y="margem_total",
                size="faturamento",
                color="produto",
                title="Margem % (Eixo X) vs Lucro Total R$ (Eixo Y)",
                hover_name="produto"
            )
            fig_scatter.add_vline(x=df_eficiencia["margem_perc"].mean(), line_dash="dash", line_color="gray", annotation_text="Média %")
            fig_scatter.add_hline(y=df_eficiencia["margem_total"].mean(), line_dash="dash", line_color="gray", annotation_text="Média R$")
            st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# TAB 5: SIMULADOR DE CENÁRIOS
# ==========================================
with tab_simulador:
    st.header("🔮 Simulador & Análise de Ponto de Equilíbrio")
    
    if not st.session_state.catalogo_produtos:
        st.warning("Cadastre produtos primeiro.")
    else:
        st.markdown("### 1. Simulador Global de Cenários")
        st.caption("Ajuste os parâmetros para ver o impacto no resultado final (baseado no mês atual).")
        
        # Container para Inputs
        with st.container():
            col_params, col_result = st.columns([1, 2], gap="large")
            
            with col_params:
                st.markdown('<div class="sim-card">', unsafe_allow_html=True)
                st.markdown("**⚙️ Ajustes de Mercado**")
                fator_vendas = st.slider("Volume de Vendas", -50, 50, 0, format="%d%%")
                fator_preco = st.slider("Reajuste de Preços", -20, 20, 0, format="%d%%")
                fator_custo = st.slider("Custo Operacional", -20, 20, 0, format="%d%%")
                
                base_vendas_padrao = receita_mes if 'receita_mes' in locals() else 0.0
                st.divider()
                base_vendas_mensal = st.number_input("Venda Base (Mês) R$", value=base_vendas_padrao)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_result:
                st.markdown('<div class="sim-card">', unsafe_allow_html=True)
                st.markdown("**📊 Resultados da Simulação**")
                
                custo_fixo = sum(c['valor'] for c in st.session_state.custos_fixos_lista)
                
                # Lógica de Simulação
                margem_media_atual = 0.40
                if 'receita_total' in locals() and receita_total > 0:
                    margem_media_atual = margem_total / receita_total

                nova_receita = base_vendas_mensal * (1 + fator_vendas/100) * (1 + fator_preco/100)
                novo_custo_var = (base_vendas_mensal * (1 - margem_media_atual)) * (1 + fator_vendas/100) * (1 + fator_custo/100)
                
                nova_margem_val = nova_receita - novo_custo_var
                novo_lucro = nova_margem_val - custo_fixo
                val_margem_liq = (novo_lucro / nova_receita * 100) if nova_receita > 0 else 0.0
                
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("Nova Receita", f"R$ {nova_receita:,.0f}", delta=f"{(nova_receita - base_vendas_mensal):,.0f}")
                col_s2.metric("Novo Lucro", f"R$ {novo_lucro:,.0f}", delta=f"{(novo_lucro - (base_vendas_mensal * margem_media_atual - custo_fixo)):,.0f}")
                col_s3.metric("Margem Líquida", f"{val_margem_liq:.1f}%")
                
                # Gráfico Simples
                fig_sim = go.Figure()
                fig_sim.add_trace(go.Bar(x=["Cenário Base", "Cenário Simulado"], 
                                        y=[base_vendas_mensal * margem_media_atual - custo_fixo, novo_lucro], 
                                        marker_color=["#bdc3c7", "#3498db"]))
                fig_sim.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_sim, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # --- NOVA SEÇÃO: PONTO DE EQUILÍBRIO POR PRODUTO ---
        st.markdown("### 2. Meta de Vendas para Ponto de Equilíbrio")
        st.info("Esta análise responde: *Quantas festas deste tipo eu preciso vender para pagar TODO o custo fixo da empresa (R$ {:.2f})?*".format(custo_fixo))
        
        lista_pe_produtos = []
        
        for p in st.session_state.catalogo_produtos:
            nome = p['nome']
            preco = p['preco_venda']
            custo_var = p['custo_total']
            margem_unit = preco - custo_var
            
            if margem_unit > 0:
                qtd_necessaria = custo_fixo / margem_unit
                # Criar texto de dificuldade
                dificuldade = "Baixa" if qtd_necessaria < 10 else "Média" if qtd_necessaria < 30 else "Alta"
            else:
                qtd_necessaria = float('inf')
                dificuldade = "Impossível (Margem Negativa)"
            
            lista_pe_produtos.append({
                "Produto": nome,
                "Preço Venda": preco,
                "Custo Variável": custo_var,
                "Margem Unitária": margem_unit,
                "Qtd Necessária (PE)": qtd_necessaria,
                "Meta Faturamento (PE)": qtd_necessaria * preco if qtd_necessaria != float('inf') else 0,
                "Dificuldade": dificuldade
            })
            
        df_pe = pd.DataFrame(lista_pe_produtos)
        
        c_pe_g, c_pe_t = st.columns([1, 2])
        
        with c_pe_g:
            # Gráfico de Qtd Necessária
            # Filtrar infinitos para o gráfico
            df_graph = df_pe[df_pe["Qtd Necessária (PE)"] != float('inf')].sort_values("Qtd Necessária (PE)")
            
            fig_pe_bar = px.bar(
                df_graph,
                x="Qtd Necessária (PE)",
                y="Produto",
                orientation='h',
                title="Quantas vendas para zerar custos?",
                text_auto='.1f',
                color="Qtd Necessária (PE)",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_pe_bar, use_container_width=True)
            
        with c_pe_t:
            st.dataframe(
                df_pe,
                column_config={
                    "Preço Venda": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Custo Variável": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Margem Unitária": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Qtd Necessária (PE)": st.column_config.NumberColumn(format="%.1f unid"),
                    "Meta Faturamento (PE)": st.column_config.NumberColumn(format="R$ %.2f"),
                },
                use_container_width=True,
                hide_index=True
            )
"""
Dashboard Interativo - Análise de Resíduos em Santa Catarina
Gráficos interativos com Plotly para visualização de dados
"""
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests

print("="*70)
print("📊 CRIANDO DASHBOARD INTERATIVO DE ANÁLISE DE RESÍDUOS")
print("="*70)

# ============================================================================
# 1. CARREGAR E PREPARAR DADOS
# ============================================================================
print("\n1️⃣ Carregando dados...")

# Carregar CSVs existentes
df_bacias = pd.read_csv(r'outputs\resumo_por_bacia.csv')
df_regioes = pd.read_csv(r'outputs\resumo_por_regiao.csv')
df_risco = pd.read_csv(r'outputs\analise_risco_municipios.csv')

# Carregar setores para análise municipal completa
gdf = gpd.read_file(r'SC_setores_CD2022.gpkg')

# Buscar população municipal
print("   Buscando população via API IBGE...")
try:
    url = "https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93?localidades=N6[all]"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    rows = []
    for item in data[0]['resultados']:
        for loc in item['series']:
            codigo = str(loc['localidade']['id']).zfill(7)
            nome = loc['localidade']['nome']
            pop = list(loc['serie'].values())[0] if loc['serie'] else None
            if pop:
                rows.append({
                    'codigo_ibge': codigo,
                    'municipio': nome,
                    'populacao': float(pop)
                })
    pop_df = pd.DataFrame(rows)
    pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
    pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10
    print(f"   ✓ {len(pop_df)} municípios carregados")
except Exception as e:
    print(f"   ⚠️ Erro: {e}")
    pop_df = None

# ============================================================================
# 2. PREPARAR DADOS PARA GRÁFICOS
# ============================================================================
print("\n2️⃣ Processando dados para visualizações...")

# Top 15 municípios
if pop_df is not None:
    top_municipios = pop_df.nlargest(15, 'domestico_t_ano')
    
    # Estatísticas gerais
    total_pop = pop_df['populacao'].sum()
    total_domestico = pop_df['domestico_t_ano'].sum()
    total_reciclavel = pop_df['reciclavel_t_ano'].sum()
    
    print(f"   📊 População total SC: {total_pop:,.0f} habitantes")
    print(f"   🔵 Resíduos domésticos: {total_domestico:,.0f} t/ano")
    print(f"   🟡 Resíduos recicláveis: {total_reciclavel:,.0f} t/ano")

# ============================================================================
# 3. CRIAR GRÁFICOS INTERATIVOS
# ============================================================================
print("\n3️⃣ Criando gráficos interativos...")

# Cores do tema
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'domestico': '#034e7b',
    'reciclavel': '#e31a1c',
    'background': '#f8f9fa',
    'text': '#333333'
}

# ---------------------------------------------------------------------------
# GRÁFICO 1: Top 15 Municípios - Resíduos Domésticos
# ---------------------------------------------------------------------------
fig1 = go.Figure()

fig1.add_trace(go.Bar(
    y=top_municipios['municipio'],
    x=top_municipios['domestico_t_ano'],
    orientation='h',
    marker=dict(
        color=top_municipios['domestico_t_ano'],
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="t/ano")
    ),
    text=top_municipios['domestico_t_ano'].apply(lambda x: f'{x:,.0f}'),
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Resíduos: %{x:,.0f} t/ano<extra></extra>'
))

fig1.update_layout(
    title='🔵 Top 15 Municípios - Geração de Resíduos Domésticos',
    xaxis_title='Toneladas por Ano',
    yaxis_title='',
    height=600,
    template='plotly_white',
    font=dict(size=12),
    showlegend=False
)

# ---------------------------------------------------------------------------
# GRÁFICO 2: Distribuição por Bacias Hidrográficas
# ---------------------------------------------------------------------------
fig2 = go.Figure()

cores_bacias = ['#1976d2', '#388e3c', '#7b1fa2', '#0097a7', 
                '#00796b', '#f57c00', '#5d4037', '#757575']

fig2.add_trace(go.Bar(
    x=df_bacias['bacia'],
    y=df_bacias['domestico_t_ano'],
    name='Doméstico',
    marker_color='#034e7b',
    text=df_bacias['domestico_t_ano'].apply(lambda x: f'{x:,.0f}'),
    textposition='outside'
))

fig2.add_trace(go.Bar(
    x=df_bacias['bacia'],
    y=df_bacias['reciclavel_t_ano'],
    name='Reciclável',
    marker_color='#fbc02d',
    text=df_bacias['reciclavel_t_ano'].apply(lambda x: f'{x:,.0f}'),
    textposition='outside'
))

fig2.update_layout(
    title='🌊 Geração de Resíduos por Bacia Hidrográfica',
    xaxis_title='Bacia Hidrográfica',
    yaxis_title='Toneladas por Ano',
    height=500,
    template='plotly_white',
    barmode='group',
    xaxis_tickangle=-45
)

# ---------------------------------------------------------------------------
# GRÁFICO 3: Pizza - Distribuição de Risco
# ---------------------------------------------------------------------------
risco_counts = df_risco['risco'].value_counts()

fig3 = go.Figure(data=[go.Pie(
    labels=risco_counts.index,
    values=risco_counts.values,
    hole=0.4,
    marker=dict(colors=['#d32f2f', '#f57c00', '#fbc02d', '#388e3c']),
    textinfo='label+percent+value',
    hovertemplate='<b>%{label}</b><br>Municípios: %{value}<br>%{percent}<extra></extra>'
)])

fig3.update_layout(
    title='⚠️ Distribuição de Municípios por Nível de Risco',
    height=450,
    template='plotly_white',
    annotations=[dict(text='Risco', x=0.5, y=0.5, font_size=20, showarrow=False)]
)

# ---------------------------------------------------------------------------
# GRÁFICO 4: Top 10 Regiões (RGI)
# ---------------------------------------------------------------------------
top_regioes = df_regioes.nlargest(10, 'domestico_t_ano')

fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=top_regioes['populacao'],
    y=top_regioes['domestico_t_ano'],
    mode='markers+text',
    marker=dict(
        size=top_regioes['domestico_t_ano'] / 5000,
        color=top_regioes['domestico_t_ano'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="t/ano"),
        line=dict(width=2, color='white')
    ),
    text=top_regioes['NM_RGI'],
    textposition='top center',
    textfont=dict(size=9),
    hovertemplate='<b>%{text}</b><br>População: %{x:,.0f}<br>Resíduos: %{y:,.0f} t/ano<extra></extra>'
))

fig4.update_layout(
    title='📍 Top 10 Regiões (RGI) - População vs Resíduos',
    xaxis_title='População',
    yaxis_title='Resíduos Domésticos (t/ano)',
    height=500,
    template='plotly_white'
)

# ---------------------------------------------------------------------------
# GRÁFICO 5: Comparativo Bacias vs Regiões
# ---------------------------------------------------------------------------
fig5 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('População por Bacia', 'População por Região (Top 5)'),
    specs=[[{'type': 'domain'}, {'type': 'domain'}]]
)

fig5.add_trace(go.Pie(
    labels=df_bacias['bacia'],
    values=df_bacias['populacao'],
    name='Bacias',
    marker=dict(colors=cores_bacias)
), 1, 1)

top5_regioes = df_regioes.nlargest(5, 'populacao')
fig5.add_trace(go.Pie(
    labels=top5_regioes['NM_RGI'],
    values=top5_regioes['populacao'],
    name='Regiões'
), 1, 2)

fig5.update_layout(
    title_text='🗺️ Distribuição Populacional: Bacias vs Regiões',
    height=400,
    showlegend=True,
    template='plotly_white'
)

# ---------------------------------------------------------------------------
# GRÁFICO 6: Heatmap - Correlação
# ---------------------------------------------------------------------------
if pop_df is not None:
    # Top 20 para o heatmap (melhor visualização)
    top20 = pop_df.nlargest(20, 'populacao')[['municipio', 'populacao', 'domestico_t_ano', 'reciclavel_t_ano']]
    
    fig6 = go.Figure(data=go.Heatmap(
        z=[top20['populacao'].values, 
           top20['domestico_t_ano'].values, 
           top20['reciclavel_t_ano'].values],
        x=top20['municipio'].values,
        y=['População', 'Doméstico (t/ano)', 'Reciclável (t/ano)'],
        colorscale='RdYlBu_r',
        hovertemplate='<b>%{x}</b><br>%{y}: %{z:,.0f}<extra></extra>'
    ))
    
    fig6.update_layout(
        title='🔥 Heatmap - Top 20 Municípios',
        height=300,
        template='plotly_white',
        xaxis_tickangle=-45
    )

# ============================================================================
# 4. CRIAR HTML DO DASHBOARD
# ============================================================================
print("\n4️⃣ Montando dashboard HTML...")

html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Análise de Resíduos SC</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .back-button {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: transform 0.3s;
            margin-top: 20px;
        }}
        
        .back-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Dashboard Interativo</h1>
            <p class="subtitle">Análise de Resíduos Sólidos em Santa Catarina</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">População Total</div>
                <div class="stat-number">{total_pop:,.0f}</div>
                <div class="stat-label">habitantes</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Resíduos Domésticos</div>
                <div class="stat-number">{total_domestico:,.0f}</div>
                <div class="stat-label">toneladas/ano</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Resíduos Recicláveis</div>
                <div class="stat-number">{total_reciclavel:,.0f}</div>
                <div class="stat-label">toneladas/ano</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Municípios Analisados</div>
                <div class="stat-number">{len(pop_df)}</div>
                <div class="stat-label">em 7 bacias</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="chart1"></div>
        </div>
        
        <div class="chart-container">
            <div id="chart2"></div>
        </div>
        
        <div class="grid-2">
            <div class="chart-container">
                <div id="chart3"></div>
            </div>
            <div class="chart-container">
                <div id="chart4"></div>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="chart5"></div>
        </div>
        
        <div class="chart-container">
            <div id="chart6"></div>
        </div>
        
        <div style="text-align: center;">
            <a href="../../index.html" class="back-button">⬅️ Voltar ao Portfólio</a>
        </div>
        
        <footer>
            <p>Dashboard gerado automaticamente com Plotly | 2025</p>
        </footer>
    </div>
    
    <script>
        // Gráfico 1
        var chart1 = {fig1.to_json()};
        Plotly.newPlot('chart1', chart1.data, chart1.layout, {{responsive: true}});
        
        // Gráfico 2
        var chart2 = {fig2.to_json()};
        Plotly.newPlot('chart2', chart2.data, chart2.layout, {{responsive: true}});
        
        // Gráfico 3
        var chart3 = {fig3.to_json()};
        Plotly.newPlot('chart3', chart3.data, chart3.layout, {{responsive: true}});
        
        // Gráfico 4
        var chart4 = {fig4.to_json()};
        Plotly.newPlot('chart4', chart4.data, chart4.layout, {{responsive: true}});
        
        // Gráfico 5
        var chart5 = {fig5.to_json()};
        Plotly.newPlot('chart5', chart5.data, chart5.layout, {{responsive: true}});
        
        // Gráfico 6
        var chart6 = {fig6.to_json()};
        Plotly.newPlot('chart6', chart6.data, chart6.layout, {{responsive: true}});
    </script>
</body>
</html>
"""

# Salvar HTML
output_path = r'outputs\dashboard.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

import os
file_size = os.path.getsize(output_path) / (1024 * 1024)

print(f"\n✅ Dashboard criado com sucesso!")
print(f"📁 Arquivo: {output_path}")
print(f"💾 Tamanho: {file_size:.2f} MB")
print(f"\n📊 Gráficos incluídos:")
print("   1. Top 15 Municípios - Resíduos Domésticos")
print("   2. Distribuição por Bacias Hidrográficas")
print("   3. Pizza - Níveis de Risco")
print("   4. Top 10 Regiões - População vs Resíduos")
print("   5. Comparativo Bacias vs Regiões")
print("   6. Heatmap - Top 20 Municípios")

print("\n" + "="*70)
print("✅ DASHBOARD INTERATIVO CONCLUÍDO!")
print("="*70)

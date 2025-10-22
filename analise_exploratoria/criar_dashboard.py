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

# Buscar população municipal APENAS DE SANTA CATARINA
print("   Buscando população via API IBGE (apenas SC)...")
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
            # FILTRAR APENAS SANTA CATARINA (códigos começam com 42)
            if pop and codigo.startswith('42'):
                rows.append({
                    'codigo_ibge': codigo,
                    'municipio': nome,
                    'populacao': float(pop)
                })
    pop_df = pd.DataFrame(rows)
    pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
    pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10
    print(f"   ✓ {len(pop_df)} municípios de SC carregados")
except Exception as e:
    print(f"   ⚠️ Erro: {e}")
    pop_df = None

# ============================================================================
# 2. PREPARAR DADOS PARA GRÁFICOS
# ============================================================================
print("\n2️⃣ Processando dados para visualizações...")

# Top 15 municípios
if pop_df is not None:
    # Seleciona os 15 maiores e exibe em ordem crescente
    top_municipios = (
        pop_df
        .nlargest(15, 'domestico_t_ano')
        .sort_values('domestico_t_ano', ascending=True)
    )
    
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
    yaxis=dict(categoryorder='array', categoryarray=top_municipios['municipio'].tolist()),
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
# Garantir tipos numéricos e remover nulos
df_regioes['populacao'] = pd.to_numeric(df_regioes['populacao'], errors='coerce')
df_regioes['domestico_t_ano'] = pd.to_numeric(df_regioes['domestico_t_ano'], errors='coerce')
regioes_validas = df_regioes.dropna(subset=['populacao', 'domestico_t_ano'])
top_regioes = regioes_validas.nlargest(10, 'domestico_t_ano')

fig4 = go.Figure()

if len(top_regioes) > 0:
    # Calcular tamanhos proporcionais (8 a 60 pixels)
    tamanhos = (top_regioes['domestico_t_ano'] / 5000).clip(lower=8, upper=60).tolist()
    
    fig4.add_trace(go.Scatter(
        x=top_regioes['populacao'].tolist(),
        y=top_regioes['domestico_t_ano'].tolist(),
        mode='markers+text',
        marker=dict(
            size=tamanhos,
            color=top_regioes['domestico_t_ano'].tolist(),
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="t/ano"),
            line=dict(width=2, color='white')
        ),
        text=top_regioes['NM_RGI'].tolist(),
        textposition='top center',
        textfont=dict(size=9),
        hovertemplate='<b>%{text}</b><br>População: %{x:,.0f}<br>Resíduos: %{y:,.0f} t/ano<extra></extra>'
    ))
else:
    # Mensagem amigável quando não houver dados
    fig4.add_annotation(
        text="Sem dados para exibir",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16)
    )

fig4.update_layout(
    title='📍 Top 10 Regiões (RGI) - População vs Resíduos',
    xaxis_title='População',
    yaxis_title='Resíduos Domésticos (t/ano)',
    height=500,
    template='plotly_white'
)
fig4.update_xaxes(tickformat=",.0f")
fig4.update_yaxes(tickformat=",.0f")

# ---------------------------------------------------------------------------
# GRÁFICO 5: Comparativo Bacias vs Regiões (versão barras)
# ---------------------------------------------------------------------------
fig5 = make_subplots(
    rows=1, cols=2,
    subplot_titles=(
        '🌊 População por Bacia Hidrográfica',
        '📍 População por Região (Top 5)'
    ),
    specs=[[{'type': 'xy'}, {'type': 'xy'}]],
    column_widths=[0.48, 0.48],
    horizontal_spacing=0.12
)

# Dados e cores para Bacias
total_bacias = df_bacias['populacao'].sum()
df_bacias_sorted = df_bacias.copy().sort_values('populacao', ascending=True)
share_bacias = (df_bacias_sorted['populacao'] / total_bacias).values
# mapear cores preservando a cor original por bacia
map_cor_bacia = {b: c for b, c in zip(df_bacias['bacia'], cores_bacias)}
cores_bacias_sorted = [map_cor_bacia[b] for b in df_bacias_sorted['bacia']]

fig5.add_trace(go.Bar(
    y=df_bacias_sorted['bacia'],
    x=df_bacias_sorted['populacao'],
    orientation='h',
    marker_color=cores_bacias_sorted,
    text=[f"{v:,.0f} ({p:.1%})" for v, p in zip(df_bacias_sorted['populacao'], share_bacias)],
    texttemplate='%{text}',
    textposition='auto',
    textfont=dict(size=10),
    constraintext='both',
    hovertemplate='<b>%{y}</b><br>População: %{x:,.0f}<br>Participação: %{customdata:.1%}<extra></extra>',
    customdata=share_bacias
), row=1, col=1)

# Dados e barras para Regiões (Top 5)
top5_regioes = df_regioes.nlargest(5, 'populacao').copy().sort_values('populacao', ascending=True)
total_regioes_top5 = top5_regioes['populacao'].sum()
share_regioes = (top5_regioes['populacao'] / total_regioes_top5).values

fig5.add_trace(go.Bar(
    y=top5_regioes['NM_RGI'],
    x=top5_regioes['populacao'],
    orientation='h',
    marker_color='#90caf9',
    text=[f"{v:,.0f} ({p:.1%})" for v, p in zip(top5_regioes['populacao'], share_regioes)],
    texttemplate='%{text}',
    textposition='auto',
    textfont=dict(size=10),
    constraintext='both',
    hovertemplate='<b>%{y}</b><br>População: %{x:,.0f}<br>Participação (Top 5): %{customdata:.1%}<extra></extra>',
    customdata=share_regioes
), row=1, col=2)

fig5.update_layout(
    title_text='🗺️ Distribuição Populacional: Bacias vs Regiões',
    height=500,
    showlegend=False,
    template='plotly_white',
    margin=dict(t=80, r=30, b=60, l=30),
)

fig5.update_xaxes(tickformat=",.0f", title_text='Habitantes', automargin=True, tickfont=dict(size=10), row=1, col=1)
fig5.update_xaxes(tickformat=",.0f", title_text='Habitantes', automargin=True, tickfont=dict(size=10), row=1, col=2)
fig5.update_yaxes(title_text='Bacia Hidrográfica', automargin=True, tickfont=dict(size=10), row=1, col=1)
fig5.update_yaxes(title_text='Região (RGI)', automargin=True, tickfont=dict(size=10), row=1, col=2)

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

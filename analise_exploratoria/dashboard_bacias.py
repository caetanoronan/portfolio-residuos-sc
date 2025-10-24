"""
Dashboard Interativo - Análise de Resíduos por Bacias Hidrográficas de Santa Catarina
Visualizações: Ranking, Distribuição, Per Capita, Risco e Comparações
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Carregar dados
df_bacias = pd.read_csv(r'outputs\resumo_por_bacia.csv')
df_municipios = pd.read_csv(r'outputs\analise_risco_municipios.csv')

# Calcular métricas adicionais
df_bacias['domestico_per_capita'] = (df_bacias['domestico_t_ano'] / df_bacias['populacao']) * 1000  # kg/hab/ano
df_bacias['percentual_pop'] = (df_bacias['populacao'] / df_bacias['populacao'].sum()) * 100
df_bacias['percentual_residuos'] = (df_bacias['domestico_t_ano'] / df_bacias['domestico_t_ano'].sum()) * 100

# Ordenar para visualizações
df_bacias_sorted = df_bacias.sort_values('domestico_t_ano', ascending=True)

# Paleta de cores por bacia
cores_bacias = {
    'Bacia do Itajaí': '#1976d2',
    'Bacia do Tubarão': '#388e3c',
    'Bacia do Uruguai': '#7b1fa2',
    'Bacia Litorânea Norte': '#0097a7',
    'Bacia Litorânea Central': '#00796b',
    'Bacia do Rio do Peixe': '#f57c00',
    'Bacia do Canoas': '#5d4037',
    'Outras Bacias': '#757575'
}

df_bacias_sorted['cor'] = df_bacias_sorted['bacia'].map(cores_bacias)

print("📊 Criando Dashboard de Bacias Hidrográficas...")

# ==============================================
# GRÁFICO 1: Ranking de Bacias por Volume
# ==============================================
print("1️⃣ Gráfico 1: Ranking de bacias por volume de resíduos...")

fig1 = go.Figure()

fig1.add_trace(go.Bar(
    y=df_bacias_sorted['bacia'],
    x=df_bacias_sorted['domestico_t_ano'],
    orientation='h',
    marker=dict(
        color=df_bacias_sorted['cor'].tolist(),
        line=dict(color='white', width=2)
    ),
    text=[f"{val:,.0f} t/ano" for val in df_bacias_sorted['domestico_t_ano']],
    textposition='outside',
    textfont=dict(size=13, color='#333'),
    hovertemplate='<b>%{y}</b><br>' +
                  'Resíduos: %{x:,.0f} t/ano<br>' +
                  '<extra></extra>'
))

fig1.update_layout(
    title={
        'text': '🏆 Ranking das Bacias Hidrográficas por Volume de Resíduos Domésticos',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title='Volume de Resíduos Domésticos (toneladas/ano)',
    yaxis_title='',
    xaxis=dict(
        showgrid=True,
        gridcolor='#e0e0e0',
        tickformat=',',
        title_font=dict(size=14)
    ),
    yaxis=dict(
        tickfont=dict(size=13, color='#333')
    ),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    height=500,
    margin=dict(l=20, r=120, t=80, b=60),
    hoverlabel=dict(bgcolor="white", font_size=13)
)

# ==============================================
# GRÁFICO 2: Distribuição da População (MELHORADO)
# ==============================================
print("2️⃣ Gráfico 2: Distribuição populacional por bacia...")

df_pop = df_bacias.sort_values('populacao', ascending=True)

fig2 = go.Figure()

# Barras horizontais com população
fig2.add_trace(go.Bar(
    y=df_pop['bacia'].tolist(),
    x=df_pop['populacao'].tolist(),
    orientation='h',
    marker=dict(
        color=[cores_bacias[b] for b in df_pop['bacia']],
        line=dict(color='white', width=2)
    ),
    text=[f"{val/1000:.0f}k hab ({pct:.1f}%)" 
          for val, pct in zip(df_pop['populacao'], df_pop['percentual_pop'])],
    textposition='outside',
    textfont=dict(size=11, color='#333'),
    hovertemplate='<b>%{y}</b><br>' +
                  'População: %{x:,.0f} habitantes<br>' +
                  'Percentual do Estado: %{customdata:.1f}%<br>' +
                  '<extra></extra>',
    customdata=df_pop['percentual_pop'].tolist()
))

# Adicionar linha de média
media_pop = df_bacias['populacao'].mean()
fig2.add_vline(
    x=media_pop,
    line_dash="dash",
    line_color="red",
    line_width=2,
    annotation_text=f"Média: {media_pop/1000:.0f}k hab",
    annotation_position="top",
    annotation_font=dict(size=11, color='red')
)

fig2.update_layout(
    title={
        'text': '👥 Distribuição Populacional por Bacia Hidrográfica',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title='População (habitantes)',
    yaxis_title='',
    xaxis=dict(
        showgrid=True,
        gridcolor='#e0e0e0',
        tickformat=',',
        title_font=dict(size=14)
    ),
    yaxis=dict(
        tickfont=dict(size=11, color='#333'),
        automargin=True
    ),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    height=550,
    margin=dict(l=200, r=200, t=80, b=80),
    hoverlabel=dict(bgcolor="white", font_size=13),
    uniformtext=dict(mode='hide', minsize=8),
    annotations=[
        dict(
            text="<i>Barras mostram população absoluta | Rótulos incluem habitantes (k) e % do estado total</i>",
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    ]
)

# ==============================================
# GRÁFICO 3: Geração Per Capita
# ==============================================
print("3️⃣ Gráfico 3: Geração per capita por bacia...")

df_percapita = df_bacias.sort_values('domestico_per_capita', ascending=False)

fig3 = go.Figure()

# Calcular tamanhos dos marcadores (entre 15 e 60 pixels)
tamanhos = (df_percapita['domestico_t_ano'] / df_percapita['domestico_t_ano'].max() * 45 + 15).tolist()

# Adicionar cada bacia individualmente COM LEGENDA (sem texto nos marcadores)
for idx, row in df_percapita.iterrows():
    bacia_nome = row['bacia']
    fig3.add_trace(go.Scatter(
        x=[row['populacao']],
        y=[row['domestico_per_capita']],
        mode='markers',  # Removido 'text' - apenas marcadores
        marker=dict(
            size=(row['domestico_t_ano'] / df_percapita['domestico_t_ano'].max() * 45 + 15),
            color=cores_bacias[bacia_nome],
            line=dict(color='white', width=2),
            opacity=0.8
        ),
        name=bacia_nome,  # Nome aparecerá na legenda
        showlegend=True,  # Mostrar na legenda
        legendgroup=bacia_nome,
        hovertemplate='<b>' + bacia_nome + '</b><br>' +
                      'População: %{x:,.0f} hab<br>' +
                      'Per Capita: %{y:.1f} kg/hab/ano<br>' +
                      f'Volume Total: {row["domestico_t_ano"]:,.0f} t/ano<br>' +
                      '<extra></extra>'
    ))

# Linha de média
media_percapita = df_bacias['domestico_per_capita'].mean()
fig3.add_hline(
    y=media_percapita,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Média SC: {media_percapita:.1f} kg/hab/ano",
    annotation_position="right",
    annotation_font=dict(size=12, color='red')
)

fig3.update_layout(
    title={
        'text': '📊 Geração Per Capita de Resíduos vs População das Bacias',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title='População (habitantes)',
    yaxis_title='Geração Per Capita (kg/hab/ano)',
    xaxis=dict(
        showgrid=True,
        gridcolor='#e0e0e0',
        tickformat=',',
        title_font=dict(size=14),
        zeroline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#e0e0e0',
        title_font=dict(size=14),
        zeroline=False,
        range=[340, 360]  # Ajustar range para melhor visualização
    ),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    height=550,
    margin=dict(l=80, r=250, t=100, b=80),  # Margem direita maior para legenda
    hoverlabel=dict(bgcolor="white", font_size=13),
    legend=dict(
        title=dict(
            text='<b>Bacias Hidrográficas</b>',
            font=dict(size=13, color='#1976d2')
        ),
        orientation='v',
        yanchor='middle',
        y=0.5,
        xanchor='left',
        x=1.02,
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='#1976d2',
        borderwidth=2,
        font=dict(size=11)
    ),
    annotations=[
        dict(
            text="<i>Tamanho das bolhas representa o volume total de resíduos gerados por cada bacia</i>",
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    ]
)

# ==============================================
# GRÁFICO 4: Análise de Risco dos Municípios (MELHORADO)
# ==============================================
print("4️⃣ Gráfico 4: Distribuição de risco por bacia...")

# Contar total de municípios por bacia
total_por_bacia = df_municipios.groupby('bacia').size().reset_index(name='total')

# Contar municípios de ALTO RISCO (CRÍTICO + ALTO) por bacia
alto_risco = df_municipios[df_municipios['risco'].isin(['CRÍTICO', 'ALTO'])]
alto_risco_counts = alto_risco.groupby('bacia').size().reset_index(name='alto_risco')

# Merge e calcular percentual
risco_summary = total_por_bacia.merge(alto_risco_counts, on='bacia', how='left').fillna(0)
risco_summary['percentual_alto_risco'] = (risco_summary['alto_risco'] / risco_summary['total'] * 100)
risco_summary['baixo_medio_risco'] = risco_summary['total'] - risco_summary['alto_risco']
risco_summary = risco_summary.sort_values('percentual_alto_risco', ascending=True)

fig4 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Municípios por Nível de Risco', 'Percentual de Municípios em Alto Risco'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}]],
    horizontal_spacing=0.15
)

# Subplot 1: Barras AGRUPADAS (lado a lado) - Melhor para valores pequenos
fig4.add_trace(
    go.Bar(
        name='Alto Risco (Crítico/Alto)',
        y=risco_summary['bacia'].tolist(),
        x=risco_summary['alto_risco'].tolist(),
        orientation='h',
        marker=dict(color='#d32f2f', line=dict(color='white', width=2)),
        text=[f"<b>{int(val)}</b>" for val in risco_summary['alto_risco']],
        textposition='outside',
        textfont=dict(color='#d32f2f', size=11),
        hovertemplate='<b>%{y}</b><br>Alto Risco: %{x} municípios<extra></extra>',
        offsetgroup=1
    ),
    row=1, col=1
)

fig4.add_trace(
    go.Bar(
        name='Baixo/Médio Risco',
        y=risco_summary['bacia'].tolist(),
        x=risco_summary['baixo_medio_risco'].tolist(),
        orientation='h',
        marker=dict(color='#388e3c', line=dict(color='white', width=2)),
        text=[f"<b>{int(val)}</b>" for val in risco_summary['baixo_medio_risco']],
        textposition='outside',
        textfont=dict(color='#388e3c', size=11),
        hovertemplate='<b>%{y}</b><br>Baixo/Médio Risco: %{x} municípios<extra></extra>',
        offsetgroup=2
    ),
    row=1, col=1
)

# Subplot 2: Barras - Percentual de Alto Risco
fig4.add_trace(
    go.Bar(
        y=risco_summary['bacia'].tolist(),
        x=risco_summary['percentual_alto_risco'].tolist(),
        orientation='h',
        marker=dict(
            color=risco_summary['percentual_alto_risco'].tolist(),
            colorscale=[[0, '#388e3c'], [0.5, '#fbc02d'], [1, '#d32f2f']],
            line=dict(color='white', width=2),
            showscale=False
        ),
        text=[f"{val:.1f}%" for val in risco_summary['percentual_alto_risco']],
        textposition='outside',
        textfont=dict(size=11, color='#333'),
        showlegend=False,
        hovertemplate='<b>%{y}</b><br>Alto Risco: %{x:.1f}%<extra></extra>'
    ),
    row=1, col=2
)

# Configurar eixos
fig4.update_xaxes(title_text="Número de Municípios", row=1, col=1, showgrid=True, gridcolor='#e0e0e0')
fig4.update_xaxes(title_text="Percentual (%)", row=1, col=2, showgrid=True, gridcolor='#e0e0e0', range=[0, max(risco_summary['percentual_alto_risco']) * 1.3])
fig4.update_yaxes(row=1, col=1, tickfont=dict(size=10))
fig4.update_yaxes(row=1, col=2, showticklabels=True, tickfont=dict(size=10))

fig4.update_layout(
    title={
        'text': '⚠️ Análise de Risco de Contaminação por Bacia Hidrográfica',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    barmode='group',  # Barras lado a lado ao invés de empilhadas
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    height=550,
    margin=dict(l=20, r=120, t=100, b=60),
    bargap=0.15,  # Espaço entre grupos de barras
    bargroupgap=0.05,  # Espaço entre barras dentro do grupo
    legend=dict(
        title=dict(text='<b>Classificação</b>', font=dict(size=12)),
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='center',
        x=0.3,
        font=dict(size=11),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ccc',
        borderwidth=1
    ),
    hoverlabel=dict(bgcolor="white", font_size=13),
    annotations=[
        dict(
            text="<i>Barras agrupadas facilitam comparação | Vermelho = Alto Risco, Verde = Baixo/Médio Risco</i>",
            xref="paper", yref="paper",
            x=0.5, y=-0.10,
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    ]
)

# ==============================================
# GRÁFICO 5: Comparação Populacional vs Resíduos (MELHORADO)
# ==============================================
print("5️⃣ Gráfico 5: Comparação entre população e resíduos...")

fig5 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('População por Bacia (habitantes)', 'Resíduos Domésticos por Bacia (t/ano)'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}]],
    horizontal_spacing=0.15
)

# Subplot 1: População - BARRAS HORIZONTAIS
fig5.add_trace(
    go.Bar(
        y=df_bacias_sorted['bacia'].tolist(),
        x=df_bacias_sorted['populacao'].tolist(),
        orientation='h',
        marker=dict(
            color=[cores_bacias[b] for b in df_bacias_sorted['bacia']],
            line=dict(color='white', width=2)
        ),
        text=[f"{val/1000:.0f}k hab" for val in df_bacias_sorted['populacao']],
        textposition='outside',
        textfont=dict(size=11, color='#333'),
        name='População',
        hovertemplate='<b>%{y}</b><br>População: %{x:,.0f} habitantes<extra></extra>',
        showlegend=False
    ),
    row=1, col=1
)

# Subplot 2: Resíduos - BARRAS HORIZONTAIS
fig5.add_trace(
    go.Bar(
        y=df_bacias_sorted['bacia'].tolist(),
        x=df_bacias_sorted['domestico_t_ano'].tolist(),
        orientation='h',
        marker=dict(
            color=[cores_bacias[b] for b in df_bacias_sorted['bacia']],
            line=dict(color='white', width=2)
        ),
        text=[f"{val/1000:.0f}k t/ano" for val in df_bacias_sorted['domestico_t_ano']],
        textposition='outside',
        textfont=dict(size=11, color='#333'),
        name='Resíduos',
        hovertemplate='<b>%{y}</b><br>Resíduos: %{x:,.0f} toneladas/ano<extra></extra>',
        showlegend=False
    ),
    row=1, col=2
)

# Configurar eixos
fig5.update_xaxes(title_text="População (habitantes)", row=1, col=1, showgrid=True, gridcolor='#e0e0e0', tickformat=',')
fig5.update_xaxes(title_text="Resíduos (toneladas/ano)", row=1, col=2, showgrid=True, gridcolor='#e0e0e0', tickformat=',')
fig5.update_yaxes(row=1, col=1, tickfont=dict(size=11), automargin=True)
fig5.update_yaxes(row=1, col=2, tickfont=dict(size=11), automargin=True)

fig5.update_layout(
    title={
        'text': '📈 Comparação: População × Geração de Resíduos por Bacia',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    showlegend=False,
    height=550,
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='white',
    margin=dict(l=220, r=180, t=100, b=60),
    annotations=[
        dict(
            text="<i>Ordenadas do menor para o maior | Cores consistentes com outros gráficos</i>",
            xref="paper", yref="paper",
            x=0.5, y=-0.08,
            showarrow=False,
            font=dict(size=10, color='#666')
        )
    ]
)

# ==============================================
# GRÁFICO 6: Painel de Indicadores (3 painéis)
# ==============================================
print("6️⃣ Gráfico 6: Painel com indicadores-chave...")

fig6 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Top 3 Bacias - Volume Total de Resíduos',
        '⚠️ Taxa Uniforme: 346.75 kg/hab/ano em todo o Estado',
        'Distribuição da População por Bacia (%)',
        'Distribuição dos Resíduos por Bacia (%)'
    ),
    specs=[[{'type': 'bar'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'bar'}]],
    vertical_spacing=0.20,
    horizontal_spacing=0.15
)

# Top 3 Volume - HORIZONTAL
top3_volume = df_bacias.nlargest(3, 'domestico_t_ano').sort_values('domestico_t_ano', ascending=True)
fig6.add_trace(
    go.Bar(
        y=top3_volume['bacia'].tolist(),
        x=top3_volume['domestico_t_ano'].tolist(),
        orientation='h',
        marker=dict(
            color=[cores_bacias[b] for b in top3_volume['bacia']],
            line=dict(color='white', width=2)
        ),
        text=[f"<b>{val/1000:.0f}k t/ano</b>" for val in top3_volume['domestico_t_ano']],
        textposition='outside',
        textfont=dict(size=11, color='#333'),
        showlegend=False,
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} toneladas/ano<extra></extra>'
    ),
    row=1, col=1
)

# Painel Informativo - Explicação sobre taxa uniforme
fig6.add_annotation(
    x=0.5, y=0.5,
    xref='x2', yref='y2',
    text=('<b style="font-size:16px">Geração Per Capita Uniforme</b><br><br>'
          'Os dados foram calculados usando uma<br>'
          '<b style="font-size:18px; color:#1976d2">taxa uniforme de 0.95 kg/hab/dia</b><br><br>'
          'Todas as 8 bacias têm a mesma geração per capita:<br>'
          '<b style="font-size:24px; color:#d32f2f">346.75 kg/hab/ano</b><br><br>'
          '<i style="font-size:12px; color:#666">Isso reflete uma estimativa estadual média,<br>'
          'sem variação regional específica.</i>'),
    showarrow=False,
    font=dict(size=13, color='#333'),
    align='center',
    bgcolor='#fff3e0',
    bordercolor='#ff9800',
    borderwidth=2,
    borderpad=15
)

# Barras - População por bacia (simples)
df_pop_sorted = df_bacias.sort_values('populacao', ascending=True)
fig6.add_trace(
    go.Bar(
        y=df_pop_sorted['bacia'],
        x=df_pop_sorted['percentual_pop'],
        orientation='h',
        marker=dict(
            color=[cores_bacias[b] for b in df_pop_sorted['bacia']],
            line=dict(color='white', width=2)
        ),
        text=[f"{val:.1f}%" for val in df_pop_sorted['percentual_pop']],
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{y}</b><br>%{x:.1f}% da população<extra></extra>',
        showlegend=False
    ),
    row=2, col=1
)

# Barras - Resíduos por bacia (simples)
df_res_sorted = df_bacias.sort_values('domestico_t_ano', ascending=True)
fig6.add_trace(
    go.Bar(
        y=df_res_sorted['bacia'],
        x=df_res_sorted['percentual_residuos'],
        orientation='h',
        marker=dict(
            color=[cores_bacias[b] for b in df_res_sorted['bacia']],
            line=dict(color='white', width=2)
        ),
        text=[f"{val:.1f}%" for val in df_res_sorted['percentual_residuos']],
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{y}</b><br>%{x:.1f}% dos resíduos<extra></extra>',
        showlegend=False
    ),
    row=2, col=2
)

# Configurar eixos
fig6.update_xaxes(showgrid=True, gridcolor='#e0e0e0', title_text="Volume (t/ano)", title_font=dict(size=11), row=1, col=1)
fig6.update_xaxes(showgrid=False, visible=False, row=1, col=2)  # Ocultar eixo no painel informativo
fig6.update_xaxes(ticksuffix='%', row=2, col=1, showgrid=True, gridcolor='#e0e0e0', range=[0, 50])
fig6.update_xaxes(ticksuffix='%', row=2, col=2, showgrid=True, gridcolor='#e0e0e0', range=[0, 50])

fig6.update_yaxes(row=1, col=1, tickfont=dict(size=10))
fig6.update_yaxes(showgrid=False, visible=False, row=1, col=2)  # Ocultar eixo no painel informativo
fig6.update_yaxes(row=2, col=1, tickfont=dict(size=10))
fig6.update_yaxes(row=2, col=2, tickfont=dict(size=10))

fig6.update_layout(
    title={
        'text': '🎯 Painel de Indicadores - Destaques por Bacia Hidrográfica',
        'font': {'size': 22, 'color': '#1976d2', 'family': 'Arial Black'},
        'x': 0.5,
        'xanchor': 'center'
    },
    height=750,
    paper_bgcolor='white',
    plot_bgcolor='#f8f9fa',
    margin=dict(l=180, r=120, t=100, b=60),
    showlegend=False
)

# ==============================================
# GERAR HTML INTEGRADO
# ==============================================
print("\n📄 Gerando dashboard HTML integrado...")

# Estatísticas gerais
total_pop = df_bacias['populacao'].sum()
total_dom = df_bacias['domestico_t_ano'].sum()
total_rec = df_bacias['reciclavel_t_ano'].sum()
num_bacias = len(df_bacias)
num_municipios = len(df_municipios)
media_percapita = df_bacias['domestico_per_capita'].mean()

# Risco
risco_critico = len(df_municipios[df_municipios['risco'] == 'CRÍTICO'])
risco_alto = len(df_municipios[df_municipios['risco'] == 'ALTO'])
risco_medio = len(df_municipios[df_municipios['risco'] == 'MÉDIO'])
risco_baixo = len(df_municipios[df_municipios['risco'] == 'BAIXO'])

html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>Dashboard - Análise por Bacias Hidrográficas | Santa Catarina</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 10px;
            color: #333;
            -webkit-overflow-scrolling: touch;
        }}
        
        /* Mobile First */
        @media (min-width: 768px) {{
            body {{
                padding: 20px;
            }}
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            line-height: 1.3;
        }}
        
        header p {{
            font-size: 14px;
            opacity: 0.95;
        }}
        
        /* Desktop */
        @media (min-width: 768px) {{
            header {{
                padding: 40px;
            }}
            header h1 {{
                font-size: 42px;
            }}
            header p {{
                font-size: 18px;
            }}
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
        }}
        
        @media (min-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
            }}
        }}
        
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #1976d2;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        @media (min-width: 768px) {{
            .stat-card {{
                padding: 25px;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }}
        }}
        
        .stat-card .icon {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        
        @media (min-width: 768px) {{
            .stat-card .icon {{
                font-size: 40px;
                margin-bottom: 10px;
            }}
        }}
        
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #1976d2;
            margin: 8px 0;
        }}
        
        @media (min-width: 768px) {{
            .stat-card .value {{
                font-size: 32px;
                margin: 10px 0;
            }}
        }}
        
        .stat-card .label {{
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        @media (min-width: 768px) {{
            .stat-card .label {{
                font-size: 14px;
                letter-spacing: 1px;
            }}
        }}
        
        .risk-card {{
            border-left-color: #d32f2f;
        }}
        
        .risk-card .value {{
            color: #d32f2f;
        }}
        
        .chart-container {{
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        @media (min-width: 768px) {{
            .chart-container {{
                padding: 40px;
            }}
        }}
        
        .chart-container:last-child {{
            border-bottom: none;
        }}
        
        .chart-title {{
            font-size: 18px;
            color: #1976d2;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #1976d2;
            line-height: 1.4;
        }}
        
        @media (min-width: 768px) {{
            .chart-title {{
                font-size: 24px;
                margin-bottom: 20px;
                padding-left: 15px;
                border-left: 5px solid #1976d2;
            }}
        }}
        
        .chart {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .info-box {{
            background: #e3f2fd;
            border-left: 5px solid #1976d2;
            padding: 20px;
            margin: 30px;
            border-radius: 8px;
        }}
        
        .info-box h3 {{
            color: #1976d2;
            margin-bottom: 10px;
        }}
        
        .info-box ul {{
            margin-left: 20px;
            line-height: 1.8;
        }}
        
        footer {{
            background: #263238;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        footer a {{
            color: #64b5f6;
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        .map-link {{
            display: inline-block;
            background: #1976d2;
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 5px;
            transition: background 0.3s ease;
            font-size: 14px;
            touch-action: manipulation;
        }}
        
        @media (min-width: 768px) {{
            .map-link {{
                padding: 15px 30px;
                margin: 20px;
                font-size: 16px;
            }}
            .map-link:hover {{
                background: #0d47a1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌊 Dashboard de Análise por Bacias Hidrográficas</h1>
            <p>Gestão de Resíduos Sólidos em Santa Catarina</p>
            <div style="margin-top: 20px;">
                <a href="mapa_bacias_hidrograficas.html" class="map-link" target="_blank">
                    🗺️ Ver Mapa Interativo das Bacias
                </a>
                <a href="relatorio_tecnico.html" class="map-link" target="_blank" style="background: #d32f2f;">
                    📄 Relatório Técnico Completo
                </a>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">🌊</div>
                <div class="value">{num_bacias}</div>
                <div class="label">Bacias Hidrográficas</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📍</div>
                <div class="value">{num_municipios}</div>
                <div class="label">Municípios</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">👥</div>
                <div class="value">{total_pop/1000000:.2f}M</div>
                <div class="label">População Total</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🗑️</div>
                <div class="value">{total_dom/1000000:.2f}M</div>
                <div class="label">Resíduos Domésticos (t/ano)</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">♻️</div>
                <div class="value">{total_rec/1000:.0f}k</div>
                <div class="label">Resíduos Recicláveis (t/ano)</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="value">{media_percapita:.0f}</div>
                <div class="label">Média Per Capita (kg/hab/ano)</div>
            </div>
            
            <div class="stat-card risk-card">
                <div class="icon">🔴</div>
                <div class="value">{risco_critico + risco_alto}</div>
                <div class="label">Municípios Risco Crítico/Alto</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🟢</div>
                <div class="value">{risco_baixo}</div>
                <div class="label">Municípios Risco Baixo</div>
            </div>
        </div>
        
        <div class="info-box">
            <h3>📋 Sobre esta Análise</h3>
            <p>Este dashboard apresenta uma análise abrangente da geração de resíduos sólidos domésticos em Santa Catarina, 
            organizada por <strong>bacias hidrográficas</strong>. Esta abordagem permite:</p>
            <ul>
                <li><strong>Gestão territorial integrada</strong> - considerar os limites naturais dos recursos hídricos</li>
                <li><strong>Avaliação de risco ambiental</strong> - identificar áreas críticas para contaminação de corpos d'água</li>
                <li><strong>Planejamento regional</strong> - facilitar consórcios e cooperação entre municípios da mesma bacia</li>
                <li><strong>Priorização de investimentos</strong> - direcionar recursos para áreas de maior impacto potencial</li>
            </ul>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart1"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart2"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart3"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart4"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart5"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart" id="chart6"></div>
        </div>
        
        <div class="info-box">
            <h3>💡 Principais Insights e Recomendações</h3>
            <ul>
                <li><strong>"Outras Bacias"</strong> concentra {df_bacias[df_bacias['bacia']=='Outras Bacias']['percentual_pop'].values[0]:.1f}% da população estadual - requer atenção especial</li>
                <li><strong>Bacias Litorâneas</strong> (Central e Norte) somam alta densidade populacional e volume de resíduos</li>
                <li><strong>{risco_critico + risco_alto} municípios</strong> estão em risco CRÍTICO ou ALTO - prioridade para intervenção</li>
                <li><strong>Consórcios regionais</strong> por bacia podem otimizar logística e reduzir custos</li>
                <li><strong>Monitoramento de recursos hídricos</strong> deve ser intensificado nas bacias de maior geração</li>
                <li><strong>Programas de educação ambiental</strong> regionalizados podem aumentar efetividade</li>
            </ul>
        </div>
        
        <footer>
            <h3>🎓 Análise de Resíduos Sólidos - Santa Catarina</h3>
            <p>Dashboard desenvolvido para apoio à gestão ambiental e planejamento territorial</p>
            <p style="margin-top: 10px;">
                <strong>👤 Autor:</strong> Ronan Armando Caetano
            </p>
            <p style="margin-top: 15px; font-size: 14px;">
                📊 Dados: IBGE Censo 2022 | 🔬 Metodologia: Estimativa baseada em população<br>
                <a href="mapa_bacias_hidrograficas.html" target="_blank">🗺️ Ver Mapa Interativo</a> | 
                <a href="relatorio_tecnico.html" target="_blank">📄 Relatório Técnico Completo</a> |
                <a href="dashboard.html" target="_blank">📈 Dashboard Municipal</a>
            </p>
            <p style="margin-top: 15px; font-size: 12px; color: #999;">
                Desenvolvido com Python, GeoPandas, Plotly e Folium | 
                Assistência: GitHub Copilot (IA) | 
                Outubro de 2025
            </p>
        </footer>
    </div>
    
    <script>
        // Configuração mobile-friendly para Plotly
        var config = {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'toggleSpikelines'],
            displaylogo: false,
            toImageButtonOptions: {{
                format: 'png',
                filename: 'grafico_bacias_sc',
                height: 800,
                width: 1200,
                scale: 2
            }},
            scrollZoom: false
        }};
        
        // Gráfico 1
        var fig1 = {fig1.to_json()};
        Plotly.newPlot('chart1', fig1.data, fig1.layout, config);
        
        // Gráfico 2
        var fig2 = {fig2.to_json()};
        Plotly.newPlot('chart2', fig2.data, fig2.layout, config);
        
        // Gráfico 3
        var fig3 = {fig3.to_json()};
        Plotly.newPlot('chart3', fig3.data, fig3.layout, config);
        
        // Gráfico 4
        var fig4 = {fig4.to_json()};
        Plotly.newPlot('chart4', fig4.data, fig4.layout, config);
        
        // Gráfico 5
        var fig5 = {fig5.to_json()};
        Plotly.newPlot('chart5', fig5.data, fig5.layout, config);
        
        // Gráfico 6
        var fig6 = {fig6.to_json()};
        Plotly.newPlot('chart6', fig6.data, fig6.layout, config);
        
        // Ajuste automático de tamanho para mobile
        window.addEventListener('resize', function() {{
            Plotly.Plots.resize('chart1');
            Plotly.Plots.resize('chart2');
            Plotly.Plots.resize('chart3');
            Plotly.Plots.resize('chart4');
            Plotly.Plots.resize('chart5');
            Plotly.Plots.resize('chart6');
        }});
    </script>
</body>
</html>
"""

# Salvar dashboard
output_file = r'outputs\dashboard_bacias.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

import os
file_size = os.path.getsize(output_file) / (1024 * 1024)

print(f"\n✅ Dashboard criado com sucesso!")
print(f"📁 Arquivo: {output_file}")
print(f"💾 Tamanho: {file_size:.2f} MB")
print(f"\n{'='*70}")
print("🎉 DASHBOARD DE BACIAS HIDROGRÁFICAS COMPLETO!")
print(f"{'='*70}")
print(f"\n📊 {len([fig1, fig2, fig3, fig4, fig5, fig6])} gráficos interativos criados")
print(f"🌊 {num_bacias} bacias hidrográficas analisadas")
print(f"📍 {num_municipios} municípios classificados")
print(f"\n💡 Abra o arquivo em seu navegador para visualizar!")

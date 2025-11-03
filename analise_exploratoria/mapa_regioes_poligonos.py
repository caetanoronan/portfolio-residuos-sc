"""
Análise de Resíduos por Macro-Região (RGI) - Versão com Polígonos
Sem heatmaps - apenas camadas de polígonos por região
"""
import os
import geopandas as gpd
import folium
from folium.plugins import Fullscreen, MiniMap
import pandas as pd
import requests
import warnings

def fetch_population():
    """Busca população via API IBGE"""
    try:
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93?localidades=N6[all]"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        rows = []
        for item in data[0]['resultados']:
            for loc in item['series']:
                codigo = str(loc['localidade']['id']).zfill(7)
                pop = list(loc['serie'].values())[0] if loc['serie'] else None
                if pop:
                    rows.append({'codigo_ibge': codigo, 'populacao': float(pop)})
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"⚠️ Erro ao buscar população: {e}")
        return None

def fmt_num(x, decimals=0, suffix=''):
    """Formata número com segurança para NaN"""
    try:
        if pd.isna(x) or x is None:
            return 'N/A'
        return f"{x:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.') + suffix
    except:
        return 'N/A'

print("="*60)
print("📊 MAPA DE RESÍDUOS POR REGIÃO (POLÍGONOS)")
print("="*60)

print("\n1) Lendo setores censitários...")
gdf = gpd.read_file(r'analise_exploratoria\SC_setores_CD2022.gpkg')
print(f"   ✓ {len(gdf):,} setores carregados")

print("\n2) Obtendo população por município (IBGE → fallback: setores)...")
pop_df = fetch_population()

print("\n3) Preparando dados municipais...")
gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)

# Dissolver setores por município mantendo informações de região
print("   ▶ Criando geometrias municipais (dissolve)...")
muni = gdf.dissolve(by='CD_MUN_str', aggfunc={
    'NM_MUN': 'first',
    'CD_RGI': 'first',
    'NM_RGI': 'first'
}).reset_index()
muni = gpd.GeoDataFrame(muni, geometry='geometry', crs=gdf.crs)

# Merge com dados populacionais
if pop_df is not None:
    muni = muni.merge(pop_df, left_on='CD_MUN_str', right_on='codigo_ibge', how='left')
else:
    # Fallback: agregar população dos setores
    pop_setores = gdf.groupby('CD_MUN_str').agg({'populacao': 'sum'}).reset_index()
    muni = muni.merge(pop_setores, on='CD_MUN_str', how='left')

# Calcular estimativas de resíduos
muni['domestico_t_ano'] = muni['populacao'] * 0.95 * 365 / 1000
muni['reciclavel_t_ano'] = muni['domestico_t_ano'] * 0.10

print(f"   ✓ {len(muni)} municípios preparados")

# Identificar campo correto do nome do município após merge
nm_mun_field = 'NM_MUN' if 'NM_MUN' in muni.columns else ('NM_MUN_y' if 'NM_MUN_y' in muni.columns else 'NM_MUN_x')

print("\n4) Simplificando geometrias para web (100 m)...")
muni_3857 = muni.to_crs(3857)
muni_3857['geometry'] = muni_3857.geometry.simplify(100, preserve_topology=True)
muni = muni_3857.to_crs(4326)

print("\n5) Construindo mapa Folium...")
center = [muni.geometry.centroid.y.mean(), muni.geometry.centroid.x.mean()]

# Calcular bounds de SC para limitar visualização
bounds = muni.total_bounds  # [minx, miny, maxx, maxy]
sw = [bounds[1], bounds[0]]  # southwest corner [lat, lon]
ne = [bounds[3], bounds[2]]  # northeast corner [lat, lon]

m = folium.Map(
    location=center, 
    zoom_start=7,
    tiles='CartoDB positron',
    min_zoom=6,        # Zoom mínimo (não permite afastar muito)
    max_zoom=13,       # Zoom máximo (não permite aproximar muito)
    max_bounds=True,   # Restringe pan aos limites
    max_bounds_viscosity=0.5  # Suavidade ao atingir limites
)

# Definir limites geográficos (bounds) de SC
m.fit_bounds([sw, ne])

# Adicionar plugins
Fullscreen(position='topleft').add_to(m)
MiniMap(toggle_display=True).add_to(m)

# Identificar regiões únicas
regioes = muni[[cd for cd in ['CD_RGI', 'NM_RGI'] if cd in muni.columns]].drop_duplicates().sort_values('NM_RGI')

# Cores por região (palette ColorBrewer qualitativa - 15 cores acessíveis)
cores_disponiveis = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
    '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5',
    '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f'
]

cores_regioes = {}
for i, (_, regiao) in enumerate(regioes.iterrows()):
    cores_regioes[regiao['CD_RGI']] = cores_disponiveis[i % len(cores_disponiveis)]

print(f"   ✓ {len(regioes)} regiões identificadas")

# Criar uma camada (FeatureGroup) por região
feature_groups = {}
for _, regiao in regioes.iterrows():
    fg = folium.FeatureGroup(name=f"{regiao['NM_RGI']}", show=True)
    feature_groups[regiao['CD_RGI']] = fg
    fg.add_to(m)

# Adicionar municípios às camadas por região
for _, row in muni.iterrows():
    cd_rgi = row.get('CD_RGI')
    if cd_rgi not in feature_groups:
        continue
    
    cor = cores_regioes.get(cd_rgi, '#999999')
    nm_mun = row.get(nm_mun_field, 'N/A')
    nm_rgi = row.get('NM_RGI', 'N/A')
    pop = row.get('populacao', 0)
    dom = row.get('domestico_t_ano', 0)
    rec = row.get('reciclavel_t_ano', 0)
    
    popup_html = f"""
    <div style='font-family: Arial; font-size: 13px; min-width: 260px;'>
        <h4 style='margin: 0 0 10px 0; padding-bottom: 5px; border-bottom: 2px solid {cor};'>
            📍 {nm_mun}
        </h4>
        <div style='background: #f0f0f0; padding: 8px; margin: 5px 0; border-radius: 4px;'>
            <strong style='color: {cor};'>🗺️ Região:</strong> {nm_rgi}
        </div>
        <div style='background: #e3f2fd; padding: 6px; margin: 3px 0; border-left: 3px solid #034e7b;'>
            <strong>🔵 Doméstico:</strong> {fmt_num(dom)} t/ano
        </div>
        <div style='background: #fff3e0; padding: 6px; margin: 3px 0; border-left: 3px solid #e65100;'>
            <strong>🟡 Reciclável:</strong> {fmt_num(rec)} t/ano
        </div>
        <div style='background: #f5f5f5; padding: 6px; margin: 3px 0; border-radius: 4px;'>
            <strong>👥 População:</strong> {fmt_num(pop)} hab
        </div>
    </div>
    """
    
    folium.GeoJson(
        row['geometry'],
        style_function=lambda x, cor=cor: {
            'fillColor': cor,
            'color': '#333',
            'weight': 1,
            'fillOpacity': 0.6
        },
        tooltip=f"{nm_mun} ({nm_rgi})",
        popup=folium.Popup(popup_html, max_width=350)
    ).add_to(feature_groups[cd_rgi])

print(f"   ✔ Camadas criadas por região")

# Limite estadual (contorno discreto)
print("   ▶ Criando limite estadual...")
try:
    limite_sc = muni.dissolve().geometry.iloc[0]
    folium.GeoJson(
        limite_sc,
        name='Limite de Santa Catarina',
        style_function=lambda x: {
            'color': '#000000',
            'weight': 1,
            'opacity': 0.3,
            'fillOpacity': 0
        },
        tooltip='Santa Catarina'
    ).add_to(m)
except Exception as e:
    warnings.warn(f"Falha ao criar limite estadual: {e}")

# Controles
folium.LayerControl(position='topleft', collapsed=False).add_to(m)

# Legenda com cores das regiões
legenda_items = []
for _, regiao in regioes.iterrows():
    cor = cores_regioes[regiao['CD_RGI']]
    legenda_items.append(f"<div style='margin: 3px 0;'><span style='display: inline-block; width: 16px; height: 16px; background: {cor}; border: 1px solid #333; margin-right: 6px;'></span>{regiao['NM_RGI']}</div>")

legenda_html = f'''
<div id="legend-panel" style="position: fixed; bottom: 20px; left: 20px; width: 320px; background: rgba(255, 255, 255, 0.95); 
            border: 3px solid #333; border-radius: 10px; padding: 0; z-index: 9999;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3); backdrop-filter: blur(10px); transition: all 0.3s ease;">
    
    <!-- Header com botão de toggle -->
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; 
                background: rgba(0,0,0,0.05); border-radius: 7px 7px 0 0; cursor: pointer; border-bottom: 2px solid #333;"
         onclick="toggleLegend()">
        <h4 style="margin: 0; font-size: 15px; font-weight: bold;">♿ Legenda - Regiões (RGI)</h4>
        <span id="legend-toggle" style="font-size: 20px; font-weight: bold; user-select: none;">+</span>
    </div>
    
    <!-- Conteúdo recolhível (inicia fechado) -->
    <div id="legend-content" style="display: none; padding: 15px; max-height: 50vh; overflow-y: auto;">
        <div style="font-size: 12px; line-height: 1.6;">
            {''.join(legenda_items)}
        </div>
        <div style="margin: 15px 0 8px 0; padding-top: 10px; border-top: 1px solid #ddd;">
            <div style="padding: 4px; background: #e3f2fd; margin: 3px 0; border-left: 3px solid #034e7b;">
                <strong>🔵 Domésticos</strong>
            </div>
            <div style="padding: 4px; background: #fff3e0; margin: 3px 0; border-left: 3px solid #e65100;">
                <strong>🟡 Recicláveis</strong>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 10px; text-align: center; color: #666;">
            ✓ Regiões Geográficas Imediatas (IBGE)<br>
            📍 {len(muni)} municípios | {len(regioes)} RGIs
        </div>
    </div>
</div>

<script>
function toggleLegend() {{
    const content = document.getElementById('legend-content');
    const toggle = document.getElementById('legend-toggle');
    const panel = document.getElementById('legend-panel');
    
    if (content.style.display === 'none') {{
        content.style.display = 'block';
        toggle.textContent = '−';
        panel.style.width = '320px';
    }} else {{
        content.style.display = 'none';
        toggle.textContent = '+';
        panel.style.width = 'auto';
    }}
}}
</script>
'''
m.get_root().html.add_child(folium.Element(legenda_html))

# Calcular estatísticas gerais para o painel
total_pop = muni['populacao'].sum()
total_dom = muni['domestico_t_ano'].sum()
total_rec = muni['reciclavel_t_ano'].sum()
media_dom_mun = muni['domestico_t_ano'].mean()
media_rec_mun = muni['reciclavel_t_ano'].mean()

# Estatísticas por região para encontrar top 3
regioes_stats = muni.groupby('NM_RGI').agg({
    'populacao': 'sum',
    'domestico_t_ano': 'sum',
    'reciclavel_t_ano': 'sum',
    'CD_MUN_str': 'count'
}).reset_index().sort_values('domestico_t_ano', ascending=False)

top_regiao_1 = regioes_stats.iloc[0]['NM_RGI'] if len(regioes_stats) > 0 else 'N/A'
top_regiao_2 = regioes_stats.iloc[1]['NM_RGI'] if len(regioes_stats) > 1 else 'N/A'
top_regiao_3 = regioes_stats.iloc[2]['NM_RGI'] if len(regioes_stats) > 2 else 'N/A'

# Painel de estatísticas no lado esquerdo acima da legenda (recolhível + semi-transparente)
stats_panel_html = f'''
<div id="stats-panel" style="position: fixed; top: 80px; left: 20px; width: 340px; 
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
            border-radius: 12px; padding: 0; z-index: 9998; box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            font-family: Arial, sans-serif; color: white; backdrop-filter: blur(10px); transition: all 0.3s ease;">
    
    <!-- Header com botão de toggle -->
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; 
                background: rgba(0,0,0,0.2); border-radius: 12px 12px 0 0; border-bottom: 2px solid rgba(255,255,255,0.3);
                cursor: pointer;"
         onclick="toggleStats()">
        <h3 style="margin: 0; font-size: 18px; font-weight: bold;">
            📊 Estatísticas - Santa Catarina
        </h3>
        <span id="stats-toggle" style="font-size: 24px; font-weight: bold; user-select: none;">+</span>
    </div>
    
    <!-- Conteúdo recolhível (inicia fechado) -->
    <div id="stats-content" style="display: none;">
        <!-- Stats Grid -->
        <div style="padding: 15px;">
            <!-- Card 1: População -->
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 8px; 
                        padding: 12px; margin-bottom: 10px; border-left: 4px solid #4caf50;">
                <div style="font-size: 11px; opacity: 0.9; margin-bottom: 4px;">👥 POPULAÇÃO TOTAL</div>
                <div style="font-size: 24px; font-weight: bold; line-height: 1.2;">{fmt_num(total_pop)}</div>
                <div style="font-size: 10px; opacity: 0.8; margin-top: 4px;">habitantes em {len(muni)} municípios</div>
            </div>
            
            <!-- Card 2: Resíduos Domésticos -->
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 8px; 
                        padding: 12px; margin-bottom: 10px; border-left: 4px solid #034e7b;">
                <div style="font-size: 11px; opacity: 0.9; margin-bottom: 4px;">🔵 RESÍDUOS DOMÉSTICOS</div>
                <div style="font-size: 24px; font-weight: bold; line-height: 1.2;">{fmt_num(total_dom)} t/ano</div>
                <div style="font-size: 10px; opacity: 0.8; margin-top: 4px;">
                    📊 Média: {fmt_num(media_dom_mun)} t/ano por município
                </div>
            </div>
            
            <!-- Card 3: Resíduos Recicláveis -->
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 8px; 
                        padding: 12px; margin-bottom: 10px; border-left: 4px solid #e65100;">
                <div style="font-size: 11px; opacity: 0.9; margin-bottom: 4px;">🟡 RESÍDUOS RECICLÁVEIS</div>
                <div style="font-size: 24px; font-weight: bold; line-height: 1.2;">{fmt_num(total_rec)} t/ano</div>
                <div style="font-size: 10px; opacity: 0.8; margin-top: 4px;">
                    📊 Média: {fmt_num(media_rec_mun)} t/ano por município
                </div>
            </div>
            
            <!-- Card 4: Top 3 Regiões -->
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 8px; 
                        padding: 12px; border-left: 4px solid #ffd92f;">
                <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">🏆 TOP 3 REGIÕES (RGI)</div>
                <div style="font-size: 11px; line-height: 1.6;">
                    <div style="padding: 3px 0;">🥇 {top_regiao_1}</div>
                    <div style="padding: 3px 0;">🥈 {top_regiao_2}</div>
                    <div style="padding: 3px 0;">🥉 {top_regiao_3}</div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 0 0 12px 12px; 
                    text-align: center; font-size: 9px; opacity: 0.8; border-top: 1px solid rgba(255,255,255,0.2);">
            ✓ Dados: IBGE Censo 2022 | Taxa: 0,95 kg/hab/dia
        </div>
    </div>
</div>

<script>
function toggleStats() {{
    const content = document.getElementById('stats-content');
    const toggle = document.getElementById('stats-toggle');
    const panel = document.getElementById('stats-panel');
    
    if (content.style.display === 'none') {{
        content.style.display = 'block';
        toggle.textContent = '−';
        panel.style.width = '340px';
    }} else {{
        content.style.display = 'none';
        toggle.textContent = '+';
        panel.style.width = 'auto';
    }}
}}
</script>
'''
m.get_root().html.add_child(folium.Element(stats_panel_html))

# CSS responsivo para mobile e painéis recolhíveis
mobile_css = '''
<style>
/* Estilos para painéis recolhíveis */
#stats-panel, #legend-panel {
    transition: all 0.3s ease;
}

/* Hover nos headers para indicar que são clicáveis */
#stats-panel > div:first-child:hover,
#legend-panel > div:first-child:hover {
    background: rgba(0,0,0,0.15) !important;
}

@media (max-width: 768px) {
    .leaflet-control-minimap { display: none; }
    
    /* Legenda de regiões - mobile */
    #legend-panel {
        bottom: 10px !important;
        left: 10px !important;
        right: 10px !important;
        width: auto !important;
        max-width: 95vw !important;
    }
    
    #legend-content {
        max-height: 35vh !important;
        font-size: 11px !important;
    }
    
    #legend-panel h4 {
        font-size: 13px !important;
    }
    
    /* Painel de estatísticas - mobile */
    #stats-panel {
        top: 60px !important;
        left: 10px !important;
        right: 10px !important;
        width: auto !important;
        max-width: 95vw !important;
    }
    
    #stats-panel h3 {
        font-size: 14px !important;
    }
    
    #stats-content > div:first-child {
        padding: 10px !important;
    }
    
    #stats-content > div:first-child > div {
        padding: 8px !important;
        margin-bottom: 8px !important;
    }
    
    #stats-content > div:first-child > div > div:nth-child(2) {
        font-size: 20px !important;
    }
}

/* Ajuste para desktop - evitar sobreposição */
@media (min-width: 769px) {
    .leaflet-control-container .leaflet-top.leaflet-right {
        top: 450px !important;
    }
}

/* Animação suave para abrir/fechar */
#stats-content, #legend-content {
    overflow: hidden;
    transition: all 0.3s ease;
}
</style>
'''
m.get_root().html.add_child(folium.Element(mobile_css))

# Salvar
output_path = r'outputs\mapa_regioes_poligonos.html'
m.save(output_path)

file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f"\n✔ Mapa salvo em {output_path}")
print(f"💾 Tamanho: {file_size:.2f} MB")

# Estatísticas por região
print("\n📊 RESUMO POR REGIÃO:")
print("-" * 90)
regioes_stats = muni.groupby('NM_RGI').agg({
    'populacao': 'sum',
    'domestico_t_ano': 'sum',
    'reciclavel_t_ano': 'sum',
    'CD_MUN_str': 'count'
}).reset_index()
regioes_stats.columns = ['Região', 'População', 'Doméstico (t/ano)', 'Reciclável (t/ano)', 'N° Municípios']

for _, row in regioes_stats.sort_values('Doméstico (t/ano)', ascending=False).iterrows():
    print(f"{row['Região']:35} | {row['N° Municípios']:2.0f} mun | Pop: {row['População']:>10,.0f} | "
          f"Dom: {row['Doméstico (t/ano)']:>8,.0f} t/ano | Rec: {row['Reciclável (t/ano)']:>7,.0f} t/ano")

print("\n" + "="*60)
print("✅ MAPA DE REGIÕES (POLÍGONOS) CONCLUÍDO!")
print("="*60)

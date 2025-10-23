"""
Mapa interativo sem heatmap: marcadores proporcionais por município
- Camadas: Doméstico (t/ano) e Reciclável (t/ano)
- Clusters para melhor desempenho
- Popups com informações principais
- Controles: Fullscreen, LayerControl, MiniMap
"""
import os
import math
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster, MiniMap, Fullscreen
import requests

# ----------------------------
# 1) Carregar dados
# ----------------------------
print("Carregando setores...")
gdf = gpd.read_file(r'SC_setores_CD2022.gpkg')

print("Buscando população (IBGE 2022)...")
url = "https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93?localidades=N6[all]"
rows = []
try:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    for item in data[0]['resultados']:
        for loc in item['series']:
            codigo = str(loc['localidade']['id']).zfill(7)
            nome = loc['localidade']['nome']
            pop = list(loc['serie'].values())[0] if loc['serie'] else None
            if pop and codigo.startswith('42'):  # apenas SC
                rows.append({'codigo_ibge': codigo, 'municipio': nome, 'populacao': float(pop)})
except Exception as e:
    print(f"⚠️ Erro ao buscar IBGE: {e}")

pop_df = pd.DataFrame(rows)
if pop_df.empty:
    raise RuntimeError("Sem dados de população para SC")

# Estimativas simples (coerentes com o dashboard)
pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10

# Agregar setores -> municípios (usando primeiro polígono/centro)
gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
muni_agg = gdf.groupby('CD_MUN_str').agg({'NM_MUN': 'first', 'geometry': 'first'}).reset_index()
muni = gpd.GeoDataFrame(muni_agg, geometry='geometry', crs=gdf.crs).rename(columns={'CD_MUN_str': 'CD_MUN'})

# Merge com população
muni = muni.merge(pop_df, left_on='CD_MUN', right_on='codigo_ibge', how='left')
muni_wgs = muni.to_crs(epsg=4326)

# ----------------------------
# 2) Função de escala de raio
# ----------------------------
def scale_radius(series, min_r=4, max_r=16):
    s = series.fillna(0).astype(float)
    s_min, s_max = float(s.min()), float(s.max())
    if s_max <= 0 or s_max == s_min:
        return [min_r] * len(s)
    return [min_r + (val - s_min) / (s_max - s_min) * (max_r - min_r) for val in s]

r_dom = scale_radius(muni_wgs['domestico_t_ano'])
r_rec = scale_radius(muni_wgs['reciclavel_t_ano'])

# ----------------------------
# 3) Criar mapa base
# ----------------------------
centroid_mean = muni_wgs.geometry.centroid
center = [centroid_mean.y.mean(), centroid_mean.x.mean()]
m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron')

Fullscreen().add_to(m)
MiniMap(toggle_display=True, minimized=True).add_to(m)

# Grupos de camadas
grp_dom = folium.FeatureGroup(name='🔵 Doméstico (t/ano)', show=True)
grp_rec = folium.FeatureGroup(name='🟡 Reciclável (t/ano)', show=False)

cl_dom = MarkerCluster(name='Cluster Doméstico', show=True)
cl_rec = MarkerCluster(name='Cluster Reciclável', show=True)

grp_dom.add_child(cl_dom)
grp_rec.add_child(cl_rec)

# ----------------------------
# 4) Adicionar marcadores
# ----------------------------
for i, row in muni_wgs.iterrows():
    geom = row.geometry
    if geom is None:
        continue
    c = geom.centroid
    nome = row.get('NM_MUN', row.get('municipio', 'N/D'))
    dom = float(row.get('domestico_t_ano', 0) or 0)
    rec = float(row.get('reciclavel_t_ano', 0) or 0)

    popup_html = f"""
    <div style='font-family: Arial; font-size: 13px; min-width: 220px;'>
      <h4 style='margin:0 0 10px 0; color:#667eea;'>{nome}</h4>
      <div style='background:#e3f2fd; padding:6px; margin:4px 0; border-left:4px solid #034e7b;'>
        <b>🔵 Doméstico:</b> {dom:,.0f} t/ano
      </div>
      <div style='background:#fff3e0; padding:6px; margin:4px 0; border-left:4px solid #e65100;'>
        <b>🟡 Reciclável:</b> {rec:,.0f} t/ano
      </div>
    </div>
    """

    # Doméstico
    folium.CircleMarker(
        location=[c.y, c.x],
        radius=r_dom[i],
        color='#034e7b',
        weight=1,
        fill=True,
        fill_color='#1976d2',
        fill_opacity=0.55,
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(cl_dom)

    # Reciclável
    folium.CircleMarker(
        location=[c.y, c.x],
        radius=r_rec[i],
        color='#e65100',
        weight=1,
        fill=True,
        fill_color='#fbc02d',
        fill_opacity=0.55,
        popup=folium.Popup(popup_html, max_width=320)
    ).add_to(cl_rec)

# Adicionar grupos ao mapa
grp_dom.add_to(m)
grp_rec.add_to(m)

# ----------------------------
# 5) Legenda
# ----------------------------
legend_html = f'''
<div style="position: fixed; bottom: 50px; right: 50px; width: 260px; background: white; 
            border: 2px solid #333; border-radius: 10px; padding: 12px; z-index: 9999;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
    <h4 style="margin: 0 0 8px 0;">Legenda</h4>
    <div style="margin: 6px 0; padding: 6px; background: #e3f2fd; border-left: 4px solid #034e7b;">
        <b style="color:#034e7b;">🔵 Doméstico</b> — tamanho ∝ t/ano
    </div>
    <div style="margin: 6px 0; padding: 6px; background: #fff3e0; border-left: 4px solid #e65100;">
        <b style="color:#e65100;">🟡 Reciclável</b> — tamanho ∝ t/ano
    </div>
    <div style="margin-top: 6px; font-size: 11px; color: #666;">
        📍 {len(muni_wgs)} municípios
    </div>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl(position='topleft', collapsed=False).add_to(m)

# ----------------------------
# 6) Salvar
# ----------------------------
output_path = os.path.join('outputs', 'interactive_points_map.html')
m.save(output_path)

file_size = os.path.getsize(output_path) / (1024 * 1024)
print("\n✅ Mapa de pontos criado com sucesso!")
print(f"📊 {len(muni_wgs)} municípios")
print(f"💾 Tamanho do arquivo: {file_size:.2f} MB")
print(f"📁 Salvo em: {os.path.abspath(output_path)}")

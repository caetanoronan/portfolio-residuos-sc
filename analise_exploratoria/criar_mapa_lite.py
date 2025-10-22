"""
Versão LITE do mapa - apenas agregação municipal para GitHub Pages
"""
import os
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import pandas as pd
import requests

# Buscar dados populacionais
def fetch_population():
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
    except:
        return None

print("Carregando setores...")
gdf = gpd.read_file(r'c:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Portifolio\analise_exploratoria\SC_setores_CD2022.gpkg')

print("Buscando população...")
pop_df = fetch_population()

if pop_df is not None:
    pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
    pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10
    
    print("Agregando por município...")
    # Agregar sem dissolver (mais rápido)
    gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    muni_agg = gdf.groupby('CD_MUN_str').agg({'NM_MUN': 'first', 'geometry': 'first'}).reset_index()
    muni = gpd.GeoDataFrame(muni_agg, geometry='geometry', crs=gdf.crs)
    muni = muni.rename(columns={'CD_MUN_str': 'CD_MUN'})
    
    # Merge com dados
    muni = muni.merge(pop_df, left_on='CD_MUN', right_on='codigo_ibge', how='left')
    
    print("Criando mapa...")
    muni_wgs = muni.to_crs(epsg=4326)
    center = [muni_wgs.geometry.centroid.y.mean(), muni_wgs.geometry.centroid.x.mean()]
    
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron')
    
    # Heatmap doméstico
    centroids = muni_wgs.copy()
    centroids['centroid'] = centroids.geometry.centroid
    
    heat_dom = [[pt.y, pt.x, wt] for pt, wt in zip(centroids['centroid'], centroids['domestico_t_ano']) 
                if pd.notna(wt) and wt > 0]
    if heat_dom:
        HeatMap(heat_dom, name='🔵 Resíduos Domésticos', radius=25, blur=30, 
                gradient={0.0: '#d0d1e6', 0.5: '#74a9cf', 1.0: '#034e7b'}).add_to(m)
    
    # Heatmap reciclável
    heat_rec = [[pt.y, pt.x, wt] for pt, wt in zip(centroids['centroid'], centroids['reciclavel_t_ano']) 
                if pd.notna(wt) and wt > 0]
    if heat_rec:
        HeatMap(heat_rec, name='🟡 Resíduos Recicláveis', radius=25, blur=30,
                gradient={0.0: '#ffffcc', 0.5: '#feb24c', 1.0: '#e31a1c'}).add_to(m)
    
    # Markers municipais (mais leve que polígonos)
    for _, row in muni_wgs.iterrows():
        centroid = row['geometry'].centroid
        popup = f"""<div style="font-family: Arial; font-size: 13px; min-width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: #667eea;">{row.get('NM_MUN', 'N/A')}</h4>
        <div style="background: #e3f2fd; padding: 5px; margin: 3px 0; border-left: 3px solid #034e7b;">
        <b>🔵 Doméstico:</b> {row.get('domestico_t_ano', 0):,.0f} t/ano</div>
        <div style="background: #fff3e0; padding: 5px; margin: 3px 0; border-left: 3px solid #e65100;">
        <b>🟡 Reciclável:</b> {row.get('reciclavel_t_ano', 0):,.0f} t/ano</div>
        </div>"""
        
        folium.CircleMarker(
            location=[centroid.y, centroid.x],
            radius=3,
            color='#667eea',
            fill=True,
            fillColor='#667eea',
            fillOpacity=0.6,
            popup=folium.Popup(popup, max_width=300)
        ).add_to(m)
    
    # Legenda
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 250px; background: white; 
                border: 3px solid #333; border-radius: 10px; padding: 15px; z-index: 9999;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #333;">♿ Legenda Acessível</h4>
        <div style="margin: 8px 0; padding: 6px; background: #e3f2fd; border-left: 4px solid #034e7b;">
            <b style="color: #034e7b;">🔵 Azul:</b> Domésticos
        </div>
        <div style="margin: 8px 0; padding: 6px; background: #fff3e0; border-left: 4px solid #e65100;">
            <b style="color: #e65100;">🟡 Amarelo:</b> Recicláveis
        </div>
        <div style="margin-top: 10px; font-size: 11px; text-align: center; color: #666;">
            ✓ Paleta segura para daltonismo<br>
            📍 {len(muni)} municípios de SC
        </div>
    </div>
    '''.replace('{len(muni)}', str(len(muni)))
    m.get_root().html.add_child(folium.Element(legend_html))
    
    folium.LayerControl(position='topleft').add_to(m)
    
    output_path = r'c:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Portifolio\analise_exploratoria\outputs\interactive_waste_map.html'
    m.save(output_path)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Mapa LITE criado com sucesso!")
    print(f"📊 {len(muni)} municípios")
    print(f"💾 Tamanho do arquivo: {file_size:.2f} MB")
    print(f"📁 Salvo em: {output_path}")
else:
    print("❌ Erro ao buscar dados de população")

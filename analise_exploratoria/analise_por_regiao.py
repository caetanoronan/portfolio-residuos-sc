"""
Análise de Resíduos por Macro-Região (RGI - Regiões Geográficas Imediatas)
Versão leve para GitHub Pages
"""
import os
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import pandas as pd
import requests

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
        print(f"Erro ao buscar população: {e}")
        return None

print("="*60)
print("📊 ANÁLISE DE RESÍDUOS POR MACRO-REGIÃO")
print("="*60)

print("\n1️⃣ Carregando dados dos setores censitários...")
gdf = gpd.read_file(r'SC_setores_CD2022.gpkg')
print(f"   ✓ {len(gdf):,} setores carregados")

print("\n2️⃣ Identificando Regiões Geográficas Imediatas (RGI)...")
regioes = gdf[['CD_RGI', 'NM_RGI']].drop_duplicates().sort_values('NM_RGI')
print(f"   ✓ {len(regioes)} RGIs identificadas:")
for _, row in regioes.iterrows():
    print(f"      • {row['NM_RGI']}")

print("\n3️⃣ Buscando dados populacionais (API IBGE)...")
pop_df = fetch_population()

if pop_df is not None:
    print(f"   ✓ População de {len(pop_df)} municípios obtida")
    
    # Calcular estimativas de resíduos
    pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
    pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10
    
    print("\n4️⃣ Agregando dados por município...")
    gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    
    # Agregar por município mantendo região
    muni_gdf = gdf.groupby('CD_MUN_str').agg({
        'NM_MUN': 'first',
        'CD_RGI': 'first',
        'NM_RGI': 'first',
        'geometry': 'first'
    }).reset_index()
    muni_gdf = gpd.GeoDataFrame(muni_gdf, geometry='geometry', crs=gdf.crs)
    
    # Merge com dados populacionais
    muni_gdf = muni_gdf.merge(pop_df, left_on='CD_MUN_str', right_on='codigo_ibge', how='left')
    print(f"   ✓ {len(muni_gdf)} municípios agregados")
    
    print("\n5️⃣ Agregando por Região Geográfica Imediata...")
    regioes_agg = muni_gdf.groupby(['CD_RGI', 'NM_RGI']).agg({
        'populacao': 'sum',
        'domestico_t_ano': 'sum',
        'reciclavel_t_ano': 'sum'
    }).reset_index()
    
    print(f"\n📊 RESUMO POR REGIÃO:")
    print("-" * 80)
    for _, row in regioes_agg.sort_values('domestico_t_ano', ascending=False).iterrows():
        print(f"{row['NM_RGI']:40} | Pop: {row['populacao']:>10,.0f} | "
              f"Dom: {row['domestico_t_ano']:>8,.0f} t/ano | "
              f"Rec: {row['reciclavel_t_ano']:>7,.0f} t/ano")
    
    print("\n6️⃣ Criando mapa interativo por região...")
    muni_wgs = muni_gdf.to_crs(epsg=4326)
    center = [muni_wgs.geometry.centroid.y.mean(), muni_wgs.geometry.centroid.x.mean()]
    
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron')
    
    # Cores por região (palette qualitativa acessível)
    cores_regioes = {}
    cores_disponiveis = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 
                         '#ffff33', '#a65628', '#f781bf', '#999999', '#66c2a5',
                         '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f']
    
    for i, (_, regiao) in enumerate(regioes.iterrows()):
        cores_regioes[regiao['CD_RGI']] = cores_disponiveis[i % len(cores_disponiveis)]
    
    # Adicionar municípios com cores por região
    for _, row in muni_wgs.iterrows():
        if pd.notna(row.get('domestico_t_ano')):
            cor_regiao = cores_regioes.get(row['CD_RGI'], '#999999')
            centroid = row['geometry'].centroid
            
            popup_html = f"""
            <div style="font-family: Arial; font-size: 13px; min-width: 250px;">
                <h4 style="margin: 0 0 10px 0; padding-bottom: 5px; border-bottom: 2px solid {cor_regiao};">
                    📍 {row.get('NM_MUN', 'N/A')}
                </h4>
                <div style="background: #f0f0f0; padding: 8px; margin: 5px 0; border-radius: 4px;">
                    <strong style="color: {cor_regiao};">🗺️ Região:</strong> {row.get('NM_RGI', 'N/A')}
                </div>
                <div style="background: #e3f2fd; padding: 6px; margin: 3px 0; border-left: 3px solid #034e7b;">
                    <strong>🔵 Doméstico:</strong> {row.get('domestico_t_ano', 0):,.0f} t/ano
                </div>
                <div style="background: #fff3e0; padding: 6px; margin: 3px 0; border-left: 3px solid #e65100;">
                    <strong>🟡 Reciclável:</strong> {row.get('reciclavel_t_ano', 0):,.0f} t/ano
                </div>
                <div style="background: #f5f5f5; padding: 6px; margin: 3px 0; border-radius: 4px;">
                    <strong>👥 População:</strong> {row.get('populacao', 0):,.0f} hab
                </div>
            </div>
            """
            
            folium.CircleMarker(
                location=[centroid.y, centroid.x],
                radius=4,
                color=cor_regiao,
                fill=True,
                fillColor=cor_regiao,
                fillOpacity=0.7,
                weight=2,
                popup=folium.Popup(popup_html, max_width=350)
            ).add_to(m)
    
    # Heatmap doméstico
    centroids = muni_wgs.copy()
    centroids['centroid'] = centroids.geometry.centroid
    heat_dom = [[pt.y, pt.x, wt] for pt, wt in zip(centroids['centroid'], centroids['domestico_t_ano']) 
                if pd.notna(wt) and wt > 0]
    if heat_dom:
        HeatMap(heat_dom, name='🔵 Resíduos Domésticos (Heatmap)', radius=25, blur=30, 
                gradient={0.0: '#d0d1e6', 0.5: '#74a9cf', 1.0: '#034e7b'}).add_to(m)
    
    # Heatmap reciclável
    heat_rec = [[pt.y, pt.x, wt] for pt, wt in zip(centroids['centroid'], centroids['reciclavel_t_ano']) 
                if pd.notna(wt) and wt > 0]
    if heat_rec:
        HeatMap(heat_rec, name='🟡 Resíduos Recicláveis (Heatmap)', radius=25, blur=30,
                gradient={0.0: '#ffffcc', 0.5: '#feb24c', 1.0: '#e31a1c'}).add_to(m)
    
    # Legenda
    legenda_regioes = "<br>".join([f'<span style="color: {cores_regioes[cd]};">●</span> {nm}' 
                                   for cd, nm in zip(regioes['CD_RGI'], regioes['NM_RGI'])])
    
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 300px; background: white; 
                border: 3px solid #333; border-radius: 10px; padding: 15px; z-index: 9999;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3); max-height: 70vh; overflow-y: auto;">
        <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #333;">♿ Legenda - Regiões</h4>
        <div style="font-size: 12px; line-height: 1.8; margin: 10px 0;">
            {legenda_regioes}
        </div>
        <div style="margin: 15px 0 8px 0; padding-top: 10px; border-top: 1px solid #ddd;">
            <div style="padding: 4px; background: #e3f2fd; margin: 3px 0;">
                <strong style="color: #034e7b;">🔵</strong> Domésticos
            </div>
            <div style="padding: 4px; background: #fff3e0; margin: 3px 0;">
                <strong style="color: #e65100;">🟡</strong> Recicláveis
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 10px; text-align: center; color: #666;">
            ✓ Cores por RGI (IBGE)<br>
            📍 {len(muni_gdf)} municípios | {len(regioes)} regiões
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    folium.LayerControl(position='topleft').add_to(m)
    
    output_path = r'outputs\mapa_regioes.html'
    m.save(output_path)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Mapa por REGIÃO criado com sucesso!")
    print(f"💾 Tamanho: {file_size:.2f} MB")
    print(f"📁 Salvo em: {output_path}")
    
    # Salvar CSV com dados agregados por região
    csv_path = r'outputs\resumo_por_regiao.csv'
    regioes_agg.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"📊 Resumo CSV salvo em: {csv_path}")
    
else:
    print("❌ Erro ao obter dados de população")

print("\n" + "="*60)
print("✅ ANÁLISE CONCLUÍDA!")
print("="*60)

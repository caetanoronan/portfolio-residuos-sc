"""
Script rápido para atualizar apenas o mapa com limites de zoom
Usa os dados já processados anteriormente
"""
import geopandas as gpd
import folium
import pandas as pd
import os

print("🗺️  Atualizando mapa com limites de zoom...")

# Carregar dados já processados
print("📊 Carregando dados processados...")
bacias_csv = pd.read_csv('outputs/resumo_por_bacia.csv')

# Carregar GeoPackage completo
print("📦 Carregando geometrias...")
gdf = gpd.read_file('outputs/sectors_with_waste_estimates.gpkg')

# Dissolver por bacia
print("🔄 Criando geometrias das bacias...")
muni_gdf = gdf.dissolve(by='CD_MUN', aggfunc='first')
muni_gdf = muni_gdf.merge(bacias_csv, left_on='bacia', right_on='bacia', how='left')

# Criar geometrias das bacias
bacias_geom = muni_gdf.dissolve(by='bacia', aggfunc='sum')
bacias_geom = bacias_geom.to_crs(epsg=4326)
bacias_geom = bacias_geom.merge(bacias_csv, left_on='bacia', right_on='bacia', how='left')

# Criar mapa com limites de zoom
print("🗺️  Criando mapa interativo com limites de zoom...")
center = [bacias_geom.geometry.centroid.y.mean(), bacias_geom.geometry.centroid.x.mean()]

m = folium.Map(
    location=center, 
    zoom_start=7, 
    tiles='CartoDB positron',
    min_zoom=6,      # Limite de afastamento
    max_zoom=13,     # Limite de aproximação
    max_bounds=True  # Restringe aos limites
)

# Cores por bacia
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

# Adicionar polígonos
print("🎨 Adicionando polígonos...")
for _, bacia_row in bacias_geom.iterrows():
    cor = cores_bacias.get(bacia_row['bacia'], '#999999')
    
    popup_html = f"""
    <div style="font-family: Arial; font-size: 14px; min-width: 300px;">
        <h3 style="margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 3px solid {cor}; color: {cor};">
            🌊 {bacia_row['bacia']}
        </h3>
        <div style="background: #e3f2fd; padding: 10px; margin: 8px 0; border-left: 5px solid #1976d2; border-radius: 4px;">
            <strong>👥 População Total:</strong><br>
            <span style="font-size: 18px; font-weight: bold; color: #1976d2;">
                {bacia_row['populacao']:,.0f} habitantes
            </span>
        </div>
        <div style="background: #e8f5e9; padding: 10px; margin: 8px 0; border-left: 5px solid #388e3c; border-radius: 4px;">
            <strong>🗑️ Resíduos Domésticos:</strong><br>
            <span style="font-size: 18px; font-weight: bold; color: #388e3c;">
                {bacia_row['domestico_t_ano']:,.0f} t/ano
            </span>
        </div>
        <div style="background: #fff3e0; padding: 10px; margin: 8px 0; border-left: 5px solid #f57c00; border-radius: 4px;">
            <strong>♻️ Resíduos Recicláveis:</strong><br>
            <span style="font-size: 18px; font-weight: bold; color: #f57c00;">
                {bacia_row['reciclavel_t_ano']:,.0f} t/ano
            </span>
        </div>
        <div style="background: #f3e5f5; padding: 10px; margin: 8px 0; border-left: 5px solid {cor}; border-radius: 4px;">
            <strong>📊 Per Capita:</strong><br>
            <span style="font-size: 16px; font-weight: bold; color: {cor};">
                {(bacia_row['domestico_t_ano'] / bacia_row['populacao'] * 1000):.1f} kg/hab/ano
            </span>
        </div>
    </div>
    """
    
    folium.GeoJson(
        bacia_row['geometry'],
        style_function=lambda feature, cor=cor: {
            'fillColor': cor,
            'color': '#ffffff',
            'weight': 4,
            'fillOpacity': 0.6
        },
        tooltip=folium.Tooltip(bacia_row['bacia'], sticky=False),
        popup=folium.Popup(popup_html, max_width=400)
    ).add_to(m)

# Adicionar legenda
print("📋 Adicionando legenda...")
legend_html = '''
<div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; 
     background: white; padding: 20px; border-radius: 10px; 
     box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 2px solid #1976d2;">
    <h4 style="margin: 0 0 15px 0; color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 8px;">
        🌊 Bacias Hidrográficas
    </h4>
'''

for bacia, cor in cores_bacias.items():
    legend_html += f'''
    <div style="margin: 8px 0; display: flex; align-items: center;">
        <div style="width: 30px; height: 20px; background: {cor}; 
             border: 2px solid white; margin-right: 10px; border-radius: 3px;"></div>
        <span style="font-size: 13px; color: #333;">{bacia}</span>
    </div>
    '''

legend_html += '''
    <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0; font-size: 11px; color: #666;">
        🔍 Zoom: 6-13 níveis<br>
        📍 Clique para detalhes
    </div>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# Salvar
print("💾 Salvando mapa...")
m.save('outputs/mapa_bacias_hidrograficas.html')

file_size = os.path.getsize('outputs/mapa_bacias_hidrograficas.html') / (1024*1024)
print(f"\n✅ Mapa atualizado com sucesso!")
print(f"📁 Arquivo: outputs/mapa_bacias_hidrograficas.html")
print(f"💾 Tamanho: {file_size:.2f} MB")
print(f"🔍 Zoom configurado: min=6, max=13")

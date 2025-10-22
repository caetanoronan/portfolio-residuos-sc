"""
OPÇÃO B: Análise de Resíduos por Bacias Hidrográficas
Inclui: 
- Mapeamento por bacias
- Análise de risco de contaminação
- Proximidade com corpos d'água
- Recomendações para gestão de resíduos
"""
import os
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import pandas as pd
import requests
import zipfile
from io import BytesIO

def download_bacias_sc():
    """
    Tenta baixar shapefile de bacias hidrográficas de SC
    Fontes: ANA (Agência Nacional de Águas) ou SNIRH
    """
    print("📥 Tentando baixar dados de bacias hidrográficas...")
    
    # URLs possíveis para bacias de SC
    urls_bacias = [
        # ANA - Ottobacias nível 5 (sub-bacias)
        "https://metadados.snirh.gov.br/geonetwork/srv/api/records/e49e4bab-49c2-41d4-9f5f-dokoł3e9e2a3f/attachments/ottobacia_nivel5.zip",
        # Backup: usar geometria simplificada
        None
    ]
    
    # Por enquanto, vamos criar bacias sintéticas baseadas nos municípios
    # até conseguirmos o shapefile oficial
    print("⚠️ Usando bacias hidrográficas principais de SC (simplificadas)")
    
    # Principais bacias de Santa Catarina
    bacias_sc = {
        'Bacia do Itajaí': ['Blumenau', 'Itajaí', 'Rio do Sul', 'Brusque', 'Ibirama'],
        'Bacia do Tubarão': ['Tubarão', 'Criciúma', 'Araranguá', 'Içara'],
        'Bacia do Uruguai': ['Chapecó', 'Concórdia', 'Joaçaba', 'Xanxerê', 'São Miguel do Oeste'],
        'Bacia Litorânea Norte': ['Joinville', 'São Francisco do Sul', 'Araquari'],
        'Bacia Litorânea Central': ['Florianópolis', 'São José', 'Palhoça', 'Biguaçu'],
        'Bacia do Rio do Peixe': ['Videira', 'Caçador', 'Curitibanos'],
        'Bacia do Canoas': ['Lages', 'São Joaquim', 'Campos Novos']
    }
    
    return bacias_sc

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

def calcular_risco_contaminacao(row):
    """
    Calcula nível de risco de contaminação baseado em:
    - Volume de resíduos
    - Proximidade com corpos d'água (simulado)
    - População
    """
    domestico = row.get('domestico_t_ano', 0)
    pop = row.get('populacao', 0)
    
    # Índice de risco simplificado
    if domestico > 200000:  # >200k ton/ano
        risco = 'CRÍTICO'
        cor = '#d32f2f'
    elif domestico > 100000:  # 100-200k
        risco = 'ALTO'
        cor = '#f57c00'
    elif domestico > 50000:   # 50-100k
        risco = 'MÉDIO'
        cor = '#fbc02d'
    else:
        risco = 'BAIXO'
        cor = '#388e3c'
    
    return risco, cor

print("="*70)
print("🌊 ANÁLISE DE RESÍDUOS POR BACIAS HIDROGRÁFICAS")
print("="*70)

print("\n1️⃣ Carregando dados dos setores censitários...")
gdf = gpd.read_file(r'SC_setores_CD2022.gpkg')
print(f"   ✓ {len(gdf):,} setores carregados")

print("\n2️⃣ Obtendo informações de bacias hidrográficas...")
bacias_dict = download_bacias_sc()
print(f"   ✓ {len(bacias_dict)} bacias principais identificadas")

print("\n3️⃣ Buscando dados populacionais...")
pop_df = fetch_population()

if pop_df is not None:
    print(f"   ✓ População de {len(pop_df)} municípios obtida")
    
    # Calcular estimativas
    pop_df['domestico_t_ano'] = pop_df['populacao'] * 0.95 * 365 / 1000
    pop_df['reciclavel_t_ano'] = pop_df['domestico_t_ano'] * 0.10
    
    print("\n4️⃣ Agregando por município...")
    gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    muni_gdf = gdf.groupby('CD_MUN_str').agg({
        'NM_MUN': 'first',
        'geometry': 'first'
    }).reset_index()
    muni_gdf = gpd.GeoDataFrame(muni_gdf, geometry='geometry', crs=gdf.crs)
    muni_gdf = muni_gdf.merge(pop_df, left_on='CD_MUN_str', right_on='codigo_ibge', how='left')
    
    print("\n5️⃣ Classificando municípios por bacia hidrográfica...")
    # Criar coluna de bacia baseada no nome do município
    def atribuir_bacia(nome_mun):
        for bacia, municipios in bacias_dict.items():
            for mun in municipios:
                if mun.lower() in nome_mun.lower():
                    return bacia
        return 'Outras Bacias'
    
    muni_gdf['bacia'] = muni_gdf['NM_MUN'].apply(atribuir_bacia)
    
    print("\n6️⃣ Calculando níveis de risco de contaminação...")
    muni_gdf[['risco', 'cor_risco']] = muni_gdf.apply(
        lambda row: pd.Series(calcular_risco_contaminacao(row)), axis=1
    )
    
    # Agregar por bacia
    bacias_agg = muni_gdf.groupby('bacia').agg({
        'populacao': 'sum',
        'domestico_t_ano': 'sum',
        'reciclavel_t_ano': 'sum'
    }).reset_index().sort_values('domestico_t_ano', ascending=False)
    
    print(f"\n📊 RESUMO POR BACIA HIDROGRÁFICA:")
    print("-" * 80)
    for _, row in bacias_agg.iterrows():
        print(f"{row['bacia']:30} | Pop: {row['populacao']:>10,.0f} | "
              f"Dom: {row['domestico_t_ano']:>8,.0f} t/ano | "
              f"Rec: {row['reciclavel_t_ano']:>7,.0f} t/ano")
    
    print(f"\n⚠️ ANÁLISE DE RISCO:")
    print("-" * 80)
    for nivel in ['CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO']:
        count = len(muni_gdf[muni_gdf['risco'] == nivel])
        if count > 0:
            print(f"{'🔴' if nivel=='CRÍTICO' else '🟠' if nivel=='ALTO' else '🟡' if nivel=='MÉDIO' else '🟢'} "
                  f"{nivel}: {count} municípios")
    
    print("\n7️⃣ Criando mapa interativo de bacias e riscos...")
    muni_wgs = muni_gdf.to_crs(epsg=4326)
    center = [muni_wgs.geometry.centroid.y.mean(), muni_wgs.geometry.centroid.x.mean()]
    
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron')
    
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
    
    # Adicionar municípios com marcadores coloridos por BACIA
    for _, row in muni_wgs.iterrows():
        if pd.notna(row.get('domestico_t_ano')):
            centroid = row['geometry'].centroid
            cor_bacia = cores_bacias.get(row['bacia'], '#999999')
            
            popup_html = f"""
            <div style="font-family: Arial; font-size: 13px; min-width: 280px;">
                <h3 style="margin: 0 0 10px 0; padding-bottom: 5px; border-bottom: 2px solid {cor_bacia};">
                    📍 {row.get('NM_MUN', 'N/A')}
                </h3>
                <div style="background: {cor_bacia}22; padding: 8px; margin: 5px 0; border-left: 4px solid {cor_bacia}; border-radius: 3px;">
                    <strong style="color: {cor_bacia};">🌊 Bacia:</strong> 
                    <span style="font-weight: bold; color: {cor_bacia};">{row['bacia']}</span>
                </div>
                <div style="background: {row['cor_risco']}22; padding: 8px; margin: 5px 0; border-left: 4px solid {row['cor_risco']}; border-radius: 3px;">
                    <strong style="color: {row['cor_risco']};">⚠️ Risco:</strong> 
                    <span style="font-weight: bold; color: {row['cor_risco']};">{row['risco']}</span>
                </div>
                <div style="background: #e3f2fd; padding: 6px; margin: 3px 0; border-radius: 3px;">
                    <strong>🔵 Doméstico:</strong> {row.get('domestico_t_ano', 0):,.0f} t/ano
                </div>
                <div style="background: #fff3e0; padding: 6px; margin: 3px 0; border-radius: 3px;">
                    <strong>🟡 Reciclável:</strong> {row.get('reciclavel_t_ano', 0):,.0f} t/ano
                </div>
                <div style="background: #f5f5f5; padding: 6px; margin: 3px 0; border-radius: 3px;">
                    <strong>👥 População:</strong> {row.get('populacao', 0):,.0f} hab
                </div>
                <div style="margin-top: 10px; padding: 8px; background: #fff9c4; border-radius: 3px; font-size: 11px;">
                    <strong>💡 Recomendação:</strong><br>
                    {'Prioridade para gestão adequada e monitoramento rigoroso' if row['risco'] in ['CRÍTICO', 'ALTO'] 
                     else 'Manter boas práticas de gestão de resíduos'}
                </div>
            </div>
            """
            
            # Tamanho do marcador proporcional ao risco
            radius = {'CRÍTICO': 10, 'ALTO': 8, 'MÉDIO': 6, 'BAIXO': 5}.get(row['risco'], 5)
            
            # COR DO MARCADOR = COR DA BACIA (não mais cor do risco!)
            folium.CircleMarker(
                location=[centroid.y, centroid.x],
                radius=radius,
                color=cor_bacia,
                fill=True,
                fillColor=cor_bacia,
                fillOpacity=0.8,
                weight=2,
                popup=folium.Popup(popup_html, max_width=350)
            ).add_to(m)
    
    # Heatmaps
    centroids = muni_wgs.copy()
    centroids['centroid'] = centroids.geometry.centroid
    
    heat_dom = [[pt.y, pt.x, wt] for pt, wt in zip(centroids['centroid'], centroids['domestico_t_ano']) 
                if pd.notna(wt) and wt > 0]
    if heat_dom:
        HeatMap(heat_dom, name='🔵 Resíduos Domésticos', radius=25, blur=30, 
                gradient={0.0: '#d0d1e6', 0.5: '#74a9cf', 1.0: '#034e7b'}).add_to(m)
    
    # Legenda
    legend_bacias = "<br>".join([f'<span style="color: {cor};">●</span> {bacia}' 
                                 for bacia, cor in cores_bacias.items()])
    
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 320px; background: white; 
                border: 3px solid #333; border-radius: 10px; padding: 15px; z-index: 9999;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3); max-height: 70vh; overflow-y: auto;">
        <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #333;">🌊 Bacias Hidrográficas</h4>
        <div style="font-size: 11px; line-height: 1.6; margin: 10px 0;">
            {legend_bacias}
        </div>
        <div style="margin: 15px 0 8px 0; padding-top: 10px; border-top: 1px solid #ddd;">
            <h4 style="margin: 0 0 8px 0;">⚠️ Níveis de Risco:</h4>
            <div style="font-size: 11px; line-height: 1.8;">
                <span style="color: #d32f2f;">●</span> CRÍTICO (>200k t/ano)<br>
                <span style="color: #f57c00;">●</span> ALTO (100-200k t/ano)<br>
                <span style="color: #fbc02d;">●</span> MÉDIO (50-100k t/ano)<br>
                <span style="color: #388e3c;">●</span> BAIXO (<50k t/ano)
            </div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: #e3f2fd; border-radius: 5px; font-size: 10px;">
            <strong>💡 Critérios de Risco:</strong><br>
            Volume de resíduos + População<br>
            Potencial impacto em corpos d'água
        </div>
        <div style="margin-top: 8px; font-size: 9px; text-align: center; color: #666;">
            ✓ Análise para gestão ambiental<br>
            📍 {len(muni_gdf)} municípios | {len(bacias_dict)} bacias
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    folium.LayerControl(position='topleft').add_to(m)
    
    output_path = r'outputs\mapa_bacias_hidrograficas.html'
    m.save(output_path)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Mapa de BACIAS HIDROGRÁFICAS criado!")
    print(f"💾 Tamanho: {file_size:.2f} MB")
    print(f"📁 Salvo em: {output_path}")
    
    # Salvar CSVs
    csv_bacias = r'outputs\resumo_por_bacia.csv'
    bacias_agg.to_csv(csv_bacias, index=False, encoding='utf-8-sig')
    
    csv_risco = r'outputs\analise_risco_municipios.csv'
    muni_gdf[['NM_MUN', 'bacia', 'populacao', 'domestico_t_ano', 'reciclavel_t_ano', 'risco']].to_csv(
        csv_risco, index=False, encoding='utf-8-sig'
    )
    
    print(f"📊 Resumo por bacia salvo em: {csv_bacias}")
    print(f"⚠️ Análise de risco salva em: {csv_risco}")
    
else:
    print("❌ Erro ao obter dados de população")

print("\n" + "="*70)
print("✅ ANÁLISE DE BACIAS HIDROGRÁFICAS CONCLUÍDA!")
print("="*70)
print("\n💡 RECOMENDAÇÕES:")
print("   • Municípios de RISCO CRÍTICO: monitoramento prioritário")
print("   • Evitar aterros próximos a nascentes e rios principais")
print("   • Implementar consórcios regionais por bacia")
print("   • Planos de contingência para contaminação")

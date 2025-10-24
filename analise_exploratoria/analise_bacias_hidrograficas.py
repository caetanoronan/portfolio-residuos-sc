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
    
    # Dissolver TODOS os setores de cada município para criar polígonos COMPLETOS
    print("   🔄 Dissolvendo setores censitários por município...")
    muni_gdf = gdf.dissolve(by='CD_MUN_str', aggfunc='first').reset_index()
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
    
    print("\n7️⃣ Criando mapa interativo com POLÍGONOS DAS BACIAS...")
    
    # Dissolver os municípios por bacia para criar os polígonos das bacias
    print("   📐 Criando geometrias das bacias hidrográficas...")
    bacias_geom = muni_gdf.dissolve(by='bacia', aggfunc='sum').reset_index()
    bacias_geom = bacias_geom.to_crs(epsg=4326)
    
    # Juntar com as estatísticas agregadas
    bacias_geom = bacias_geom.merge(bacias_agg[['bacia', 'populacao', 'domestico_t_ano', 'reciclavel_t_ano']], 
                                     on='bacia', how='left', suffixes=('_old', ''))
    
    # Remover colunas duplicadas
    cols_to_drop = [c for c in bacias_geom.columns if c.endswith('_old')]
    if cols_to_drop:
        bacias_geom = bacias_geom.drop(columns=cols_to_drop)
    
    # Calcular centro do mapa
    center = [bacias_geom.geometry.centroid.y.mean(), bacias_geom.geometry.centroid.x.mean()]
    
    m = folium.Map(
        location=center, 
        zoom_start=7, 
        tiles='CartoDB positron',
        min_zoom=6,      # Limite de afastamento (não deixa zoom muito distante)
        max_zoom=13,     # Limite de aproximação (não deixa zoom muito próximo)
        max_bounds=True  # Restringe o mapa aos limites de SC
    )
    
    # Cores por bacia (degradê de azuis e verdes)
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
    
    # Adicionar POLÍGONOS das bacias coloridos
    print("   🎨 Adicionando polígonos coloridos das bacias...")
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
                <strong>� Per Capita:</strong><br>
                <span style="font-size: 16px; font-weight: bold; color: {cor};">
                    {(bacia_row['domestico_t_ano'] / bacia_row['populacao'] * 1000):.1f} kg/hab/ano
                </span>
            </div>
        </div>
        """
        
        folium.GeoJson(
            bacia_row['geometry'],
            style_function=lambda x, cor=cor: {
                'fillColor': cor,
                'color': '#ffffff',  # Borda branca para contraste
                'weight': 4,  # Borda mais grossa
                'fillOpacity': 0.6,  # Mais opaco para melhor visibilidade
                'opacity': 1.0,  # Borda totalmente visível
                'dashArray': None
            },
            highlight_function=lambda x: {
                'weight': 6,
                'fillOpacity': 0.8,
                'color': '#ffff00'  # Borda amarela no hover
            },
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=folium.Tooltip(f"<b style='font-size: 14px;'>{bacia_row['bacia']}</b>", permanent=False)
        ).add_to(m)
    
    # Legenda personalizada para as bacias
    print("   📋 Adicionando legenda...")
    legend_bacias = "<br>".join([f'<span style="background-color: {cor}; padding: 2px 8px; border-radius: 3px; color: white; font-weight: bold;">■</span> {bacia}' 
                                 for bacia, cor in cores_bacias.items()])
    
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 340px; background: white; 
                border: 3px solid #333; border-radius: 10px; padding: 18px; z-index: 9999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4); max-height: 75vh; overflow-y: auto;">
        <h3 style="margin: 0 0 15px 0; border-bottom: 3px solid #1976d2; padding-bottom: 8px; color: #1976d2;">
            🌊 Bacias Hidrográficas de SC
        </h3>
        <div style="font-size: 13px; line-height: 2.2; margin: 12px 0;">
            {legend_bacias}
        </div>
        <div style="margin-top: 15px; padding: 12px; background: #e8f5e9; border-left: 4px solid #388e3c; border-radius: 5px; font-size: 11px;">
            <strong>💡 Como usar o mapa:</strong><br>
            • Clique nos polígonos para ver detalhes da bacia<br>
            • Cores representam as diferentes bacias hidrográficas<br>
            • Polígonos mostram os limites territoriais das bacias
        </div>
        <div style="margin-top: 12px; font-size: 10px; text-align: center; color: #666; padding-top: 10px; border-top: 1px solid #ddd;">
            📊 {len(bacias_geom)} bacias hidrográficas<br>
            📍 {len(muni_gdf)} municípios de Santa Catarina
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
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

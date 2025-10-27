"""
Migra o mapa para usar polígonos oficiais de bacias (Ottobacias ANA) em SC.
Fluxo:
1) Carrega limites de SC a partir de SC_setores_CD2022.gpkg (dissolve)
2) Baixa Ottobacias via ArcGIS REST (camadas prováveis 0..6) recortando pela bbox de SC
3) Faz clip por SC
4) Gera polígonos de referência das 8 bacias (a partir de municípios por nome, igual ao pipeline anterior)
5) Atribui cada ottobacia à bacia de referência por maior área de interseção
6) Dissolve ottobacias por bacia e gera mapa Folium, reaproveitando estatísticas de outputs/resumo_por_bacia.csv

Observação: Se o endpoint da ANA estiver indisponível, o script aborta com instruções.
"""
import os
import io
import json
import math
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import folium
from folium import plugins

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

SETORES_GPKG = os.path.join(BASE_DIR, 'SC_setores_CD2022.gpkg')
RESUMO_CSV = os.path.join(BASE_DIR, 'outputs', 'resumo_por_bacia.csv')
OUT_MAP = os.path.join(BASE_DIR, 'outputs', 'mapa_bacias_hidrograficas.html')

SUPPORTED_EXTS = ('.gpkg', '.geojson', '.json', '.shp', '.zip', '.fgb')

def load_sc_boundary():
    gdf = gpd.read_file(SETORES_GPKG)
    sc = gdf.to_crs(4674) if gdf.crs is None else gdf
    sc_union = sc.dissolve().to_crs(4326)
    return sc_union.geometry.iloc[0]

def bbox_from_geom(geom):
    minx, miny, maxx, maxy = geom.bounds
    return minx, miny, maxx, maxy

def fetch_ottobacias_geojson(bbox):
    # Tenta múltiplas camadas possíveis
    base = 'https://geoservicos.ana.gov.br/arcgis/rest/services/BASES/OTTOBACIAS/MapServer'
    params_common = {
        'where': '1=1',
        'outFields': '*',
        'f': 'geojson',
        'geometryType': 'esriGeometryEnvelope',
        'inSR': 4326,
        'spatialRel': 'esriSpatialRelIntersects',
        'returnGeometry': 'true',
    }
    minx, miny, maxx, maxy = bbox
    geometry = json.dumps({'xmin': minx, 'ymin': miny, 'xmax': maxx, 'ymax': maxy, 'spatialReference': {'wkid': 4326}})

    last_err = None
    for layer in range(0, 7):
        url = f"{base}/{layer}/query"
        params = dict(params_common)
        params['geometry'] = geometry
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            if 'FeatureCollection' in r.text and 'features' in r.text:
                return r.json()
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Falha ao obter Ottobacias via ArcGIS REST: {last_err}")

def find_local_otto_file():
    """Procura um arquivo de ottobacias na pasta data/.
    Suporta: .gpkg, .geojson/.json, .shp, .zip (shapefile zipado), .fgb.
    Retorna caminho absoluto ou None.
    """
    if not os.path.isdir(DATA_DIR):
        return None
    # Preferências de extensão (geojson/gpkg primeiro)
    priority = ['.geojson', '.json', '.gpkg', '.fgb', '.zip', '.shp']
    candidates = []
    for name in os.listdir(DATA_DIR):
        lower = name.lower()
        if lower.endswith(SUPPORTED_EXTS):
            candidates.append(os.path.join(DATA_DIR, name))
    if not candidates:
        return None
    # Ordena por prioridade de extensão
    def prio_key(p):
        ext = os.path.splitext(p)[1].lower()
        try:
            return priority.index(ext)
        except ValueError:
            return 999
    candidates.sort(key=prio_key)
    return candidates[0]

def load_local_ottobacias(path: str) -> gpd.GeoDataFrame:
    """Carrega ottobacias de um arquivo local com GeoPandas.
    - .zip com shapefile: usar prefixo zip://
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.zip':
        # Shapefile zipado
        return gpd.read_file(f"zip://{path}")
    return gpd.read_file(path)

def geojson_to_gdf(geojson_obj):
    # GeoPandas lê via GeoDataFrame.from_features
    feats = geojson_obj.get('features', [])
    if not feats:
        raise ValueError('GeoJSON sem features')
    gdf = gpd.GeoDataFrame.from_features(feats, crs='EPSG:4326')
    return gdf

def build_bacias_ref_from_municipios():
    # Usa setores para dissolver por município, em seguida atribui bacia por nome
    gdf = gpd.read_file(SETORES_GPKG)
    gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    muni = gdf.dissolve(by='CD_MUN_str', aggfunc='first').reset_index()

    bacias_sc = {
        'Bacia do Itajaí': ['Blumenau', 'Itajaí', 'Rio do Sul', 'Brusque', 'Ibirama'],
        'Bacia do Tubarão': ['Tubarão', 'Criciúma', 'Araranguá', 'Içara'],
        'Bacia do Uruguai': ['Chapecó', 'Concórdia', 'Joaçaba', 'Xanxerê', 'São Miguel do Oeste'],
        'Bacia Litorânea Norte': ['Joinville', 'São Francisco do Sul', 'Araquari'],
        'Bacia Litorânea Central': ['Florianópolis', 'São José', 'Palhoça', 'Biguaçu'],
        'Bacia do Rio do Peixe': ['Videira', 'Caçador', 'Curitibanos'],
        'Bacia do Canoas': ['Lages', 'São Joaquim', 'Campos Novos'],
        'Outras Bacias': []
    }
    def atribuir_bacia(nome_mun: str) -> str:
        if not isinstance(nome_mun, str):
            return 'Outras Bacias'
        for bacia, municipios in bacias_sc.items():
            for mun in municipios:
                if mun.lower() in nome_mun.lower():
                    return bacia
        return 'Outras Bacias'

    if 'NM_MUN' not in muni.columns:
        raise KeyError("NM_MUN não encontrado no SC_setores_CD2022.gpkg")
    muni['bacia'] = muni['NM_MUN'].apply(atribuir_bacia)
    bacias_ref = muni.dissolve(by='bacia', aggfunc='sum').reset_index().to_crs(4326)
    return bacias_ref

def assign_ottobacia_to_bacia(otto: gpd.GeoDataFrame, ref: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Usa interseção de área para atribuir a bacia com maior sobreposição
    otto = otto.to_crs(3857)
    ref_ = ref.to_crs(3857)
    assigned = []
    for idx, row in otto.iterrows():
        geom = row.geometry
        best_bacia = None
        best_area = 0.0
        for _, r in ref_.iterrows():
            inter = geom.intersection(r.geometry)
            if inter.is_empty:
                continue
            area = inter.area
            if area > best_area:
                best_area = area
                best_bacia = r['bacia']
        assigned.append(best_bacia or 'Outras Bacias')
    otto_assigned = otto.to_crs(4326).copy()
    otto_assigned['bacia'] = assigned
    return otto_assigned

def build_map_from_official(bacias_official: gpd.GeoDataFrame, resumo: pd.DataFrame, otto_assigned: gpd.GeoDataFrame, sc_geom):
    # Cores ColorBrewer Set2 (8 cores qualitativas, colorblind-safe)
    # Fonte: https://colorbrewer2.org/#type=qualitative&scheme=Set2&n=8
    cores_bacias = {
        'Bacia do Itajaí': '#66c2a5',        # Verde-azulado claro
        'Bacia do Tubarão': '#fc8d62',       # Laranja suave
        'Bacia do Uruguai': '#8da0cb',       # Azul-lavanda
        'Bacia Litorânea Norte': '#e78ac3',  # Rosa suave
        'Bacia Litorânea Central': '#a6d854', # Verde-lima
        'Bacia do Rio do Peixe': '#ffd92f',  # Amarelo dourado
        'Bacia do Canoas': '#e5c494',        # Bege-dourado
        'Outras Bacias': '#b3b3b3'           # Cinza neutro
    }
    center = [bacias_official.geometry.centroid.y.mean(), bacias_official.geometry.centroid.x.mean()]
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron', min_zoom=6, max_zoom=13, max_bounds=True)

    # ===== PLUGINS PARA FUNCIONALIDADES EXTRAS =====
    
    # 1. MiniMap - Minimapa de navegação no canto inferior esquerdo
    minimap = plugins.MiniMap(toggle_display=True, tile_layer='CartoDB positron', 
                              position='bottomleft', width=150, height=150, zoom_level_offset=-5)
    minimap.add_to(m)
    
    # 2. Fullscreen - Botão de tela cheia
    plugins.Fullscreen(
        position='topleft',
        title='Tela Cheia',
        title_cancel='Sair da Tela Cheia',
        force_separate_button=True
    ).add_to(m)
    
    # 3. MousePosition - Mostra coordenadas do mouse (movido para topright para evitar sobreposição)
    plugins.MousePosition(
        position='topright',
        separator=' | ',
        prefix='Coords: ',
        lat_formatter="function(num) {return L.Util.formatNum(num, 4) + '°N';}",
        lng_formatter="function(num) {return L.Util.formatNum(num, 4) + '°O';}"
    ).add_to(m)
    
    # 4. MeasureControl - Medir distâncias e áreas
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='meters',
        primary_area_unit='sqkilometers',
        secondary_area_unit='hectares',
        active_color='red',
        completed_color='blue'
    ).add_to(m)
    
    # 5. LocateControl - Botão para encontrar localização do usuário
    plugins.LocateControl(
        position='topleft',
        strings={'title': 'Ver minha localização'},
        locateOptions={'enableHighAccuracy': True}
    ).add_to(m)

    # Borda do estado (camada base)
    fg_limites = folium.FeatureGroup(name='🗺️ Limite de SC', show=True)
    try:
        folium.GeoJson(sc_geom, style_function=lambda f: {
            'fillColor': 'transparent', 'color': '#111', 'weight': 3, 'dashArray': '6,4', 'fillOpacity': 0
        }).add_to(fg_limites)
    except Exception:
        pass
    fg_limites.add_to(m)

    # Criar FeatureGroup INDIVIDUAL para cada bacia (permite ligar/desligar separadamente)
    bacias_layers = {}
    
    for _, row in bacias_official.iterrows():
        bacia = row['bacia']
        cor = cores_bacias.get(bacia, '#999999')
        stats = resumo.loc[resumo['bacia'] == bacia].iloc[0] if (resumo['bacia'] == bacia).any() else None
        
        # Criar FeatureGroup específico para esta bacia
        fg_bacia = folium.FeatureGroup(name=f'🌊 {bacia}', show=True)
        
        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; min-width: 280px; max-width: 320px;">
            <h3 style="margin: 0 0 10px 0; padding-bottom: 6px; border-bottom: 3px solid {cor}; color: {cor}; font-size: 16px;">
                🌊 {bacia}
            </h3>
            {f'<div style="background: #e3f2fd; padding: 8px; margin: 6px 0; border-left: 4px solid #1976d2; border-radius: 3px;"><strong style="font-size: 12px;">👥 População Total:</strong><br><span style="font-size: 16px; font-weight: bold; color: #1976d2;">{stats.populacao:,.0f} habitantes</span></div>' if stats is not None else ''}
            {f'<div style="background: #e8f5e9; padding: 8px; margin: 6px 0; border-left: 4px solid #388e3c; border-radius: 3px;"><strong style="font-size: 12px;">🗑️ Resíduos Domésticos:</strong><br><span style="font-size: 16px; font-weight: bold; color: #388e3c;">{stats.domestico_t_ano:,.0f} t/ano</span></div>' if stats is not None else ''}
            {f'<div style="background: #fff3e0; padding: 8px; margin: 6px 0; border-left: 4px solid #f57c00; border-radius: 3px;"><strong style="font-size: 12px;">♻️ Resíduos Recicláveis:</strong><br><span style="font-size: 16px; font-weight: bold; color: #f57c00;">{stats.reciclavel_t_ano:,.0f} t/ano</span></div>' if stats is not None else ''}
        </div>
        """
        gj = folium.GeoJson(
            row['geometry'],
            style_function=lambda f, cor=cor: {'fillColor': cor, 'color': '#222222', 'weight': 2, 'fillOpacity': 0.6},
            tooltip=folium.Tooltip(bacia, sticky=False)
        )
        gj.add_to(fg_bacia)
        folium.Popup(popup_html, max_width=400).add_to(gj)
        
        # Adicionar ao mapa
        fg_bacia.add_to(m)
        bacias_layers[bacia] = fg_bacia

    # Legenda responsiva e SEMPRE VISÍVEL (ajustada para não sobrepor atribuição CartoDB)
    legend_html = '''
    <style>
        /* Esconder controles pesados no mobile */
        @media (max-width: 768px) {
            .leaflet-control-minimap { display: none !important; }
            .leaflet-control-measure { display: none !important; }
        }

        /* Ajustar atribuição do mapa base para evitar sobreposição */
        .leaflet-control-attribution {
            font-size: 10px !important;
            padding: 2px 5px !important;
            background: rgba(255, 255, 255, 0.8) !important;
            max-width: 200px !important;
        }
        
        .legend-bacias {
            position: fixed;
            bottom: 35px;
            right: 20px;
            z-index: 999 !important;
            background: white;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            border: 3px solid #1976d2;
            max-height: 80vh;
            overflow-y: auto;
            min-width: 280px;
            max-width: 350px;
        }
        
        @media (max-width: 768px) {
            .legend-bacias {
                bottom: 5px !important;
                right: 5px !important;
                left: 5px !important;
                padding: 10px !important;
                font-size: 10px !important;
                max-height: 40vh !important;
                min-width: auto !important;
                max-width: none !important;
                border-width: 2px !important;
            }
            .legend-bacias h4 {
                font-size: 12px !important;
                margin-bottom: 8px !important;
                padding-bottom: 5px !important;
                border-bottom-width: 2px !important;
            }
            .legend-bacias .bacia-item { 
                margin: 4px 0 !important; 
            }
            .legend-bacias .color-box { 
                width: 18px !important; 
                height: 14px !important;
                margin-right: 6px !important;
            }
            .legend-bacias .bacia-name { 
                font-size: 10px !important; 
                line-height: 1.2 !important;
            }
            /* Reduzir tamanho das seções extras em mobile */
            .legend-bacias .instrucoes-mobile {
                padding: 6px !important;
                font-size: 9px !important;
                margin-top: 8px !important;
            }
            .legend-bacias .fonte-mobile {
                font-size: 8px !important;
                margin-top: 8px !important;
                padding-top: 6px !important;
            }
        }
        
        @media print {
            .legend-bacias {
                display: block !important;
            }
        }
    </style>
    <div class="legend-bacias">
        <h4 style="margin: 0 0 15px 0; color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 8px; font-size: 16px; font-weight: bold;">
            🌊 Bacias Hidrográficas de SC
        </h4>
    '''
    for bacia, cor in cores_bacias.items():
        legend_html += f'''
        <div class="bacia-item" style="margin: 8px 0; display: flex; align-items: center;">
            <div class="color-box" style="width: 28px; height: 20px; background: {cor}; 
                 border: 2px solid #333; margin-right: 10px; border-radius: 4px; flex-shrink: 0; 
                 box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
            <span class="bacia-name" style="font-size: 13px; color: #333; font-weight: 500;">{bacia}</span>
        </div>
        '''
    legend_html += '''
        <div class="instrucoes-mobile" style="margin-top: 15px; padding: 10px; background: #e8f5e9; border-left: 4px solid #388e3c; 
                    border-radius: 5px; font-size: 11px;">
            <strong>💡 Como usar:</strong><br>
            • Clique nas bacias para ver dados<br>
            • Use os controles de camadas<br>
            • Zoom: + / - ou scroll
        </div>
        <div class="fonte-mobile" style="margin-top: 12px; padding-top: 10px; border-top: 2px solid #e0e0e0; font-size: 10px; 
                    color: #666; text-align: center;">
            <strong>Fonte:</strong> ANA - Ottobacias<br>
            8 macro-bacias hidrográficas
        </div>
    </div>
    '''

    # Meta viewport para mobile
    viewport_meta = '''
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    '''
    meta_inject_js = '''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var meta1 = document.createElement('meta');
        meta1.name = 'viewport';
        meta1.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
        document.head.appendChild(meta1);
        var meta2 = document.createElement('meta');
        meta2.name = 'mobile-web-app-capable';
        meta2.content = 'yes';
        document.head.appendChild(meta2);
        var meta3 = document.createElement('meta');
        meta3.name = 'apple-mobile-web-app-capable';
        meta3.content = 'yes';
        document.head.appendChild(meta3);
    });
    </script>
    '''
    m.get_root().html.add_child(folium.Element(meta_inject_js))
    
    # LayerControl (colapsado para melhorar no mobile)
    folium.LayerControl(collapsed=True, position='topleft').add_to(m)
    
    # ADICIONAR LEGENDA POR ÚLTIMO para garantir que fique visível
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(OUT_MAP)

if __name__ == '__main__':
    print('🔎 Preparando limites de SC...')
    sc_geom = load_sc_boundary()
    bbox = bbox_from_geom(sc_geom)
    
    # Tenta primeiro arquivo local em data/
    local_file = find_local_otto_file()
    if local_file:
        print(f"📁 Carregando Ottobacias locais: {os.path.basename(local_file)}")
        otto = load_local_ottobacias(local_file)
        if otto.crs is None:
            # Assume WGS84 caso sem CRS
            otto.set_crs(epsg=4326, inplace=True)
    else:
        print('🌐 Baixando Ottobacias da ANA (ArcGIS REST)...')
        geojson = fetch_ottobacias_geojson(bbox)
        otto = geojson_to_gdf(geojson)
    # Clip por SC
    print('✂️  Recortando por SC...')
    # Para performance, reprojeta o limite de SC para o CRS das ottobacias e CLIPA os dados no CRS nativo
    # Criar GeoDataFrame do limite de SC corretamente
    sc_gdf = gpd.GeoDataFrame({'id': [1], 'geometry': [sc_geom]}, crs='EPSG:4326')
    sc_in_otto = sc_gdf.to_crs(otto.crs or 'EPSG:4326')
    otto_sc = gpd.clip(otto, sc_in_otto)

    print('🗺️  Construindo referência das 8 bacias (municípios)...')
    bacias_ref = build_bacias_ref_from_municipios()

    print('🔗 Atribuindo cada Ottobacia à bacia por maior sobreposição...')
    otto_assigned = assign_ottobacia_to_bacia(otto_sc, bacias_ref)

    # Resumo ANA após atribuição
    counts = otto_assigned['bacia'].value_counts().sort_index()
    print('\n📋 Resumo (quantidade de ottobacias por macro-bacia):')
    for b, c in counts.items():
        print(f" - {b}: {c} unidades")

    print('🧩 Dissolvendo Ottobacias por bacia...')
    bacias_official = otto_assigned.dissolve(by='bacia', aggfunc='sum').reset_index()
    
    # Simplificação AGRESSIVA para reduzir peso do HTML drasticamente
    # Tolerância de 1000m (1km) - suficiente para visualização em escala estadual
    try:
        bo_3857 = bacias_official.to_crs(3857)
        bo_3857['geometry'] = bo_3857.geometry.simplify(1000, preserve_topology=True)  # 1km
        bacias_official = bo_3857.to_crs(4326)
        print(f'   ✓ Geometrias macro-bacias simplificadas (tolerância 1km)')
    except Exception:
        # Se algo falhar, ao menos garanta 4326 para o mapa
        bacias_official = bacias_official.to_crs(4326)
    
    # Simplificar MUITO as ottobacias individuais também
    try:
        otto_3857 = otto_assigned.to_crs(3857)
        otto_3857['geometry'] = otto_3857.geometry.simplify(500, preserve_topology=True)  # 500m
        otto_assigned = otto_3857.to_crs(4326)
        print(f'   ✓ Geometrias ottobacias simplificadas (tolerância 500m)')
    except Exception:
        otto_assigned = otto_assigned.to_crs(4326)

    print('📊 Lendo estatísticas por bacia...')
    resumo = pd.read_csv(RESUMO_CSV)

    # Exportar datasets
    out_macro = os.path.join(BASE_DIR, 'outputs', 'bacias_oficiais_ana_macro.gpkg')
    out_otto = os.path.join(BASE_DIR, 'outputs', 'ottobacias_sc_atribuida.gpkg')
    try:
        bacias_official.to_file(out_macro, driver='GPKG')
        otto_assigned.to_file(out_otto, driver='GPKG')
        print(f'📦 Exportados: {out_macro} e {out_otto}')
    except Exception as e:
        print(f'⚠️ Falha ao exportar GPKG: {e}')

    print('🖼️ Gerando mapa com camadas (macro e ottobacias)...')
    build_map_from_official(bacias_official, resumo, otto_assigned, sc_geom)

    print(f'✅ Mapa atualizado com bacias oficiais! Arquivo: {OUT_MAP}')

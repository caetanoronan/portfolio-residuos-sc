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

def build_map_from_official(bacias_official: gpd.GeoDataFrame, resumo: pd.DataFrame):
    # Cores consistentes
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
    center = [bacias_official.geometry.centroid.y.mean(), bacias_official.geometry.centroid.x.mean()]
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron', min_zoom=6, max_zoom=13, max_bounds=True)

    for _, row in bacias_official.iterrows():
        bacia = row['bacia']
        cor = cores_bacias.get(bacia, '#999999')
        stats = resumo.loc[resumo['bacia'] == bacia].iloc[0] if (resumo['bacia'] == bacia).any() else None
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
        folium.GeoJson(
            row['geometry'],
            style_function=lambda f, cor=cor: {'fillColor': cor, 'color': '#ffffff', 'weight': 4, 'fillOpacity': 0.6},
            tooltip=folium.Tooltip(bacia, sticky=False),
            popup=folium.Popup(popup_html, max_width=400)
        ).add_to(m)

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
            otto.set_crs(epsg=4326, inplace=True)
        else:
            otto = otto.to_crs(4326)
    else:
        print('🌐 Baixando Ottobacias da ANA (ArcGIS REST)...')
        geojson = fetch_ottobacias_geojson(bbox)
        otto = geojson_to_gdf(geojson)
    # Clip por SC
    print('✂️  Recortando por SC...')
    otto_sc = gpd.clip(otto, gpd.GeoDataFrame(geometry=[sc_geom], crs='EPSG:4326'))

    print('🗺️  Construindo referência das 8 bacias (municípios)...')
    bacias_ref = build_bacias_ref_from_municipios()

    print('🔗 Atribuindo cada Ottobacia à bacia por maior sobreposição...')
    otto_assigned = assign_ottobacia_to_bacia(otto_sc, bacias_ref)

    print('🧩 Dissolvendo Ottobacias por bacia...')
    bacias_official = otto_assigned.dissolve(by='bacia', aggfunc='sum').reset_index()

    print('📊 Lendo estatísticas por bacia...')
    resumo = pd.read_csv(RESUMO_CSV)

    print('🖼️ Gerando mapa com polígonos oficiais...')
    build_map_from_official(bacias_official, resumo)

    print(f'✅ Mapa atualizado com bacias oficiais! Arquivo: {OUT_MAP}')

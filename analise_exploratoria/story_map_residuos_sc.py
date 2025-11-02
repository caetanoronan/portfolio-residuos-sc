import os
import sys
import warnings
import folium
from folium.plugins import Fullscreen, MiniMap
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

"""
Story Map: Resíduos Sólidos – Santa Catarina (SC)

Pipeline:
1) Carrega setores censitários (SC_setores_CD2022.gpkg)
2) Obtém população por município (API IBGE -> fallback: estimativa via setores)
3) Calcula resíduos (0.95 kg/hab/dia)
4) Dissolve setores -> municípios (polígonos simplificados)
5) Classifica porte municipal (pequeno, médio, grande)
6) Gera mapa interativo acessível (Folium) em outputs/mapa_historia_residuos_sc.html

Obs:
- Não altera o arquivo-fonte dos setores
- Cores e legendas colorblind-safe
- Operações geométricas em CRS projetado; exporta em EPSG:4326
"""

SRC_SETORS = r"analise_exploratoria/SC_setores_CD2022.gpkg"
OUT_HTML = r"outputs/mapa_historia_residuos_sc.html"
# Modo rápido: gera apenas marcadores por município (sem dissolve/choropleth)
# Para gerar o mapa completo (com polígonos/choropleth), mantenha como False
FAST_MODE = False

# Parâmetros de taxa
TAXA_KG_HAB_DIA = 0.95

# Limiares de porte (assumidos; ajuste se necessário)
LIM_PEQUENO = 50000
LIM_MEDIO = 200000

# Paletas
COR_PEQUENO = "#a6d854"  # verde
COR_MEDIO   = "#fc8d62"  # laranja
COR_GRANDE  = "#8da0cb"  # roxo

GRADIENTE_DOMESTICO = {0.0: "#d0d1e6", 0.5: "#74a9cf", 1.0: "#034e7b"}


def fetch_pop_ibge():
    """Tenta obter população 2022 por município (código IBGE 7 dígitos)."""
    try:
        url = "https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93?localidades=N6[all]"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        rows = []
        for item in data[0]['resultados']:
            for loc in item['series']:
                codigo = str(loc['localidade']['id']).zfill(7)
                valor = list(loc['serie'].values())[0] if loc['serie'] else None
                if valor is not None:
                    rows.append({"CD_MUN_str": codigo, "populacao": float(valor)})
        df = pd.DataFrame(rows)
        if len(df) == 0:
            return None
        return df
    except Exception as e:
        warnings.warn(f"Falha IBGE API: {e}")
        return None


def guess_pop_from_setors(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Inferir população a partir dos setores, tentando nomes comuns de coluna."""
    candidatos = [
        'POP', 'pop', 'POP2022', 'V002', 'V001', 'PESSOAS', 'P001']
    cols = {c.lower(): c for c in gdf.columns}
    pop_col = None
    for cand in candidatos:
        if cand.lower() in cols:
            pop_col = cols[cand.lower()]
            break
    if pop_col is None:
        warnings.warn("Não encontrei coluna de população nos setores; retornando vazio.")
        return pd.DataFrame(columns=["CD_MUN_str", "populacao"])  
    tmp = gdf[["CD_MUN", pop_col]].copy()
    tmp['CD_MUN_str'] = tmp['CD_MUN'].astype(str).str.zfill(7)
    pop_df = tmp.groupby('CD_MUN_str')[pop_col].sum().reset_index()
    pop_df = pop_df.rename(columns={pop_col: 'populacao'})
    return pop_df


def classificar_porte(pop):
    if pop is None or pd.isna(pop):
        return 'Desconhecido'
    if pop < LIM_PEQUENO:
        return 'Pequeno Porte'
    if pop < LIM_MEDIO:
        return 'Médio Porte'
    return 'Grande Porte'


def cor_por_porte(porte):
    return {
        'Pequeno Porte': COR_PEQUENO,
        'Médio Porte': COR_MEDIO,
        'Grande Porte': COR_GRANDE,
    }.get(porte, '#b3b3b3')


def fmt_num(x, decimals=0, suffix=""):
    try:
        if x is None or pd.isna(x):
            return "—"
        if decimals == 0:
            return f"{float(x):,.0f}{(' ' + suffix) if suffix else ''}"
        return f"{float(x):,.{decimals}f}{(' ' + suffix) if suffix else ''}"
    except Exception:
        return "—"


def main():
    os.makedirs('outputs', exist_ok=True)

    print("1) Lendo setores censitários...")
    gdf = gpd.read_file(SRC_SETORS)
    if gdf.crs is None:
        warnings.warn("CRS dos setores indefinido; assumindo EPSG:31982 (SIRGAS 2000 / UTM 22S)")
        gdf = gdf.set_crs(31982)

    print("2) Obtendo população por município (IBGE → fallback: setores)...")
    pop_df = fetch_pop_ibge()
    if pop_df is None or len(pop_df) == 0:
        pop_df = guess_pop_from_setors(gdf)

    # Dissolver setores → municípios (geometria)
    print("3) Preparando dados municipais...")
    gdf['CD_MUN_str'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    name_cols = [c for c in ['NM_MUN', 'NM_MUNICIP', 'MUNICIPIO'] if c in gdf.columns]
    nm_col = name_cols[0] if name_cols else None

    # Agregados por município (sem geometria por enquanto)
    muni_stats = gdf[['CD_MUN_str']].drop_duplicates().copy()
    if nm_col:
        name_map = gdf.groupby('CD_MUN_str')[nm_col].first().rename('NM_MUN').reset_index()
        muni_stats = muni_stats.merge(name_map, on='CD_MUN_str', how='left')
    else:
        muni_stats['NM_MUN'] = muni_stats['CD_MUN_str']

    muni_stats = muni_stats.merge(pop_df, on='CD_MUN_str', how='left')
    muni_stats['domestico_t_ano'] = (muni_stats['populacao'].fillna(0) * TAXA_KG_HAB_DIA * 365) / 1000.0
    muni_stats['reciclavel_t_ano'] = muni_stats['domestico_t_ano'] * 0.10
    muni_stats['porte'] = muni_stats['populacao'].apply(classificar_porte)

    if FAST_MODE:
        print("   ▶ FAST_MODE ativo: gerando pontos representativos por município...")
        # Coordenadas representativas: média dos centróides dos setores por município
        gdf4326 = gdf.to_crs(4326)
        cent = gdf4326.geometry.centroid
        coords = pd.DataFrame({'CD_MUN_str': gdf4326['CD_MUN_str'], 'lat': cent.y.values, 'lon': cent.x.values})
        muni_xy = coords.groupby('CD_MUN_str').mean().reset_index()
        muni = muni_stats.merge(muni_xy, on='CD_MUN_str', how='left')
    else:
        print("   ▶ Modo completo: criando geometrias municipais (dissolve)...")
        muni = gdf.dissolve(by='CD_MUN_str', aggfunc='first').reset_index()
        if nm_col:
            name_map = gdf.groupby('CD_MUN_str')[nm_col].first()
            muni = muni.merge(name_map, left_on='CD_MUN_str', right_index=True, how='left')
            muni = muni.rename(columns={nm_col: 'NM_MUN'})
        else:
            muni['NM_MUN'] = muni['CD_MUN_str']
        muni = muni.merge(muni_stats[['CD_MUN_str','populacao','domestico_t_ano','reciclavel_t_ano','porte']], on='CD_MUN_str', how='left')

    # Simplificação geométrica
    if not FAST_MODE:
        print("4) Simplificando geometrias para web (100 m)...")
        try:
            muni_3857 = muni.to_crs(3857)
            muni_3857['geometry'] = muni_3857.geometry.simplify(100, preserve_topology=True)
            muni = muni_3857.to_crs(4326)
        except KeyboardInterrupt:
            print("   ⚠️ Simplificação interrompida. Prosseguindo sem simplificar.")
            muni = muni.to_crs(4326)
        except Exception as e:
            print(f"   ⚠️ Falha na simplificação ({e}). Prosseguindo sem simplificar.")
            muni = muni.to_crs(4326)

    # Centro do mapa
    # Centro do mapa (seguro e rápido): centro do bounding box
    if FAST_MODE:
        # Centro por bounds aproximado usando coordenadas dos pontos
        minx, miny = muni['lon'].min(), muni['lat'].min()
        maxx, maxy = muni['lon'].max(), muni['lat'].max()
        center = [(miny + maxy) / 2, (minx + maxx) / 2]
    else:
        minx, miny, maxx, maxy = muni.total_bounds
        center = [(miny + maxy) / 2, (minx + maxx) / 2]

    print("5) Construindo mapa Folium...")
    m = folium.Map(location=center, zoom_start=7, tiles='CartoDB positron', min_zoom=6, max_zoom=13)

    # Camada: Limite estadual de SC (contorno externo de todos os municípios)
    if not FAST_MODE:
        print("   ▶ Criando limite estadual...")
        try:
            # Dissolver todos os municípios em uma única geometria (contorno do estado)
            limite_sc = muni.dissolve().geometry.iloc[0]
            
            # Adicionar como camada de contorno sutil (linha preta fina translúcida)
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

    # Camadas por porte: GeoJSON com polígonos municipais
    fg_small = folium.FeatureGroup(name='Pequeno Porte', show=True)
    fg_medium = folium.FeatureGroup(name='Médio Porte', show=True)
    fg_large = folium.FeatureGroup(name='Grande Porte', show=True)

    # Função de estilo para cada porte
    def style_function_small(feature):
        return {
            'fillColor': COR_PEQUENO,
            'color': '#333',
            'weight': 1,
            'fillOpacity': 0.7
        }
    
    def style_function_medium(feature):
        return {
            'fillColor': COR_MEDIO,
            'color': '#333',
            'weight': 1,
            'fillOpacity': 0.7
        }
    
    def style_function_large(feature):
        return {
            'fillColor': COR_GRANDE,
            'color': '#333',
            'weight': 1,
            'fillOpacity': 0.7
        }

    # Função para criar popup com dados municipais
    def create_popup_html(properties):
        return f"""
        <div style='font-family: Arial; font-size: 13px; min-width: 240px;'>
            <h4 style='margin: 0 0 8px 0; color: {cor_por_porte(properties.get('porte'))};'>{properties.get('NM_MUN')}</h4>
            <div style='background:#e3f2fd;padding:6px;margin:4px 0;border-left:4px solid #1976d2;'>
                <b>População:</b> {fmt_num(properties.get('populacao'))}
            </div>
            <div style='background:#e8f5e9;padding:6px;margin:4px 0;border-left:4px solid #388e3c;'>
                <b>Doméstico:</b> {fmt_num(properties.get('domestico_t_ano'))} t/ano
            </div>
            <div style='background:#fff8e1;padding:6px;margin:4px 0;border-left:4px solid #fb8c00;'>
                <b>Reciclável (10%):</b> {fmt_num(properties.get('reciclavel_t_ano'))} t/ano
            </div>
            <div style='margin-top:6px;color:#555;'>Porte: <b>{properties.get('porte')}</b></div>
        </div>
        """

    # Separar municípios por porte
    muni_small = muni[muni['porte'] == 'Pequeno Porte'].copy()
    muni_medium = muni[muni['porte'] == 'Médio Porte'].copy()
    muni_large = muni[muni['porte'] == 'Grande Porte'].copy()

    # Detectar nome correto do campo município (pode variar após dissolve)
    nm_mun_field = 'NM_MUN' if 'NM_MUN' in muni.columns else ('NM_MUN_y' if 'NM_MUN_y' in muni.columns else 'NM_MUN_x')
    
    # Adicionar GeoJSON para cada porte
    if not FAST_MODE:
        if len(muni_small) > 0:
            folium.GeoJson(
                muni_small,
                style_function=style_function_small,
                popup=folium.GeoJsonPopup(fields=[nm_mun_field, 'populacao', 'domestico_t_ano', 'reciclavel_t_ano', 'porte'],
                                          aliases=['Município', 'População', 'Doméstico (t/ano)', 'Reciclável (t/ano)', 'Porte'],
                                          labels=True)
            ).add_to(fg_small)
        
        if len(muni_medium) > 0:
            folium.GeoJson(
                muni_medium,
                style_function=style_function_medium,
                popup=folium.GeoJsonPopup(fields=[nm_mun_field, 'populacao', 'domestico_t_ano', 'reciclavel_t_ano', 'porte'],
                                          aliases=['Município', 'População', 'Doméstico (t/ano)', 'Reciclável (t/ano)', 'Porte'],
                                          labels=True)
            ).add_to(fg_medium)
        
        if len(muni_large) > 0:
            folium.GeoJson(
                muni_large,
                style_function=style_function_large,
                popup=folium.GeoJsonPopup(fields=[nm_mun_field, 'populacao', 'domestico_t_ano', 'reciclavel_t_ano', 'porte'],
                                          aliases=['Município', 'População', 'Doméstico (t/ano)', 'Reciclável (t/ano)', 'Porte'],
                                          labels=True)
            ).add_to(fg_large)
    
    print(f"   ✔ Camadas criadas - Pequeno: {len(muni_small)}, Médio: {len(muni_medium)}, Grande: {len(muni_large)}")

    fg_small.add_to(m)
    fg_medium.add_to(m)
    fg_large.add_to(m)

    # Controles e acessibilidade
    folium.LayerControl(collapsed=True, position='topleft').add_to(m)
    Fullscreen(position='topright').add_to(m)
    MiniMap(toggle_display=True, position='bottomright').add_to(m)

    # Legenda custom
    legend_html = f"""
    <div class='legend-bacias' style="position: fixed; bottom: 18px; left: 18px; z-index: 9999; background: #fff; padding: 10px 12px; border-radius: 10px; box-shadow: 0 2px 8px #0002; border: 2px solid #1976d2; font-family: Arial; font-size: 13px;">
      <div style='font-weight:700; margin-bottom:6px; color:#1976d2;'>Legenda – Porte e Resíduos</div>
      <div style='margin:4px 0;'><span style='display:inline-block;width:12px;height:12px;background:{COR_PEQUENO};border-radius:50%;margin-right:6px;'></span>Pequeno Porte (&lt; {LIM_PEQUENO:,} hab)</div>
      <div style='margin:4px 0;'><span style='display:inline-block;width:12px;height:12px;background:{COR_MEDIO};border-radius:50%;margin-right:6px;'></span>Médio Porte ({LIM_PEQUENO:,}–{LIM_MEDIO:,} hab)</div>
      <div style='margin:4px 0;'><span style='display:inline-block;width:12px;height:12px;background:{COR_GRANDE};border-radius:50%;margin-right:6px;'></span>Grande Porte (&ge; {LIM_MEDIO:,} hab)</div>
      <hr style='margin:8px 0;border:none;border-top:1px solid #ddd;'>
      <div>Choropleth: azul claro → escuro = menor → maior dom. (t/ano)</div>
    </div>
    """
    # Inserção correta na raiz HTML
    m.get_root().html.add_child(folium.Element(legend_html))

    # CSS mobile: esconder minimapa em telas pequenas
    mobile_css = """
    <style>@media (max-width: 768px){ .leaflet-control-minimap{ display:none; } }</style>
    """
    m.get_root().html.add_child(folium.Element(mobile_css))

    # Salvar
    m.save(OUT_HTML)
    print(f"✔ Mapa salvo em {OUT_HTML}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Erro ao gerar mapa:", e)
        sys.exit(1)

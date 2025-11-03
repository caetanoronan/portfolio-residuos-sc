"""
Conexão com GeoPackage e Operações de Banco de Dados
Carrega dados do SC_setores_CD2022.gpkg usando GeoPandas
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from functools import lru_cache
import warnings
warnings.filterwarnings('ignore')

# Forçar engine pyogrio quando disponível (evita dependência do GDAL/Fiona no deploy)
try:
    # GeoPandas 0.14+ possui opção global para engine de IO
    gpd.options.io_engine = "pyogrio"  # type: ignore[attr-defined]
except Exception:
    pass

from api.config import GPKG_PATH, TAXA_PER_CAPITA_KG_DIA, DIAS_POR_ANO, DATA_DIR


class DatabaseManager:
    """Gerenciador de conexão com GeoPackage"""
    
    def __init__(self):
        self.gpkg_path = GPKG_PATH
        self._gdf = None
        
    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """
        Carrega GeoDataFrame na primeira chamada (lazy loading)
        Mantém em cache para requisições subsequentes
        """
        if self._gdf is None:
            print(f"Carregando GeoPackage: {self.gpkg_path}")
            # Usar engine pyogrio para evitar GDAL/Fiona
            self._gdf = gpd.read_file(self.gpkg_path, engine="pyogrio")
            print(f"Carregado: {len(self._gdf)} setores censitários")
        return self._gdf
    
    def calcular_residuos(self, populacao: int) -> Dict[str, float]:
        """
        Calcula estimativa de resíduos baseado na população
        
        Args:
            populacao: População residente
            
        Returns:
            Dict com residuos_kg_dia e residuos_ton_ano
        """
        residuos_kg_dia = populacao * TAXA_PER_CAPITA_KG_DIA
        residuos_ton_ano = (residuos_kg_dia * DIAS_POR_ANO) / 1000
        
        return {
            "populacao": populacao,
            "taxa_per_capita_kg_dia": TAXA_PER_CAPITA_KG_DIA,
            "residuos_kg_dia": round(residuos_kg_dia, 2),
            "residuos_ton_ano": round(residuos_ton_ano, 2)
        }
    
    def get_municipios(self) -> List[Dict]:
        """
        Retorna lista de todos os municípios únicos
        
        Returns:
            Lista de dicts com codigo_ibge, nome, sigla_uf
        """
        gdf = self.gdf
        
        # Agrupar por município
        municipios = gdf.groupby(['CD_MUN', 'NM_MUN']).size().reset_index(name='setores')
        
        result = []
        for _, row in municipios.iterrows():
            result.append({
                "codigo_ibge": str(row['CD_MUN']),
                "nome": row['NM_MUN'],
                "sigla_uf": "SC"
            })
        
        return sorted(result, key=lambda x: x['nome'])
    
    def get_municipio_detalhes(self, codigo_ibge: str) -> Optional[Dict]:
        """
        Retorna detalhes de um município específico
        
        Args:
            codigo_ibge: Código IBGE de 7 dígitos
            
        Returns:
            Dict com informações do município ou None se não encontrado
        """
        gdf = self.gdf
        
        # Filtrar setores do município
        mun_setores = gdf[gdf['CD_MUN'] == codigo_ibge]
        
        if len(mun_setores) == 0:
            return None
        
        # Dados básicos
        nome = mun_setores.iloc[0]['NM_MUN']
        
        # População total (soma de todos os setores)
        # Tentar colunas possíveis de população
        pop_columns = ['POP', 'POPULACAO', 'V001', 'V002']
        populacao = 0
        
        for col in pop_columns:
            if col in mun_setores.columns:
                populacao = int(mun_setores[col].sum())
                break
        
        # Dissolver geometrias para obter contorno do município
        mun_geom = mun_setores.dissolve().geometry.iloc[0]
        
        # Centróide
        centroide = mun_geom.centroid
        
        # Bounding box
        bounds = mun_geom.bounds
        
        # Área (converter para km²)
        # Se CRS for métrico (EPSG:31982), calcular área
        if gdf.crs.to_epsg() == 31982:
            area_km2 = mun_geom.area / 1_000_000  # m² para km²
        else:
            # Reprojetar temporariamente para calcular área
            temp_geom = gpd.GeoSeries([mun_geom], crs=gdf.crs).to_crs(31982)
            area_km2 = temp_geom.area.iloc[0] / 1_000_000
        
        return {
            "codigo_ibge": codigo_ibge,
            "nome": nome,
            "sigla_uf": "SC",
            "area_km2": round(area_km2, 2),
            "setores_censitarios": len(mun_setores),
            "centroide": {
                "latitude": round(centroide.y, 6),
                "longitude": round(centroide.x, 6)
            },
            "bounding_box": {
                "min_lat": round(bounds[1], 6),
                "max_lat": round(bounds[3], 6),
                "min_lon": round(bounds[0], 6),
                "max_lon": round(bounds[2], 6)
            }
        }
    
    def get_municipio_populacao(self, codigo_ibge: str) -> int:
        """
        Retorna população total de um município
        
        Args:
            codigo_ibge: Código IBGE de 7 dígitos
            
        Returns:
            População total ou 0 se não encontrado
        """
        gdf = self.gdf
        mun_setores = gdf[gdf['CD_MUN'] == codigo_ibge]
        
        if len(mun_setores) == 0:
            return 0
        
        # Tentar colunas possíveis de população
        pop_columns = ['POP', 'POPULACAO', 'V001', 'V002']
        
        for col in pop_columns:
            if col in mun_setores.columns:
                return int(mun_setores[col].sum())
        
        return 0


# Instância global (singleton)
db = DatabaseManager()


# Funções auxiliares (wrappers com cache)
@lru_cache(maxsize=128)
def get_municipios_list() -> tuple:
    """Wrapper para obter lista de municípios (com cache)"""
    result = db.get_municipios()
    # Converter para tuple para ser hashable (lru_cache requer)
    return tuple(tuple(sorted(m.items())) for m in result)


@lru_cache(maxsize=512)
def get_municipio_info(codigo_ibge: str) -> Optional[Dict]:
    """Wrapper para obter informações de município (com cache)"""
    return db.get_municipio_detalhes(codigo_ibge)


@lru_cache(maxsize=512)
def calcular_residuos_municipio(codigo_ibge: str) -> Optional[Dict]:
    """
    Calcula resíduos de um município
    
    Returns:
        Dict com detalhes do município + estimativa de resíduos
    """
    detalhes = db.get_municipio_detalhes(codigo_ibge)
    if not detalhes:
        return None
    
    populacao = db.get_municipio_populacao(codigo_ibge)
    residuos = db.calcular_residuos(populacao)
    
    return {
        **detalhes,
        "residuos": residuos
    }


# ========== BACIAS HIDROGRÁFICAS ==========

class BaciasManager:
    """Gerenciador de bacias hidrográficas"""
    
    def __init__(self):
        self.bacias_path = DATA_DIR / "outputs" / "bacias_oficiais_ana_macro.gpkg"
        self._bacias_gdf = None
        
    @property
    def bacias_gdf(self) -> Optional[gpd.GeoDataFrame]:
        """Carrega GeoDataFrame de bacias (lazy loading)"""
        if self._bacias_gdf is None and self.bacias_path.exists():
            print(f"Carregando bacias: {self.bacias_path}")
            # Usar engine pyogrio para evitar GDAL/Fiona
            self._bacias_gdf = gpd.read_file(self.bacias_path, engine="pyogrio")
            print(f"Carregado: {len(self._bacias_gdf)} bacias")
        return self._bacias_gdf
    
    def get_bacias_list(self) -> List[Dict]:
        """Retorna lista de todas as bacias"""
        gdf = self.bacias_gdf
        if gdf is None:
            return []
        
        result = []
        for idx, row in gdf.iterrows():
            result.append({
                "id": int(idx) + 1,
                "nome": row.get('nome_bacia', row.get('NOME', f"Bacia {idx+1}")),
                "tipo": "macro"
            })
        
        return result
    
    def get_bacia_detalhes(self, bacia_id: int) -> Optional[Dict]:
        """Retorna detalhes de uma bacia específica"""
        gdf = self.bacias_gdf
        if gdf is None or bacia_id < 1 or bacia_id > len(gdf):
            return None
        
        row = gdf.iloc[bacia_id - 1]
        geom = row.geometry
        
        # Centróide
        centroide = geom.centroid
        
        # Área
        if gdf.crs.to_epsg() == 31982:
            area_km2 = geom.area / 1_000_000
        else:
            temp_geom = gpd.GeoSeries([geom], crs=gdf.crs).to_crs(31982)
            area_km2 = temp_geom.area.iloc[0] / 1_000_000
        
        return {
            "id": bacia_id,
            "nome": row.get('nome_bacia', row.get('NOME', f"Bacia {bacia_id}")),
            "tipo": "macro",
            "area_km2": round(area_km2, 2),
            "centroide": {
                "latitude": round(centroide.y, 6),
                "longitude": round(centroide.x, 6)
            }
        }
    
    def get_bacia_populacao(self, bacia_id: int) -> int:
        """
        Calcula população total da bacia através de spatial join
        com setores censitários
        """
        gdf_bacias = self.bacias_gdf
        gdf_setores = db.gdf
        
        if gdf_bacias is None or bacia_id < 1 or bacia_id > len(gdf_bacias):
            return 0
        
        # Geometria da bacia
        bacia_geom = gdf_bacias.iloc[bacia_id - 1].geometry
        
        # Reprojetar se necessário
        if gdf_setores.crs != gdf_bacias.crs:
            gdf_setores = gdf_setores.to_crs(gdf_bacias.crs)
        
        # Filtrar setores que intersectam a bacia
        setores_na_bacia = gdf_setores[gdf_setores.geometry.intersects(bacia_geom)]
        
        # Somar população
        pop_columns = ['POP', 'POPULACAO', 'V001', 'V002']
        for col in pop_columns:
            if col in setores_na_bacia.columns:
                return int(setores_na_bacia[col].sum())
        
        return 0


# Instância global
bacias_db = BaciasManager()


def get_bacias_list() -> List[Dict]:
    """Wrapper para obter lista de bacias"""
    return bacias_db.get_bacias_list()


def get_bacia_info(bacia_id: int) -> Optional[Dict]:
    """Wrapper para obter informações de bacia"""
    return bacias_db.get_bacia_detalhes(bacia_id)


def calcular_residuos_bacia(bacia_id: int) -> Optional[Dict]:
    """
    Calcula resíduos de uma bacia
    
    Returns:
        Dict com detalhes da bacia + estimativa de resíduos
    """
    detalhes = bacias_db.get_bacia_detalhes(bacia_id)
    if not detalhes:
        return None
    
    populacao = bacias_db.get_bacia_populacao(bacia_id)
    residuos = db.calcular_residuos(populacao)
    
    return {
        **detalhes,
        "residuos": residuos
    }

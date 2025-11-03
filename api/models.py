"""
Modelos de Dados (Pydantic Schemas)
Define a estrutura das respostas JSON da API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== MODELOS BASE ==========

class Coordenadas(BaseModel):
    """Coordenadas geográficas (lat/lon)"""
    latitude: float = Field(..., description="Latitude em graus decimais (WGS84)")
    longitude: float = Field(..., description="Longitude em graus decimais (WGS84)")


class BoundingBox(BaseModel):
    """Bounding box (retângulo envolvente)"""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


# ========== RESÍDUOS ==========

class ResiduosEstimativa(BaseModel):
    """Estimativa de resíduos sólidos"""
    populacao: int = Field(..., description="População residente (Censo 2022)")
    taxa_per_capita_kg_dia: float = Field(0.95, description="Taxa de geração per capita (kg/hab/dia)")
    residuos_kg_dia: float = Field(..., description="Total de resíduos em kg/dia")
    residuos_ton_ano: float = Field(..., description="Total de resíduos em toneladas/ano")
    
    class Config:
        json_schema_extra = {
            "example": {
                "populacao": 537211,
                "taxa_per_capita_kg_dia": 0.95,
                "residuos_kg_dia": 510350.45,
                "residuos_ton_ano": 186277.91
            }
        }


# ========== MUNICÍPIO ==========

class MunicipioBase(BaseModel):
    """Informações básicas de município"""
    codigo_ibge: str = Field(..., description="Código IBGE de 7 dígitos")
    nome: str = Field(..., description="Nome do município")
    sigla_uf: str = Field("SC", description="Sigla do estado")


class MunicipioDetalhado(MunicipioBase):
    """Município com informações completas"""
    regiao_geografica_imediata: Optional[str] = Field(None, description="RGI - Região Geográfica Imediata")
    area_km2: Optional[float] = Field(None, description="Área territorial em km²")
    centroide: Optional[Coordenadas] = Field(None, description="Coordenadas do centróide")
    bounding_box: Optional[BoundingBox] = Field(None, description="Retângulo envolvente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo_ibge": "4205407",
                "nome": "Florianópolis",
                "sigla_uf": "SC",
                "regiao_geografica_imediata": "Florianópolis",
                "area_km2": 675.409,
                "centroide": {
                    "latitude": -27.5954,
                    "longitude": -48.5480
                }
            }
        }


class MunicipioComResiduos(MunicipioDetalhado):
    """Município com estimativas de resíduos"""
    residuos: ResiduosEstimativa


# ========== BACIA HIDROGRÁFICA ==========

class BaciaBase(BaseModel):
    """Informações básicas de bacia hidrográfica"""
    id: int = Field(..., description="ID único da bacia")
    nome: str = Field(..., description="Nome da bacia hidrográfica")
    tipo: str = Field(..., description="Tipo: 'macro' ou 'otto' (Ottobacia)")


class BaciaDetalhada(BaciaBase):
    """Bacia com informações completas"""
    codigo_otto: Optional[str] = Field(None, description="Código Ottobacia (se aplicável)")
    nivel: Optional[int] = Field(None, description="Nível da Ottobacia (1-6)")
    macro_bacia: Optional[str] = Field(None, description="Macro-bacia à qual pertence")
    area_km2: Optional[float] = Field(None, description="Área da bacia em km²")
    municipios: Optional[int] = Field(None, description="Número de municípios na bacia")
    centroide: Optional[Coordenadas] = Field(None, description="Coordenadas do centróide")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Bacia do Itajaí",
                "tipo": "macro",
                "area_km2": 15000.5,
                "municipios": 47,
                "centroide": {
                    "latitude": -27.15,
                    "longitude": -49.45
                }
            }
        }


class BaciaComResiduos(BaciaDetalhada):
    """Bacia com estimativas de resíduos"""
    residuos: ResiduosEstimativa


# ========== SETOR CENSITÁRIO ==========

class SetorCensitarioBase(BaseModel):
    """Informações básicas de setor censitário"""
    codigo_setor: str = Field(..., description="Código do setor censitário (Censo 2022)")
    codigo_municipio: str = Field(..., description="Código IBGE do município")
    situacao: str = Field(..., description="1=Urbano, 2=Rural, etc.")


class SetorCensitarioDetalhado(SetorCensitarioBase):
    """Setor com informações completas"""
    populacao: int = Field(..., description="População residente no setor")
    domicilios: Optional[int] = Field(None, description="Número de domicílios")
    area_km2: Optional[float] = Field(None, description="Área do setor em km²")
    centroide: Optional[Coordenadas] = Field(None, description="Coordenadas do centróide")


class SetorComResiduos(SetorCensitarioDetalhado):
    """Setor com estimativas de resíduos"""
    residuos: ResiduosEstimativa


# ========== RESPOSTAS DE LISTA ==========

class ListaMunicipios(BaseModel):
    """Resposta com lista de municípios"""
    total: int = Field(..., description="Número total de municípios")
    municipios: List[MunicipioBase] = Field(..., description="Lista de municípios")


class ListaBacias(BaseModel):
    """Resposta com lista de bacias"""
    total: int = Field(..., description="Número total de bacias")
    bacias: List[BaciaBase] = Field(..., description="Lista de bacias")


class ListaSetores(BaseModel):
    """Resposta com lista de setores"""
    total: int = Field(..., description="Número total de setores")
    setores: List[SetorCensitarioBase] = Field(..., description="Lista de setores")


# ========== ESTATÍSTICAS GERAIS ==========

class EstatisticasGerais(BaseModel):
    """Estatísticas consolidadas de Santa Catarina"""
    estado: str = "Santa Catarina"
    sigla: str = "SC"
    populacao: int
    municipios: int
    setores_censitarios: int
    residuos_totais_ton_ano: float
    residuos_per_capita_kg_dia: float
    macro_bacias: int
    ottobacias_nivel_5: int


# ========== MENSAGENS DE ERRO ==========

class ErrorResponse(BaseModel):
    """Resposta padrão de erro"""
    error: str = Field(..., description="Tipo de erro")
    message: str = Field(..., description="Mensagem descritiva")
    detail: Optional[str] = Field(None, description="Detalhes adicionais")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "NotFound",
                "message": "Município não encontrado",
                "detail": "Código IBGE 9999999 não existe na base de dados"
            }
        }

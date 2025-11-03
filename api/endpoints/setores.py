"""
Endpoints de Setores Censitários
GET /api/v1/setores - Lista setores (com filtros)
GET /api/v1/setores/{codigo} - Detalhes de um setor
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.models import (
    ListaSetores,
    SetorCensitarioBase,
    SetorCensitarioDetalhado,
    SetorComResiduos,
    ErrorResponse
)
from api.database import db

router = APIRouter()


@router.get(
    "/setores",
    response_model=ListaSetores,
    summary="Listar setores censitários",
    description="Retorna lista de setores censitários (requer filtro por município)"
)
async def listar_setores(
    municipio: Optional[str] = Query(None, description="Código IBGE do município (7 dígitos)"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Limitar número de resultados")
):
    """
    **Lista setores censitários de Santa Catarina**
    
    ⚠️ **Importante**: Devido ao volume de dados (16.831 setores), é **obrigatório** filtrar por município.
    
    - **municipio**: Código IBGE de 7 dígitos (ex: 4205407 para Florianópolis)
    - **limit**: Limitar resultados (padrão: 100, máximo: 1000)
    
    **Exemplo de uso:**
    ```
    GET /api/v1/setores?municipio=4205407&limit=50
    ```
    """
    if not municipio:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "BadRequest",
                "message": "Parâmetro 'municipio' é obrigatório",
                "detail": "Forneça o código IBGE do município (7 dígitos)"
            }
        )
    
    # Filtrar setores do município
    gdf = db.gdf
    setores_mun = gdf[gdf['CD_MUN'] == municipio]
    
    if len(setores_mun) == 0:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Nenhum setor encontrado para o município {municipio}",
                "detail": "Verifique se o código IBGE está correto"
            }
        )
    
    # Aplicar limite
    setores_mun = setores_mun.head(limit)
    
    # Montar resposta
    result = []
    for _, row in setores_mun.iterrows():
        result.append({
            "codigo_setor": str(row['CD_SETOR']),
            "codigo_municipio": str(row['CD_MUN']),
            "situacao": str(row.get('CD_SITUACAO', '1'))
        })
    
    return {
        "total": len(result),
        "setores": result
    }


@router.get(
    "/setores/{codigo_setor}",
    response_model=SetorComResiduos,
    responses={404: {"model": ErrorResponse}},
    summary="Detalhes de um setor censitário",
    description="Retorna informações detalhadas de um setor específico"
)
async def obter_setor(codigo_setor: str):
    """
    **Obtém detalhes de um setor censitário específico**
    
    - **codigo_setor**: Código do setor censitário (Censo 2022)
    
    Retorna:
    - Código do setor e município
    - População residente
    - Situação (1=Urbano, 2=Rural, etc.)
    - Coordenadas do centróide
    - Estimativa de resíduos
    
    **Exemplo de uso:**
    ```
    GET /api/v1/setores/420540705000001
    ```
    """
    gdf = db.gdf
    
    # Buscar setor
    setor = gdf[gdf['CD_SETOR'] == codigo_setor]
    
    if len(setor) == 0:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Setor {codigo_setor} não encontrado",
                "detail": "Verifique se o código do setor está correto"
            }
        )
    
    row = setor.iloc[0]
    
    # População
    pop_columns = ['POP', 'POPULACAO', 'V001', 'V002']
    populacao = 0
    for col in pop_columns:
        if col in row.index:
            populacao = int(row[col])
            break
    
    # Centróide
    geom = row.geometry
    centroide = geom.centroid
    
    # Área
    if gdf.crs.to_epsg() == 31982:
        area_km2 = geom.area / 1_000_000
    else:
        import geopandas as gpd
        temp_geom = gpd.GeoSeries([geom], crs=gdf.crs).to_crs(31982)
        area_km2 = temp_geom.area.iloc[0] / 1_000_000
    
    # Calcular resíduos
    residuos = db.calcular_residuos(populacao)
    
    return {
        "codigo_setor": codigo_setor,
        "codigo_municipio": str(row['CD_MUN']),
        "situacao": str(row.get('CD_SITUACAO', '1')),
        "populacao": populacao,
        "area_km2": round(area_km2, 6),
        "centroide": {
            "latitude": round(centroide.y, 6),
            "longitude": round(centroide.x, 6)
        },
        "residuos": residuos
    }

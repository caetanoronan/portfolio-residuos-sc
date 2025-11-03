"""
Endpoints de Municípios
GET /api/v1/municipios - Lista todos os municípios
GET /api/v1/municipios/{codigo} - Detalhes de um município
GET /api/v1/municipios/{codigo}/residuos - Estimativas de resíduos
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from api.models import (
    ListaMunicipios, 
    MunicipioBase, 
    MunicipioDetalhado,
    MunicipioComResiduos,
    ErrorResponse
)
from api.database import (
    get_municipios_list,
    get_municipio_info,
    calcular_residuos_municipio
)

router = APIRouter()


@router.get(
    "/municipios",
    response_model=ListaMunicipios,
    summary="Listar todos os municípios",
    description="Retorna lista com os 295 municípios de Santa Catarina"
)
async def listar_municipios(
    limit: Optional[int] = Query(None, ge=1, le=295, description="Limitar número de resultados"),
    offset: Optional[int] = Query(0, ge=0, description="Pular N primeiros resultados")
):
    """
    **Lista todos os municípios de Santa Catarina**
    
    - **295 municípios** no total
    - Ordenados alfabeticamente por nome
    - Suporta paginação via `limit` e `offset`
    
    **Exemplo de uso:**
    ```
    GET /api/v1/municipios?limit=10&offset=0
    ```
    """
    municipios_tuple = get_municipios_list()
    # Converter tuple de volta para list de dicts
    municipios = [dict(m) for m in municipios_tuple]
    
    # Aplicar paginação
    if limit:
        municipios = municipios[offset:offset+limit]
    
    return {
        "total": len(municipios_tuple),
        "municipios": municipios
    }


@router.get(
    "/municipios/{codigo_ibge}",
    response_model=MunicipioDetalhado,
    responses={404: {"model": ErrorResponse}},
    summary="Detalhes de um município",
    description="Retorna informações detalhadas de um município específico"
)
async def obter_municipio(codigo_ibge: str):
    """
    **Obtém detalhes de um município específico**
    
    - **codigo_ibge**: Código IBGE de 7 dígitos (ex: 4205407 para Florianópolis)
    
    Retorna:
    - Nome do município
    - Área em km²
    - Número de setores censitários
    - Coordenadas do centróide
    - Bounding box (retângulo envolvente)
    
    **Exemplo de uso:**
    ```
    GET /api/v1/municipios/4205407
    ```
    """
    municipio = get_municipio_info(codigo_ibge)
    
    if not municipio:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Município com código IBGE {codigo_ibge} não encontrado",
                "detail": "Verifique se o código está correto (7 dígitos)"
            }
        )
    
    return municipio


@router.get(
    "/municipios/{codigo_ibge}/residuos",
    response_model=MunicipioComResiduos,
    responses={404: {"model": ErrorResponse}},
    summary="Estimativa de resíduos por município",
    description="Retorna estimativa de geração de resíduos sólidos do município"
)
async def obter_residuos_municipio(codigo_ibge: str):
    """
    **Estimativa de resíduos sólidos de um município**
    
    - **codigo_ibge**: Código IBGE de 7 dígitos
    
    Cálculo baseado em:
    - **População**: Censo IBGE 2022
    - **Taxa per capita**: 0,95 kg/hab/dia (ABRELPE)
    - **Fórmula**: População × 0,95 × 365 ÷ 1000 = toneladas/ano
    
    Retorna:
    - Informações do município
    - População total
    - Resíduos em kg/dia
    - Resíduos em toneladas/ano
    
    **Exemplo de uso:**
    ```
    GET /api/v1/municipios/4205407/residuos
    ```
    
    **Exemplo de resposta:**
    ```json
    {
      "codigo_ibge": "4205407",
      "nome": "Florianópolis",
      "populacao": 537211,
      "residuos": {
        "residuos_kg_dia": 510350.45,
        "residuos_ton_ano": 186277.91
      }
    }
    ```
    """
    resultado = calcular_residuos_municipio(codigo_ibge)
    
    if not resultado:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Município com código IBGE {codigo_ibge} não encontrado",
                "detail": "Verifique se o código está correto (7 dígitos)"
            }
        )
    
    return resultado

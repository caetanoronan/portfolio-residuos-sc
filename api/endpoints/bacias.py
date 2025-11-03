"""
Endpoints de Bacias Hidrográficas
GET /api/v1/bacias - Lista todas as bacias
GET /api/v1/bacias/{id} - Detalhes de uma bacia
GET /api/v1/bacias/{id}/residuos - Estimativas de resíduos
"""

from fastapi import APIRouter, HTTPException
from typing import List

from api.models import (
    ListaBacias,
    BaciaBase,
    BaciaDetalhada,
    BaciaComResiduos,
    ErrorResponse
)
from api.database import (
    get_bacias_list,
    get_bacia_info,
    calcular_residuos_bacia
)

router = APIRouter()


@router.get(
    "/bacias",
    response_model=ListaBacias,
    summary="Listar todas as bacias hidrográficas",
    description="Retorna lista com as 8 macro-bacias de Santa Catarina"
)
async def listar_bacias():
    """
    **Lista todas as bacias hidrográficas de Santa Catarina**
    
    - **8 macro-bacias** no total
    - Baseadas na divisão hidrográfica oficial (ANA)
    - Integração com Ottobacias Nível 5
    
    **Exemplo de uso:**
    ```
    GET /api/v1/bacias
    ```
    """
    bacias = get_bacias_list()
    
    return {
        "total": len(bacias),
        "bacias": bacias
    }


@router.get(
    "/bacias/{bacia_id}",
    response_model=BaciaDetalhada,
    responses={404: {"model": ErrorResponse}},
    summary="Detalhes de uma bacia",
    description="Retorna informações detalhadas de uma bacia específica"
)
async def obter_bacia(bacia_id: int):
    """
    **Obtém detalhes de uma bacia hidrográfica específica**
    
    - **bacia_id**: ID da bacia (1-8)
    
    Retorna:
    - Nome da bacia
    - Área em km²
    - Coordenadas do centróide
    - Tipo (macro ou otto)
    
    **Exemplo de uso:**
    ```
    GET /api/v1/bacias/1
    ```
    """
    bacia = get_bacia_info(bacia_id)
    
    if not bacia:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Bacia com ID {bacia_id} não encontrada",
                "detail": "IDs válidos: 1-8 (macro-bacias)"
            }
        )
    
    return bacia


@router.get(
    "/bacias/{bacia_id}/residuos",
    response_model=BaciaComResiduos,
    responses={404: {"model": ErrorResponse}},
    summary="Estimativa de resíduos por bacia",
    description="Retorna estimativa de geração de resíduos sólidos da bacia"
)
async def obter_residuos_bacia(bacia_id: int):
    """
    **Estimativa de resíduos sólidos de uma bacia hidrográfica**
    
    - **bacia_id**: ID da bacia (1-8)
    
    Cálculo baseado em:
    - **População**: Soma de setores censitários na bacia (spatial join)
    - **Taxa per capita**: 0,95 kg/hab/dia (ABRELPE)
    - **Fórmula**: População × 0,95 × 365 ÷ 1000 = toneladas/ano
    
    Retorna:
    - Informações da bacia
    - População total (via intersecção espacial)
    - Resíduos em kg/dia
    - Resíduos em toneladas/ano
    
    **Exemplo de uso:**
    ```
    GET /api/v1/bacias/1/residuos
    ```
    
    **Exemplo de resposta:**
    ```json
    {
      "id": 1,
      "nome": "Bacia do Itajaí",
      "area_km2": 15000.5,
      "residuos": {
        "populacao": 1200000,
        "residuos_kg_dia": 1140000.0,
        "residuos_ton_ano": 416100.0
      }
    }
    ```
    """
    resultado = calcular_residuos_bacia(bacia_id)
    
    if not resultado:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "NotFound",
                "message": f"Bacia com ID {bacia_id} não encontrada",
                "detail": "IDs válidos: 1-8 (macro-bacias)"
            }
        )
    
    return resultado

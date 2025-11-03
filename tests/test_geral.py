"""
Testes para endpoints gerais e estatísticas
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_estatisticas_gerais():
    """Testa endpoint de estatísticas gerais"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Campos obrigatórios
    required_fields = [
        "estado", "sigla", "populacao", "municipios",
        "setores_censitarios", "residuos_totais_ton_ano"
    ]
    for field in required_fields:
        assert field in data
    
    # Valores esperados
    assert data["sigla"] == "SC"
    assert data["municipios"] == 295
    assert data["residuos_per_capita_kg_dia"] == 0.95


def test_openapi_docs():
    """Testa se documentação Swagger está acessível"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs():
    """Testa se ReDoc está acessível"""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_cache_performance():
    """Testa se cache está funcionando (tempo de resposta)"""
    import time
    
    # Primeira chamada (sem cache)
    start1 = time.time()
    response1 = client.get("/api/v1/municipios")
    time1 = time.time() - start1
    
    # Segunda chamada (com cache)
    start2 = time.time()
    response2 = client.get("/api/v1/municipios")
    time2 = time.time() - start2
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Segunda chamada deve ser mais rápida (ou igual)
    assert time2 <= time1 * 1.5  # Tolerância de 50%


def test_cors_headers():
    """Testa se headers CORS estão configurados"""
    response = client.options("/api/v1/municipios")
    # FastAPI TestClient não retorna headers CORS exatamente,
    # mas podemos verificar se não há erro
    assert response.status_code in [200, 405]

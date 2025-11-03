"""
Testes para endpoints de Municípios
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Testa health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_listar_municipios():
    """Testa listagem de municípios"""
    response = client.get("/api/v1/municipios")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "municipios" in data
    assert data["total"] == 295
    assert len(data["municipios"]) > 0


def test_listar_municipios_com_paginacao():
    """Testa paginação de municípios"""
    response = client.get("/api/v1/municipios?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["municipios"]) == 10


def test_obter_municipio_florianopolis():
    """Testa obtenção de detalhes de Florianópolis"""
    response = client.get("/api/v1/municipios/4205407")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_ibge"] == "4205407"
    assert data["nome"] == "Florianópolis"
    assert data["sigla_uf"] == "SC"
    assert "area_km2" in data
    assert "centroide" in data


def test_obter_municipio_inexistente():
    """Testa obtenção de município inexistente"""
    response = client.get("/api/v1/municipios/9999999")
    assert response.status_code == 404


def test_obter_residuos_florianopolis():
    """Testa cálculo de resíduos de Florianópolis"""
    response = client.get("/api/v1/municipios/4205407/residuos")
    assert response.status_code == 200
    data = response.json()
    assert "residuos" in data
    assert data["residuos"]["taxa_per_capita_kg_dia"] == 0.95
    assert data["residuos"]["populacao"] > 0
    assert data["residuos"]["residuos_ton_ano"] > 0


def test_estrutura_resposta_municipio():
    """Testa estrutura da resposta de município"""
    response = client.get("/api/v1/municipios/4205407")
    assert response.status_code == 200
    data = response.json()
    
    # Campos obrigatórios
    required_fields = ["codigo_ibge", "nome", "sigla_uf"]
    for field in required_fields:
        assert field in data
    
    # Centroide
    assert "centroide" in data
    assert "latitude" in data["centroide"]
    assert "longitude" in data["centroide"]


@pytest.mark.parametrize("codigo_ibge,nome_esperado", [
    ("4202404", "Blumenau"),
    ("4209102", "Joinville"),
    ("4205407", "Florianópolis"),
    ("4204202", "Chapecó"),
])
def test_multiplos_municipios(codigo_ibge, nome_esperado):
    """Testa múltiplos municípios conhecidos"""
    response = client.get(f"/api/v1/municipios/{codigo_ibge}")
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == nome_esperado

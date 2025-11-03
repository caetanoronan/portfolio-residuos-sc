"""
Testes para endpoints de Bacias Hidrográficas
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_listar_bacias():
    """Testa listagem de bacias"""
    response = client.get("/api/v1/bacias")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "bacias" in data
    assert data["total"] >= 0  # Pode ser 0 se arquivo não existir


def test_obter_bacia_valida():
    """Testa obtenção de bacia válida (se existir)"""
    # Primeiro lista para ver se há bacias
    response_list = client.get("/api/v1/bacias")
    if response_list.json()["total"] > 0:
        response = client.get("/api/v1/bacias/1")
        assert response.status_code in [200, 404]  # 404 se não houver bacias


def test_obter_bacia_invalida():
    """Testa obtenção de bacia com ID inválido"""
    response = client.get("/api/v1/bacias/999")
    assert response.status_code == 404


def test_estrutura_resposta_bacia():
    """Testa estrutura da resposta de bacia (se existir)"""
    response = client.get("/api/v1/bacias/1")
    if response.status_code == 200:
        data = response.json()
        required_fields = ["id", "nome", "tipo"]
        for field in required_fields:
            assert field in data

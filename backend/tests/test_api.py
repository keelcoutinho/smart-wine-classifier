import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# ✅ Impede criação de banco físico ao importar a main.py
os.environ["TESTING"] = "1"  

# Caminho para importar o app principal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

# =========================
# ✅  Teste de endpoints
# =========================

# Para rodar:
# - Dentro de /tests:     pytest -v test_api.py
# - Dentro de /backend:   pytest -v tests/test_api.py

# =========================
# 🔧 FIXTURE GLOBAL DE MOCK
# =========================

@pytest.fixture(autouse=True)
def mock_sqlite_connect():
    """
    Mocka completamente o sqlite3.connect para impedir acesso real ao banco.
    Simula um cursor com valores fictícios para testes.
    """
    conn_mock = MagicMock()
    cursor_mock = MagicMock()

    conn_mock.cursor.return_value = cursor_mock
    cursor_mock.execute.return_value = None
    cursor_mock.fetchall.return_value = [
        (
            1, "Exemplo", "Fornecedor X", "***.***.***-173", 7.0, 0.35, 0.4, 2.0,
            0.07, 30.0, 60.0, 0.995, 3.2, 0.6, 11.0, "BOM"
        )
    ]
    cursor_mock.fetchone.return_value = cursor_mock.fetchall.return_value[0]
    cursor_mock.description = [
        ("id",), ("nome",), ("fornecedor",), ("documento",), ("acidez_fixa",), ("acidez_volatil",),
        ("acido_citrico",), ("acucar_residual",), ("cloretos",), ("dioxido_enxofre_livre",),
        ("dioxido_enxofre_total",), ("densidade",), ("ph",), ("sulfatos",), ("teor_alcoolico",), ("classificacao",)
    ]
    cursor_mock.lastrowid = 1
    cursor_mock.rowcount = 1

    with patch("sqlite3.connect", return_value=conn_mock):
        yield

# =========================
# 📦 CLIENT DE TESTE
# =========================

client = TestClient(app)

# =========================
# ✅ TESTES A PARTIR DAQUI
# =========================

def test_rota_POST_response_200():
    """
    Testa a criação de um vinho (POST /vinhos) com payload válido.
    Espera status HTTP 200.
    """
    payload = {
        "nome": "Lagoas",
        "fornecedor": "Vinhos BR",
        "documento": "00623904000173",
        "acidez_fixa": 6.7,
        "acidez_volatil": 0.37,
        "acido_citrico": 0.44,
        "acucar_residual": 5.4,
        "cloretos": 0.061,
        "dioxido_enxofre_livre": 24,
        "dioxido_enxofre_total": 34,
        "densidade": 0.999,
        "ph": 3.29,
        "sulfatos": 0.8,
        "teor_alcoolico": 11.6
    }
    response = client.post("/vinhos", json=payload)
    assert response.status_code == 200

def test_rota_post_response_422():
    """
    Testa a criação de um vinho com dados incompletos.
    Espera erro de validação HTTP 422 (campo 'documento' ausente).
    """
    payload = {
        "nome": "Lagoas",
        "fornecedor": "Vinhos BR",
        "acidez_fixa": 6.7,
        "acidez_volatil": 0.37,
        "acido_citrico": 0.44,
        "acucar_residual": 5.4,
        "cloretos": 0.061,
        "dioxido_enxofre_livre": 24,
        "dioxido_enxofre_total": 34,
        "densidade": 0.999,
        "ph": 3.29,
        "sulfatos": 0.8,
        "teor_alcoolico": 11.6
    }
    response = client.post("/vinhos", json=payload)
    assert response.status_code == 422

def test_resposta_modelo_machine_learning():
    """
    Testa se o modelo de ML retorna corretamente a classificação 'BOM' ou 'RUIM'.
    """
    payload = {
        "nome": "Pias",
        "fornecedor": "Wine/Co",
        "documento": "00623904000173",
        "acidez_fixa": 6.7,
        "acidez_volatil": 0.37,
        "acido_citrico": 0.44,
        "acucar_residual": 2.4,
        "cloretos": 0.061,
        "dioxido_enxofre_livre": 24,
        "dioxido_enxofre_total": 34,
        "densidade": 0.999,
        "ph": 3.29,
        "sulfatos": 0.8,
        "teor_alcoolico": 11.6
    }
    response = client.post("/vinhos", json=payload)
    assert response.status_code == 200
    resultado = response.json()
    assert "classificacao" in resultado
    assert resultado["classificacao"] in ["BOM", "RUIM"]

def test_listar_vinhos():
    """
    Testa a listagem de vinhos (GET /vinhos).
    Verifica se uma lista é retornada e contém campos esperados.
    """
    response = client.get("/vinhos")
    assert response.status_code == 200
    vinhos = response.json()
    assert isinstance(vinhos, list)
    assert len(vinhos) > 0

def test_atualizar_vinho():
    """
    Testa a atualização de um vinho (PUT /vinhos/{id}).
    Verifica se os campos foram atualizados corretamente.
    """
    vinho_id = 1
    payload = {
        "nome": "Atualizado",
        "fornecedor": "Fornecedor Atualizado",
        "documento": "12345678900",
        "acidez_fixa": 7.0,
        "acidez_volatil": 0.3,
        "acido_citrico": 0.4,
        "acucar_residual": 2.5,
        "cloretos": 0.06,
        "dioxido_enxofre_livre": 20,
        "dioxido_enxofre_total": 30,
        "densidade": 0.995,
        "ph": 3.2,
        "sulfatos": 0.7,
        "teor_alcoolico": 11.0
    }
    response = client.put(f"/vinhos/{vinho_id}", json=payload)
    assert response.status_code == 200
    atualizado = response.json()
    assert atualizado["nome"] == "Atualizado"
    assert atualizado["fornecedor"] == "Fornecedor Atualizado"

def test_deletar_vinho():
    """
    Testa a exclusão de um vinho (DELETE /vinhos/{id}).
    Verifica se a mensagem de sucesso é retornada.
    """
    vinho_id = 1
    response = client.delete(f"/vinhos/{vinho_id}")
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Vinho deletado com sucesso."
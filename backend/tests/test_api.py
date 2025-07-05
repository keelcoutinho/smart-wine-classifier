import sqlite3
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app 
from pydantic import BaseModel

# =========================
# ✅  Teste de endpoints
# =========================

# Para rodar:
# - Dentro de /tests:     pytest -v test_api.py
# - Dentro de /backend:   pytest -v tests/test_api.py

# =========================
# 🔧 FIXTURE GLOBAL DO BANCO
# =========================

# Inicializa o banco de dados em memória e o mantém aberto durante toda a execução dos testes
@pytest.fixture(scope="session", autouse=True)
def db_conn():
    # Cria o banco de dados em memória (RAM) e permite acesso entre threads
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    # Cria a tabela dos vinhos igual à usada na aplicação
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vinhos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            fornecedor TEXT,
            documento TEXT,
            acidez_fixa REAL,
            acidez_volatil REAL,
            acido_citrico REAL,
            acucar_residual REAL,
            cloretos REAL,
            dioxido_enxofre_livre REAL,
            dioxido_enxofre_total REAL,
            densidade REAL,
            ph REAL,
            sulfatos REAL,
            teor_alcoolico REAL,
            classificacao TEXT
        )
    ''')
    conn.commit()

    # Armazena a conexão no app para que possa ser usada nos endpoints durante os testes
    app.state._conn = conn
    yield conn  
    conn.close() 

# ====================================
# 🔄 SUBSTITUI A FUNÇÃO get_connection
# ====================================

# Durante os testes, toda vez que get_connection() for chamada, vamos usar a mesma conexão da fixture acima
def get_test_connection():
    return app.state._conn

# Aplica a substituição das dependências no app
app.dependency_overrides = {}
app.dependency_overrides[get_test_connection] = get_test_connection

# Cria o client de teste do FastAPI
client = TestClient(app)

# ============================
# ✅ TESTES A PARTIR DAQUI
# ============================

# ✅ Teste POST com payload completo
def test_rota_POST_response_200():
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

# ✅ Teste POST com payload incompleto
def test_rota_post_response_422():
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

# ✅ Testa se a classificação do modelo aparece na resposta
def test_resposta_modelo_machine_learning():
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

# ✅ Testa listagem de vinhos
def test_listar_vinhos():
    vinho_teste = {
        "nome": "Taos",
        "fornecedor": "Fornecedor X",
        "documento": "12345678900000",
        "acidez_fixa": 7.0,
        "acidez_volatil": 0.35,
        "acido_citrico": 0.40,
        "acucar_residual": 2.0,
        "cloretos": 0.07,
        "dioxido_enxofre_livre": 30,
        "dioxido_enxofre_total": 60,
        "densidade": 0.995,
        "ph": 3.2,
        "sulfatos": 0.6,
        "teor_alcoolico": 11.0
    }

    client.post("/vinhos", json=vinho_teste)

    response = client.get("/vinhos")
    assert response.status_code == 200

    vinhos = response.json()
    assert isinstance(vinhos, list)
    assert len(vinhos) > 0

    vinho = vinhos[0]
    chaves_esperadas = {
        "id",
        "nome",
        "fornecedor",
        "documento",
        "acidez_fixa",
        "acidez_volatil",
        "acido_citrico",
        "acucar_residual",
        "cloretos",
        "dioxido_enxofre_livre",
        "dioxido_enxofre_total",
        "densidade",
        "ph",
        "sulfatos",
        "teor_alcoolico",
        "classificacao"
    }

    assert chaves_esperadas.issubset(set(vinho.keys()))

# ✅ Teste de atualização de vinho
def test_atualizar_vinho():
    novo_vinho = {
        "nome": "Pias",
        "fornecedor": "Wine/Co",
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

    response_post = client.post("/vinhos", json=novo_vinho)
    assert response_post.status_code == 200
    vinho_criado = response_post.json()
    vinho_id = vinho_criado["id"]

    vinho_atualizado = novo_vinho.copy()
    vinho_atualizado["nome"] = "Atualizado"
    vinho_atualizado["fornecedor"] = "Fornecedor Atualizado"

    response_put = client.put(f"/vinhos/{vinho_id}", json=vinho_atualizado)
    assert response_put.status_code == 200
    atualizado = response_put.json()

    assert atualizado["nome"] == "Atualizado"
    assert atualizado["fornecedor"] == "Fornecedor Atualizado"

# ✅ Teste de exclusão de vinho
def test_deletar_vinho():
    novo_vinho = {
        "nome": "Lago",
        "fornecedor": "Fornecedor Z",
        "documento": "99887766554433",
        "acidez_fixa": 6.8,
        "acidez_volatil": 0.36,
        "acido_citrico": 0.42,
        "acucar_residual": 2.8,
        "cloretos": 0.065,
        "dioxido_enxofre_livre": 22,
        "dioxido_enxofre_total": 33,
        "densidade": 0.996,
        "ph": 3.30,
        "sulfatos": 0.75,
        "teor_alcoolico": 11.4
    }

    response_post = client.post("/vinhos", json=novo_vinho)
    assert response_post.status_code == 200
    vinho_criado = response_post.json()
    vinho_id = vinho_criado["id"]

    response_delete = client.delete(f"/vinhos/{vinho_id}")
    assert response_delete.status_code == 200

    response_get = client.get("/vinhos")
    lista = response_get.json()
    assert all(v["id"] != vinho_id for v in lista)
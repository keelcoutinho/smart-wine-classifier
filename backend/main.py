from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import sqlite3
import pickle
import os
import re
from sklearn.metrics import f1_score, accuracy_score

# ====================================
# 🔄 CARREGA O MODELO
# ====================================

## Caminho relativo
CAMINHO_MODELO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'machineLearning',
    'models',
    'melhor_modelo_vinho.pkl'
)

CAMINHO_MODELO = os.path.normpath(CAMINHO_MODELO)

with open(CAMINHO_MODELO, 'rb') as f:
    modelo_carregado = pickle.load(f)
    
# ====================================
# 💾 CONECTAR AO BANCO DE DADOS SQLITE
# ====================================

# Define função para reutilização e testes
def get_connection():
    if os.getenv("TESTING") == "1":
        return sqlite3.connect(":memory:", check_same_thread=False)
    return sqlite3.connect("vinhos.db", check_same_thread=False)

# Criar tabela se não existir 
conn = get_connection()
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
conn.close()

# ====================================
# 🔐 ANONIMIZAÇÃO DO CPF/CNPJ
# ====================================

def anonimizar_documento(doc: str) -> str:
    if not doc:
        return ""

    # Extrai apenas os números
    numeros = re.sub(r'\D', '', doc)

    if len(numeros) == 11:  # CPF
        doc_anon = re.sub(r'\d', '*', numeros[:-3]) + numeros[-3:]
        return f"{doc_anon[:3]}.{doc_anon[3:6]}.{doc_anon[6:9]}-{doc_anon[9:]}"
    
    elif len(numeros) == 14:  # CNPJ
        doc_anon = re.sub(r'\d', '*', numeros[:-3]) + numeros[-3:]
        return f"{doc_anon[:2]}.{doc_anon[2:5]}.{doc_anon[5:8]}/{doc_anon[8:12]}-{doc_anon[12:]}"
    
    else:
        # Documento inválido ou fora dos padrões (retorna mascarado genérico)
        doc_anon = re.sub(r'\d', '*', numeros[:-3]) + numeros[-3:]
        return doc_anon

# Modelo Pydantic
class VinhoEntrada(BaseModel):
    nome: str
    fornecedor: str
    documento: str = Field(..., min_length=11, max_length=20)
    acidez_fixa: float
    acidez_volatil: float
    acido_citrico: float
    acucar_residual: float
    cloretos: float
    dioxido_enxofre_livre: float
    dioxido_enxofre_total: float
    densidade: float
    ph: float
    sulfatos: float
    teor_alcoolico: float

class VinhoSaida(VinhoEntrada):
    id: int
    classificacao: str

# FastAPI app
app = FastAPI(
    title="Wine Quality Classifier",
    description="API para predição da qualidade de vinhos usando ML",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================
# 🛣️ ROTAS A PARTIR DAQUI 
# ====================================

# Rota para criar novo vinho
@app.post("/vinhos", response_model=VinhoSaida)
def criar_vinho(vinho: VinhoEntrada):
    dados = pd.DataFrame([vinho.dict(exclude={"nome", "fornecedor", "documento"})])
    pred = modelo_carregado.predict(dados)[0]
    rotulo = "BOM" if pred == 1 else "RUIM"
    doc_anon = anonimizar_documento(vinho.documento)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vinhos (
            nome, fornecedor, documento, acidez_fixa, acidez_volatil, acido_citrico,
            acucar_residual, cloretos, dioxido_enxofre_livre, dioxido_enxofre_total,
            densidade, ph, sulfatos, teor_alcoolico, classificacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        vinho.nome, vinho.fornecedor, doc_anon,
        vinho.acidez_fixa, vinho.acidez_volatil, vinho.acido_citrico,
        vinho.acucar_residual, vinho.cloretos, vinho.dioxido_enxofre_livre,
        vinho.dioxido_enxofre_total, vinho.densidade, vinho.ph,
        vinho.sulfatos, vinho.teor_alcoolico, rotulo
    ))
    conn.commit()
    vid = cursor.lastrowid
    conn.close()
    return VinhoSaida(id=vid, classificacao=rotulo, **vinho.dict())

# Rota para listar todos os vinhos
@app.get("/vinhos", response_model=List[VinhoSaida])
def listar_vinhos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vinhos")
    linhas = cursor.fetchall()
    colunas = [col[0] for col in cursor.description]
    conn.close()
    return [VinhoSaida(**dict(zip(colunas, linha))) for linha in linhas]

# Rota para atualizar vinho
@app.put("/vinhos/{vinho_id}", response_model=VinhoSaida)
def atualizar_vinho(vinho_id: int, vinho: VinhoEntrada):
    dados = pd.DataFrame([vinho.dict(exclude={"nome", "fornecedor", "documento"})])
    pred = modelo_carregado.predict(dados)[0]
    rotulo = "BOM" if pred == 1 else "RUIM"
    doc_anon = anonimizar_documento(vinho.documento)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vinhos SET nome=?, fornecedor=?, documento=?, acidez_fixa=?, acidez_volatil=?,
        acido_citrico=?, acucar_residual=?, cloretos=?, dioxido_enxofre_livre=?,
        dioxido_enxofre_total=?, densidade=?, ph=?, sulfatos=?, teor_alcoolico=?,
        classificacao=? WHERE id=?
    """, (
        vinho.nome, vinho.fornecedor, doc_anon, vinho.acidez_fixa, vinho.acidez_volatil,
        vinho.acido_citrico, vinho.acucar_residual, vinho.cloretos, vinho.dioxido_enxofre_livre,
        vinho.dioxido_enxofre_total, vinho.densidade, vinho.ph, vinho.sulfatos,
        vinho.teor_alcoolico, rotulo, vinho_id
    ))
    conn.commit()
    conn.close()
    return VinhoSaida(id=vinho_id, classificacao=rotulo, **vinho.dict())

# Rota para deletar vinho
@app.delete("/vinhos/{vinho_id}")
def deletar_vinho(vinho_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vinhos WHERE id=?", (vinho_id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=422, detail="Vinho não encontrado.")
    
    conn.close()
    return {"mensagem": "Vinho deletado com sucesso."}

# ====================================
# 🛣️ SWAGGER 
# ====================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Wine Quality Classifier",
        version="1.0.0",
        description="API para predição de vinhos usando ML com FastAPI",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
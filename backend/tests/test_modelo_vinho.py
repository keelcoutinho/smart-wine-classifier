import os
import pandas as pd
import pickle
import pytest
from sklearn.metrics import accuracy_score, f1_score

# =========================
# ✅  Teste modelo de vinho
# =========================

# Para rodar:
# - Dentro de /tests:     pytest -v test_modelo_vinho.py
# - Dentro de /backend:   pytest -v tests/test_modelo_vinho.py

# Caminho até o modelo salvo
CAMINHO_MODELO = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', '..', 'machineLearning', 'models', 'melhor_modelo_vinho.pkl'
    )
)

# URL do dataset original
URL = "https://raw.githubusercontent.com/keelcoutinho/base-de-dados-teste/refs/heads/main/winequality-red.csv"

# Renomeação de colunas
colunas_renomeadas = {
    'fixed acidity': 'acidez_fixa',
    'volatile acidity': 'acidez_volatil',
    'citric acid': 'acido_citrico',
    'residual sugar': 'acucar_residual',
    'chlorides': 'cloretos',
    'free sulfur dioxide': 'dioxido_enxofre_livre',
    'total sulfur dioxide': 'dioxido_enxofre_total',
    'density': 'densidade',
    'pH': 'ph',
    'sulphates': 'sulfatos',
    'alcohol': 'teor_alcoolico',
    'quality': 'qualidade'
}

# Função de remoção de outliers com fator 10
def remover_outliers(df):
    colunas_numericas = df.select_dtypes(include='number').columns
    indices_outliers = set()
    for coluna in colunas_numericas:
        Q1 = df[coluna].quantile(0.25)
        Q3 = df[coluna].quantile(0.75)
        IQR = Q3 - Q1
        lim_inf = Q1 - 10 * IQR
        lim_sup = Q3 + 10 * IQR
        outliers_coluna = df[(df[coluna] < lim_inf) | (df[coluna] > lim_sup)].index
        indices_outliers.update(outliers_coluna)
    return df.drop(index=indices_outliers).reset_index(drop=True)

# Fixture para carregar e processar os dados como no notebook
@pytest.fixture(scope="module")
def dados_processados():
    df = pd.read_csv(URL, sep=';')
    df.rename(columns=colunas_renomeadas, inplace=True)
    df.dropna(inplace=True)
    df = remover_outliers(df)
    df['classificacao'] = df['qualidade'].apply(lambda x: 1 if x >= 7 else 0)
    X = df.drop(['qualidade', 'classificacao'], axis=1)
    y = df['classificacao']
    return X, y

# Fixture para carregar o modelo salvo
@pytest.fixture(scope="module")
def modelo_carregado():
    with open(CAMINHO_MODELO, 'rb') as f:
        modelo = pickle.load(f)
    return modelo

# ✅ Testa se o modelo tem desempenho adequado nos dados completos
def test_acuracia_do_modelo(dados_processados, modelo_carregado):
    X, y = dados_processados
    y_pred = modelo_carregado.predict(X)

    acuracia = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)

    print(f"\n🎯 Acurácia: {acuracia:.4f}")
    print(f"🎯 F1-score: {f1:.4f}")

    assert acuracia >= 0.75
    assert f1 >= 0.6

# ✅ Testa se o modelo consegue prever um exemplo manual
def test_predicao_manual(modelo_carregado):
    exemplo = pd.DataFrame([{
        'acidez_fixa': 6.7,
        'acidez_volatil': 0.37,
        'acido_citrico': 0.44,
        'acucar_residual': 2.4,
        'cloretos': 0.061,
        'dioxido_enxofre_livre': 24,
        'dioxido_enxofre_total': 34,
        'densidade': 0.999,
        'ph': 3.29,
        'sulfatos': 0.8,
        'teor_alcoolico': 11.6,
    }])

    pred = modelo_carregado.predict(exemplo)
    assert pred[0] in [0, 1]
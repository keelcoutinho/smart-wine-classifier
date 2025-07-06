# 🍷 Wine Quality Classifier

Um sistema inteligente para classificação da qualidade de vinhos tintos utilizando machine learning, com interface web e API RESTful.

## ✨ Funcionalidades

Classificação Automática: Predição da qualidade do vinho (BOM/RUIM) baseada em atributos físico-químicos

Gestão Completa: CRUD de vinhos com armazenamento em banco de dados

Anonimização Segura: Proteção de dados sensíveis (CPF/CNPJ)

Dashboard Intuitivo: Visualização clara dos resultados

## 🛠️ Tecnologias

### 🔙 Backend

* Python 3.11.0

* FastAPI: Framework web moderno e rápido

* SQLite: Banco de dados embutido

* Scikit-learn: Modelos de machine learning

* Pickle: Serialização do modelo treinado

### 🔜 Frontend

* HTML5 & CSS3

* Bootstrap 5: Design responsivo

* JavaScript: Interatividade

* Font Awesome: Ícones

### 🧠 Machine Learning

* Algoritmos: KNN, Árvore de Decisão, Naive Bayes, SVM

* Otimização: GridSearchCV para ajuste de hiperparâmetros

* Métrica Principal: F1-score para avaliação

## 📦 Instalação

Clone o repositório:
``` 
bash
 
git clone https://github.com/keelcoutinho/smart-wine-classifier.git

cd smart-wine-classifier
```

Crie e ative o ambiente virtual (recomendado):

```
bash

cd backend

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\Scripts\activate     # Windows
```

Instale as dependências:

```
bash

pip install -r requirements.txt
```

🚀 Execução
Inicie o servidor backend:

```
bash

uvicorn backend:app --reload
```

Abra o frontend no navegador:

```../frontend/index.html ```


## 📊 Modelo de Machine Learning

Fluxo de Processamento:

Pré-processamento dos dados

Remoção de outliers

Balanceamento com SMOTE

Normalização com StandardScaler

Treinamento e avaliação de 4 modelos

Seleção do melhor modelo baseado no F1-score

| Modelo            | F1-Score | Acurácia |
| ----------------- | -------- | -------- |
| SVM               | 0.65     | 0.89     |
| Árvore de Decisão | 0.60     | 0.87     |
| KNN               | 0.58     | 0.84     |
| Naive Bayes       | 0.46     | 0.78     |


#### 📌 Observações:

Os valores de F1-score refletem o desempenho na classe minoritária ("bom" = 1), após balanceamento com SMOTE.

A SVM foi o melhor modelo neste caso, e deve ser o escolhido para produção e serialização (.pkl).

As métricas foram calculadas com base em classification_report do conjunto de teste (y_test vs y_pred).


## 🌐 Endpoints da API

```POST /vinhos:``` Cria novo registro de vinho

```GET /vinhos:``` Lista todos os vinhos

```GET /vinhos/{id}:``` Obtém detalhes de um vinho

```PUT /vinhos/{id}:``` Atualiza um vinho existente

```DELETE /vinhos/{id}:``` Remove um vinho

## 📝 Estrutura do Projeto

text
```
smart-wine-classifier/
├── backend/                    # Código do servidor (API)
│   ├── main.py                 # Ponto de entrada da API FastAPI
│   ├── tests/                  # Testes automatizados da API
│   └── requirements.txt        # Lista de dependências do backend
│
├── frontend/                   # Interface Web do usuário
│   ├── assets/                 # Imagens e recursos estáticos
│   ├── index.html              # Página principal da interface
│   ├── script.js               # Lógica JavaScript para interação
│   └── style.css               # Estilos CSS da interface
│
├── machineLearning/            # Componentes de Machine Learning
│   ├── data/                   # Conjuntos de dados utilizados
│   ├── models/                 # Modelos treinados e salvos (.pkl)
│   └── notebooks/              # Notebooks Jupyter para análise e treino
│
└── README.md                   # Documentação e instruções do projeto

```

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

Desenvolvido com ❤️ para amantes de vinho 🍇!
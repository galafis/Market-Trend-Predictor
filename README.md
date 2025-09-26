# Market Trend Predictor — Análise e Predição de Tendências de Mercado

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](#) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) ![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB) ![R 4.0+](https://img.shields.io/badge/R-4.0%2B-276DC3)

Toolkit unificado em Python e R para coletar dados de mercado, construir features, treinar modelos preditivos e gerar análises reprodutíveis. Foco em clareza, extensibilidade e fluxo profissional para pesquisa e prototipagem.

- Idioma: Português (padrão). English summary at the end.

---

## Sumário
- [Descrição e Objetivos](#descrição-e-objetivos)
- [Diagrama do Pipeline/Arquitetura](#diagrama-do-pipelinearquitetura)
- [Estrutura de Pastas e Arquivos](#estrutura-de-pastas-e-arquivos)
- [Instalação e Configuração](#instalação-e-configuração)
  - [Python](#python)
  - [R](#r)
  - [Configuração (configpy)](#configuração-configpy)
- [Exemplos de Uso](#exemplos-de-uso)
  - [Coleta e Features em Python](#coleta-e-features-em-python)
  - [Análises e Gráficos em R](#análises-e-gráficos-em-r)
- [Resultados Esperados](#resultados-esperados)
- [Testes, Qualidade e Boas Práticas](#testes-qualidade-e-boas-práticas)
- [Como Contribuir](#como-contribuir)
- [Licença](#licença)
- [English — Brief Summary](#english--brief-summary)

---

## Descrição e Objetivos
O Market Trend Predictor fornece componentes ponta a ponta para:
- Ingestão de dados históricos de mercado (ex.: Alpha Vantage, Yahoo Finance) com cache local.
- Engenharia de atributos (janelas temporais, retornos, indicadores técnicos simples).
- Treinamento e avaliação de modelos clássicos de ML para classificação/regressão de tendência.
- Relatórios e visualizações (R) sobre correlação, distribuição e desempenho do modelo.

Arquivos principais do repositório referenciados nesta documentação:
- market_predictor.py: aplicativo/rotinas centrais em Python para dados, features, modelos e execução local do servidor (quando aplicável).
- analytics.R: funções utilitárias em R para análises exploratórias e gráficos.
- config.py: parâmetros de execução, diretórios e chaves de API.

Objetivo: oferecer uma base didática, reprodutível e extensível para estudos de tendência em séries financeiras.

---

## Diagrama do Pipeline/Arquitetura

```mermaid
flowchart TD
  A[Config (config.py)] --> B[Coleta de Dados\nmarket_predictor.py]
  B -->|CSV/Parquet| C[(data/raw)]
  C --> D[Processamento & Features\nmarket_predictor.py]
  D -->|datasets prontos| E[(data/processed)]
  E --> F[Modelagem\nTreino/Validação]
  F --> G[Resultados\nMétricas e Predições]
  E --> H[R Analytics\nanalytics.R]
  H --> I[Gráficos e Relatórios]
  subgraph Persistência
    C
    E
  end
  subgraph Núcleo Python
    B
    D
    F
    G
  end
  subgraph Núcleo R
    H
    I
  end
```

---

## Estrutura de Pastas e Arquivos

```
Market-Trend-Predictor/
├── market_predictor.py      # Núcleo Python: coleta, features, modelos e execução
├── analytics.R              # Utilitários R: correlação, gráficos e EDA
├── config.py                # Configurações: chaves, diretórios e hiperparâmetros
├── requirements.txt         # Dependências Python
├── README.md                # Esta documentação
└── data/
    ├── raw/                 # Dados brutos (cache de APIs)
    ├── processed/           # Dados limpos/derivados p/ modelagem
    └── samples/             # Conjuntos de exemplo (opcional)
```

Observação: arquivos de frontend citados em versões anteriores (index.html, app.js, styles.css) só devem ser considerados se existirem no repositório. Esta documentação foca nos arquivos confirmados: market_predictor.py, analytics.R, config.py.

---

## Instalação e Configuração

### Python
Requisitos: Python 3.9+

```
# Clonar e entrar no projeto
git clone https://github.com/galafis/Market-Trend-Predictor.git
cd Market-Trend-Predictor

# Ambiente virtual e dependências
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
# venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### R
Requisitos: R 4.0+

```
Rscript -e "install.packages(c('ggplot2','dplyr','corrplot','plotly'), repos='https://cloud.r-project.org')"
```

### Configuração (config.py)
Crie/edite config.py e ajuste variáveis conforme seu ambiente:

Exemplo mínimo:

```python
API_KEYS = {
  'ALPHA_VANTAGE': 'SUA_CHAVE_AQUI'
}

SERVER = {
  'HOST': '127.0.0.1',
  'PORT': 8000
}

MODEL = {
  'LOOKBACK_DAYS': 60,
  'TRAIN_TEST_SPLIT': 0.8,
  # Outros hiperparâmetros (ex.: n_estimators, random_state)
}

DATA_DIRS = {
  'RAW': 'data/raw',
  'PROCESSED': 'data/processed'
}
```

Crie as pastas data/raw e data/processed caso não existam.

---

## Exemplos de Uso

### Coleta e Features em Python
Exemplo 1 — baixar e cachear preços diários, gerar features e treinar um classificador simples:

```python
from market_predictor import fetch_data, features, models

# 1) Coleta (exige API key se usar Alpha Vantage)
prices = fetch_data('AAPL', source='alpha_vantage', cache=True)

# 2) Engenharia de atributos (ex.: retornos, janelas móveis)
X, y = features.make_features(prices)

# 3) Treino e avaliação
clf = models.train_classifier(X, y)
print(models.evaluate(clf, X, y))
```

Exemplo 2 — gerar previsões e salvar dataset processado:

```python
from market_predictor import io_utils, predict

# Supondo que io_utils.write_processed salva em data/processed
io_utils.write_processed('data/processed/aapl.csv', X, y)

# Previsões
preds = predict.infer_classifier(clf, X)
print(preds.head())
```

Observação: os nomes de funções acima refletem a intenção do pipeline. Caso os nomes reais no market_predictor.py diferirem, ajuste as chamadas conforme as assinaturas disponíveis no arquivo.

### Análises e Gráficos em R
Matriz de correlação sobre um CSV processado:

```r
source('analytics.R')
plot_correlation('data/processed/aapl.csv')
```

Outros exemplos comuns em analytics.R podem incluir:
- plot_feature_importance(path)
- plot_prediction_vs_actual(path)

Consulte as funções definidas em analytics.R e adapte os caminhos.

---

## Resultados Esperados
- Métricas de classificação (exemplo):
  - Accuracy ~ 0.75–0.80
  - Precision/Recall/F1 balanceadas
  - ROC-AUC/PR-AUC informativas
- Gráficos ilustrativos gerados pelo R, como:
  - Heatmap de correlação entre features
  - Linha Predição vs. Real em janelas de validação

Imagens de exemplo (placeholders):
- Predição vs Real: https://dummyimage.com/960x360/0d1117/ffffff.png&text=Prediction+vs+Actual+Sample
- Mapa de Correlação: https://dummyimage.com/720x360/161b22/20c997.png&text=Correlation+Heatmap+(example)

Resultados variam conforme ticker, janela e hiperparâmetros.

---

## Testes, Qualidade e Boas Práticas
- Estilo: black/flake8 (opcional) e tipagem gradual quando possível.
- Reprodutibilidade: fixar versões em requirements.txt e usar seeds determinísticos.
- Dados: separar diretórios raw vs processed e manter rastreabilidade.
- Versionamento: branches por feature e PRs pequenos e revisáveis.
- Documentação: docstrings claras e README atualizado conforme mudanças nas APIs.

---

## Como Contribuir
Contribuições são bem-vindas!
1) Abra uma issue descrevendo motivação e escopo.
2) Fork e branch: `git checkout -b feat/minha-melhoria`.
3) Adicione testes/exemplos quando aplicável.
4) Garanta formatação e linting.
5) Abra um PR referenciando a issue com descrição objetiva e, se houver UI, evidências visuais.

---

## Licença
MIT — consulte o arquivo LICENSE.

---

## English — Brief Summary
Market Trend Predictor provides Python routines for data ingestion, feature engineering and modeling, plus R utilities for analytics/plots. See market_predictor.py, analytics.R and config.py for the core workflow; install Python/R deps, configure config.py, then run data collection, feature creation, modeling and R visualizations as shown above.

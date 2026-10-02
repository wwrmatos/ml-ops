# Churn

Projeto-fio-condutor do curso de MLOps: predição de churn (tabular).

## Estrutura

```
src/churn/
├── data.py       # carga + validação
├── features.py   # transformações puras
├── model.py      # treino + tracking MLflow
├── experiments.py # grid de experimentos
├── registry.py   # gate + promoção @champion + load
├── lineage.py    # data_md5 (DVC) e git_commit
├── evaluate.py   # métricas
└── config.py     # Pydantic settings
tests/            # pytest
data/             # dataset (versionado depois: DVC)
pyproject.toml    # deps travadas (uv)
uv.lock
requirements*.txt # mesmas deps, exportadas do uv.lock (pip)
```

## Setup

### Com uv

```bash
uv sync
```

Cria o `.venv`, instala as dependências travadas no `uv.lock` e o próprio pacote
em modo editável.

### Sem uv (venv + pip)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt -r requirements-dev.txt
pip install -e . --no-deps
```

Com o venv ativado, os comandos abaixo funcionam sem o prefixo `uv run`
(`churn-train`, `churn-experiments`, `churn-promote`, `pytest`).

Os `requirements*.txt` são gerados a partir do `uv.lock`. Depois de qualquer
`uv add`/`uv remove`, regere-os:

```bash
uv export --format requirements.txt --no-dev --no-hashes --no-emit-project -o requirements.txt
uv export --format requirements.txt --only-group dev --no-hashes --no-emit-project -o requirements-dev.txt
```

## Uso

Coloque o dataset em `data/churn.csv` e rode:

```bash
uv run churn-train
```

Qualquer setting pode ser sobrescrito por variável de ambiente com o prefixo
`CHURN_` ou por um arquivo `.env`:

```bash
CHURN_DATA_PATH=data/outro.csv CHURN_N_ESTIMATORS=500 uv run churn-train
```

## Experimentos (MLflow)

Cada treino vira um run no experimento `churn` (backend `sqlite:///mlflow.db`),
com params, métricas, tags de linhagem (`data_md5`, `git_commit`) e o modelo
empacotado (signature + input_example).

```bash
uv run churn-experiments   # grid 3x3 (n_estimators x max_depth)
uv run churn-promote       # melhor run por roc_auc -> registry "churn" @champion
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

O `churn-promote` só promove se `roc_auc >= CHURN_MIN_ROC_AUC` (padrão 0.80).
Para consumir o modelo de produção:

```python
from churn.registry import load_champion

model = load_champion()  # models:/churn@champion (pyfunc)
model.predict(X)
```

## Testes

```bash
uv run pytest
```

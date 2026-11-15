# Churn

Projeto-fio-condutor do curso de MLOps: predição de churn (tabular).

## Estrutura

```
src/churn/
├── data.py       # carga + validação
├── features.py   # transformações puras
├── model.py      # treino (instrumentado com MLflow)
├── evaluate.py   # métricas
├── experiments.py# grid rastreado no MLflow
├── lineage.py    # data_md5() e git_commit() para linhagem
├── config.py     # Pydantic settings
├── api.py        # API FastAPI (serve o modelo)
└── app.py        # interface Streamlit (consome a API)
tests/            # pytest
data/             # dataset (versionado depois: DVC)
pyproject.toml    # deps travadas (uv)
uv.lock
.streamlit/       # tema do app
```

## Setup

```bash
uv sync
```

Cria o `.venv`, instala as dependências travadas no `uv.lock` e o próprio pacote
em modo editável.

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

## API e interface Streamlit

O backend é uma API FastAPI (`src/churn/api.py`) que carrega o modelo treinado e
expõe `GET /predict/{customer_id}` (e `GET /customers` com IDs de exemplo):

```bash
uv run uvicorn churn.api:app --port 8000   # docs em http://localhost:8000/docs
```

O frontend (Streamlit) **não** carrega o modelo — ele consulta a API. A URL do
backend vem de `CHURN_API_URL` (padrão `http://localhost:8000`):

```bash
uv run python -m streamlit run src/churn/app.py   # http://localhost:8501
```

Ou os dois juntos via Docker Compose (o app recebe `CHURN_API_URL=http://api:8000`):

```bash
docker compose up --build
```

## Testes

```bash
uv run pytest
```

## MLflow

O treino é rastreado com MLflow Tracking. Cada run registra os params (a config
Pydantic inteira via `model_dump()`), as métricas do teste, o modelo como
artefato e as tags de linhagem `data_md5` + `git_commit` — que amarram o modelo
à versão exata do dado e do código.

O backend local é SQLite (`mlflow.db`). O file store (`./mlruns`) entrou em modo
de manutenção no MLflow 3.x e é recusado.

```bash
uv run churn-train                        # 1 run rastreado
uv run python -m churn.experiments        # grid de 9 runs + melhor por roc_auc
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db   # localhost:5000
```

Para apontar para um tracking server do time:

```bash
CHURN_MLFLOW_TRACKING_URI=http://mlflow.local:5000 uv run churn-train
```

`mlflow.db`, `mlruns/` e `mlartifacts/` são gitignored — experimentos locais não
vão para o Git.

## Deploy na EC2

Na instância a stack sobe via Docker Compose: `app` (Streamlit, :8501), `api`
(FastAPI, :8000) e `mlflow` (tracking server, :5000), todos com
`restart: unless-stopped` — voltam sozinhos após reboot. O banco e os artefatos
do MLflow ficam persistidos em `./mlflow/` (volume).

### A instância não treina

A instância é uma t3.micro (~900 MB de RAM + 2 GB de swap): serve predição e
tracking, mas **treinar nela estoura a memória**. O fluxo é treinar localmente
e publicar o resultado:

1. **Treine localmente, rastreando no MLflow da EC2:**

   ```bash
   CHURN_MLFLOW_TRACKING_URI=http://<ip-da-ec2>:5000 uv run churn-train
   ```

   Params, métricas e o modelo vão pro MLflow remoto (UI em
   `http://<ip-da-ec2>:5000`).

2. **Suba o modelo treinado para a instância:**

   ```bash
   scp -i churn-key.pem models/model.pkl ubuntu@<ip-da-ec2>:~/ml-ops/models/
   ```

   A API mantém o modelo e a base em cache (`lru_cache` em `src/churn/api.py`),
   então depois de copiar o arquivo reinicie o container:

   ```bash
   ssh -i churn-key.pem ubuntu@<ip-da-ec2> "sudo docker restart ml-ops-api-1"
   ```

### Fonte de dados: CSV ou Postgres

Sem configuração extra, a API e o treino leem `data/churn.csv`. Definindo
`CHURN_DATABASE_URL` (ex.:
`postgresql+psycopg://churn:<senha>@<ip-privado>:5432/churn`), `carregar_dados`
passa a ler a tabela `customers` do Postgres — as colunas em `snake_case` do
banco são renomeadas de volta pros nomes do CSV dentro da consulta, então o
restante do pipeline não muda. No deploy da EC2, a URL fica no `.env` da
instância (fora do git) e o compose a injeta no serviço `api`.

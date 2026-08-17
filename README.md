# Churn

Projeto-fio-condutor do curso de MLOps: predição de churn (tabular).

## Estrutura

```
src/churn/
├── data.py       # carga + validação
├── features.py   # transformações puras
├── model.py      # treino
├── evaluate.py   # métricas
└── config.py     # Pydantic settings
tests/            # pytest
data/             # dataset (versionado depois: DVC)
pyproject.toml    # deps travadas (uv)
uv.lock
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

## Testes

```bash
uv run pytest
```

## O que mudou em relação ao script original

O modelo treinado é **o mesmo** do script original: `fillna(2200)`, a
normalização manual por constantes, o split e a floresta continuam sem
`random_state`. O que mudou é só o entorno:

- caminho absoluto da máquina da autora → `config.py` (env/`.env`)
- script único → módulos com funções puras e testadas
- `LabelEncoder` reusado entre colunas → codificação por coluna (mesmos códigos,
  sem o estado compartilhado)
- só acurácia → accuracy, precision, recall, f1, roc_auc (medição, não afeta o
  `fit`)
- nome de arquivo versionado à mão (`modelo_final_v3_ok.pkl`) → `config.model_path`

Como não há `random_state`, cada execução dá uma acurácia um pouco diferente —
isso é fiel ao original e foi uma decisão consciente.

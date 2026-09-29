import mlflow
from sklearn.ensemble import RandomForestClassifier

from churn.config import Settings, settings
from churn.data import carregar_dados, validar_dados
from churn.evaluate import avaliar
from churn.features import construir_features
from churn.lineage import data_md5, git_commit
from churn.model import configurar_mlflow, split

GRID_N_ESTIMATORS = (100, 200, 500)
GRID_MAX_DEPTH = (None, 8, 16)


def run_grid(config: Settings = settings) -> None:
    df = validar_dados(carregar_dados(config.data_path))
    X, y = construir_features(df, config.target, config.id_column)
    X_train, X_test, y_train, y_test = split(X, y, config)

    configurar_mlflow(config)
    tags = {"data_md5": data_md5(config.data_path), "git_commit": git_commit()}

    with mlflow.start_run(run_name="grid-rf"):
        mlflow.set_tags(tags)
        for n in GRID_N_ESTIMATORS:
            for depth in GRID_MAX_DEPTH:
                with mlflow.start_run(run_name=f"rf-n{n}-d{depth}", nested=True):
                    mlflow.set_tags(tags)
                    mlflow.log_params(
                        {
                            "n_estimators": n,
                            "max_depth": depth,
                            "test_size": config.test_size,
                            "random_state": config.random_state,
                        }
                    )
                    model = RandomForestClassifier(
                        n_estimators=n,
                        max_depth=depth,
                        random_state=config.random_state,
                    ).fit(X_train, y_train)
                    metrics = avaliar(model, X_test, y_test)
                    mlflow.log_metrics(metrics)
                    print(f"rf-n{n}-d{depth}: roc_auc={metrics['roc_auc']:.4f}")


def melhor_run(config: Settings = settings):
    """Consulta os runs do experiment e devolve o de maior roc_auc."""
    configurar_mlflow(config)
    runs = mlflow.search_runs(
        experiment_names=[config.mlflow_experiment],
        order_by=["metrics.roc_auc DESC"],
    )
    if runs.empty:
        raise RuntimeError("nenhum run encontrado - rode o grid antes")
    return runs.iloc[0]


def main() -> None:
    run_grid()
    best = melhor_run()
    print(
        "melhor run:",
        best["run_id"],
        best.get("params.n_estimators"),
        best.get("params.max_depth"),
        f"roc_auc={best['metrics.roc_auc']:.4f}",
    )


if __name__ == "__main__":
    main()

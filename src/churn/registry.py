import mlflow
from mlflow import MlflowClient

from churn.config import Settings, settings

CHAMPION = "champion"


def best_run(config: Settings):
    runs = mlflow.search_runs(
        experiment_names=[config.experiment_name],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["metrics.roc_auc DESC"],
        max_results=1,
    )
    if runs.empty:
        raise ValueError(f"nenhum run no experimento '{config.experiment_name}'")
    return runs.iloc[0]


def promote(config: Settings = settings) -> int:
    mlflow.set_tracking_uri(config.tracking_uri)
    best = best_run(config)
    roc_auc = best["metrics.roc_auc"]

    if roc_auc < config.min_roc_auc:
        raise ValueError(
            f"roc_auc {roc_auc:.4f} abaixo do limiar {config.min_roc_auc} — não promove"
        )

    mv = mlflow.register_model(
        f"runs:/{best['run_id']}/model", config.registered_model_name
    )
    MlflowClient().set_registered_model_alias(
        config.registered_model_name, CHAMPION, mv.version
    )
    print(
        f"{config.registered_model_name} v{mv.version} @{CHAMPION} "
        f"({best['tags.mlflow.runName']}, roc_auc {roc_auc:.4f})"
    )
    return int(mv.version)


def load_champion(config: Settings = settings):
    mlflow.set_tracking_uri(config.tracking_uri)
    return mlflow.pyfunc.load_model(
        f"models:/{config.registered_model_name}@{CHAMPION}"
    )


def cli() -> None:
    promote()


if __name__ == "__main__":
    cli()

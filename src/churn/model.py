import pickle
from pathlib import Path

import mlflow
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from churn.config import Settings, settings
from churn.data import carregar_dados, validar_dados
from churn.evaluate import avaliar
from churn.features import construir_features
from churn.lineage import data_md5, git_commit


def split(X: pd.DataFrame, y: pd.Series, config: Settings):
    return train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=y,
    )


def train(X: pd.DataFrame, y: pd.Series, config: Settings) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=config.n_estimators, random_state=config.random_state
    )
    model.fit(X, y)
    return model


def save_model(model: RandomForestClassifier, path: Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load_model(path: Path) -> RandomForestClassifier:
    with open(path, "rb") as f:
        return pickle.load(f)


def configurar_mlflow(config: Settings = settings) -> None:
    """Fixa o destino do tracking - evita mlruns/ espalhados por varias pastas."""
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(config.mlflow_experiment)


def main(config: Settings = settings) -> dict[str, float]:
    df = validar_dados(carregar_dados(config.data_path))
    X, y = construir_features(df, config.target, config.id_column)
    X_train, X_test, y_train, y_test = split(X, y, config)

    configurar_mlflow(config)
    with mlflow.start_run(run_name="rf"):
        # linhagem: qual dado + qual codigo geraram este modelo
        mlflow.set_tags(
            {
                "data_md5": data_md5(config.data_path),
                "git_commit": git_commit(),
            }
        )
        # a config Pydantic vira params num passo so
        mlflow.log_params(config.model_dump())

        model = train(X_train, y_train, config)
        metrics = avaliar(model, X_test, y_test)

        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(
            model,
            name="model",  # mlflow 3.x: artifact_path= foi renomeado para name=
            signature=infer_signature(X_train, model.predict(X_train)),
            input_example=X_train.head(3),
            # o modelo e gerado aqui mesmo: skops precisa do tipo declarado
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

    save_model(model, config.model_path)

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")
    return metrics


def cli() -> None:
    main()


if __name__ == "__main__":
    cli()

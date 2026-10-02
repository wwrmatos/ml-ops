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
        X, y, test_size=config.test_size, random_state=config.random_state
    )


def train(X: pd.DataFrame, y: pd.Series, config: Settings) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        random_state=config.random_state,
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


def prepare(config: Settings):
    df = validar_dados(carregar_dados(config.data_path))
    X, y = construir_features(df, config.target, config.id_column)
    return split(X, y, config)


def setup_mlflow(config: Settings) -> None:
    mlflow.set_tracking_uri(config.tracking_uri)
    mlflow.set_experiment(config.experiment_name)


def run_name(config: Settings) -> str:
    return f"rf-n{config.n_estimators}-d{config.max_depth}"


def run_experiment(config: Settings, splits=None):
    X_train, X_test, y_train, y_test = splits or prepare(config)

    with mlflow.start_run(run_name=run_name(config)) as run:
        mlflow.set_tags({"data_md5": data_md5(), "git_commit": git_commit()})
        mlflow.log_params(config.model_dump())

        model = train(X_train, y_train, config)
        metrics = avaliar(model, X_test, y_test)
        mlflow.log_metrics(metrics)

        signature = infer_signature(X_train, model.predict(X_train))
        mlflow.sklearn.log_model(
            model,
            name="model",
            signature=signature,
            input_example=X_train.head(3),
            serialization_format="cloudpickle",
        )

    return run.info.run_id, model, metrics


def main(config: Settings = settings) -> dict[str, float]:
    setup_mlflow(config)
    _, model, metrics = run_experiment(config)
    save_model(model, config.model_path)

    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")
    return metrics


def cli() -> None:
    main()


if __name__ == "__main__":
    cli()

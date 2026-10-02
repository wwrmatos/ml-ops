from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHURN_", env_file=".env", protected_namespaces=()
    )

    data_path: Path = Path("data/churn.csv")
    model_path: Path = Path("models/model.pkl")

    target: str = "Churn"
    id_column: str = "customerID"

    test_size: float = 0.25
    n_estimators: int = 200
    max_depth: int | None = 8
    random_state: int = 42

    tracking_uri: str = "sqlite:///mlflow.db"
    experiment_name: str = "churn"
    registered_model_name: str = "churn"
    min_roc_auc: float = 0.80


settings = Settings()

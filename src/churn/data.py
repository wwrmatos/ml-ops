from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from churn.config import settings
from churn.schema import ChurnSchema

COLUNAS_OBRIGATORIAS = [
    "customerID",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

# O banco guarda as colunas em snake_case; renomeamos de volta pro nome do
# CSV porque o restante do pipeline (features, modelo) fala no nome original.
_CONSULTA_CLIENTES = """
SELECT
  customer_id       AS "customerID",
  gender,
  senior_citizen    AS "SeniorCitizen",
  partner           AS "Partner",
  dependents        AS "Dependents",
  tenure,
  phone_service     AS "PhoneService",
  multiple_lines    AS "MultipleLines",
  internet_service  AS "InternetService",
  online_security   AS "OnlineSecurity",
  online_backup     AS "OnlineBackup",
  device_protection AS "DeviceProtection",
  tech_support      AS "TechSupport",
  streaming_tv      AS "StreamingTV",
  streaming_movies  AS "StreamingMovies",
  contract          AS "Contract",
  paperless_billing AS "PaperlessBilling",
  payment_method    AS "PaymentMethod",
  monthly_charges   AS "MonthlyCharges",
  total_charges     AS "TotalCharges",
  churn             AS "Churn"
FROM customers
"""


def carregar_dados(caminho: Path) -> pd.DataFrame:
    # Com CHURN_DATABASE_URL definido os dados vêm do Postgres; sem ele, do CSV.
    if settings.database_url:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            return pd.read_sql(text(_CONSULTA_CLIENTES), conn)
    if not Path(caminho).exists():
        raise FileNotFoundError(f"dataset nao encontrado: {caminho}")
    return pd.read_csv(caminho)


def validar_dados(df: pd.DataFrame) -> pd.DataFrame:
    ausentes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if ausentes:
        raise ValueError(f"colunas ausentes: {ausentes}")
    if df.empty:
        raise ValueError("dataset vazio")
    return df

def drop_identifier(df: pd.DataFrame, id_column: str | None) -> pd.DataFrame:
    if id_column and id_column in df.columns:
        return df.drop(columns=[id_column])
    return df

def coerce_total_charges(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])
    return df

def load_clean(caminho: Path, id_column: str = "customerID", target: str = "Churn") -> pd.DataFrame:
    df = carregar_dados(caminho)
    df = validar_dados(df)
    df = drop_identifier(df, id_column)
    df = coerce_total_charges(df)

    if target not in df.columns:
        raise ValueError(f"coluna target ausente: {target}")

    df = ChurnSchema.validate(df, lazy=True)
    return df
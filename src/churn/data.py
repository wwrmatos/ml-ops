from pathlib import Path
from churn.schema import ChurnSchema
import pandas as pd

COLUNAS_OBRIGATORIAS = [
    "customerID",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

def carregar_dados(caminho: Path) -> pd.DataFrame:
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
import subprocess
from pathlib import Path

import yaml


def data_md5(caminho_dados: Path = Path("data/churn.csv")) -> str:
    """Le o md5 do dado versionado pelo DVC - a versao exata do churn.csv."""
    ponteiro = Path(f"{caminho_dados}.dvc")
    doc = yaml.safe_load(ponteiro.read_text())
    return doc["outs"][0]["md5"]


def git_commit() -> str:
    """Hash do commit atual - a versao exata do codigo."""
    resultado = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    return resultado.stdout.strip() or "desconhecido"

import hashlib
import subprocess
from pathlib import Path

import yaml


def data_md5(caminho_dados: Path = Path("data/churn.csv")) -> str:
    """MD5 da versao exata do churn.csv.

    Se o dado ainda for versionado pelo DVC, le o hash do ponteiro .dvc;
    caso contrario, calcula o hash direto do arquivo (dado no git)."""
    ponteiro = Path(f"{caminho_dados}.dvc")
    if ponteiro.exists():
        doc = yaml.safe_load(ponteiro.read_text())
        return doc["outs"][0]["md5"]
    return hashlib.md5(Path(caminho_dados).read_bytes()).hexdigest()


def git_commit() -> str:
    """Hash do commit atual - a versao exata do codigo."""
    try:
        resultado = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "desconhecido"
    return resultado.stdout.strip() or "desconhecido"

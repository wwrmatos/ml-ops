import subprocess
from pathlib import Path

import yaml


def data_md5(dvc_file: Path = Path("data/churn.csv.dvc")) -> str:
    meta = yaml.safe_load(Path(dvc_file).read_text())
    return meta["outs"][0]["md5"]


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()

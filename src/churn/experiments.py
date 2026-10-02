from churn.config import Settings, settings
from churn.model import prepare, run_experiment, run_name, setup_mlflow

GRID_N_ESTIMATORS = (100, 200, 500)
GRID_MAX_DEPTH = (None, 8, 16)


def main(config: Settings = settings) -> None:
    setup_mlflow(config)
    splits = prepare(config)

    for n in GRID_N_ESTIMATORS:
        for depth in GRID_MAX_DEPTH:
            cfg = config.model_copy(update={"n_estimators": n, "max_depth": depth})
            _, _, metrics = run_experiment(cfg, splits)
            print(f"{run_name(cfg)}: roc_auc={metrics['roc_auc']:.4f}")


if __name__ == "__main__":
    main()

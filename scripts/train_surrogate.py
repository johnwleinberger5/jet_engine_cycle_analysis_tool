"""Load LHS dataset, train EngineRegressor, save R^2 plot to outputs/r2_score.png."""

from pathlib import Path

import matplotlib.pyplot as plt

from pipeline.lhs_study import LHSDataset
from pipeline.surrogate import EngineRegressor

_DATASET_PATH = Path("outputs/lhs_dataset.pkl")
_R2_PLOT_PATH = Path("outputs/r2_score.png")
_N_TRIALS = 50

if __name__ == "__main__":
    print("Loading dataset...", flush=True)
    ds = LHSDataset(_DATASET_PATH)
    print(f"Dataset loaded: {len(ds.df):,} samples")

    print(f"Training surrogate ({_N_TRIALS} Optuna trials)...", flush=True)
    print_every = max(1, _N_TRIALS // 10)

    def _shape_str(params: dict) -> str:
        return f"MLP(4 -> {params['h1']} -> {params['h2']} -> {params['h3']} -> 2)"

    def _progress_callback(study: object, trial: object) -> None:
        n = trial.number + 1
        if n % print_every == 0:
            print(
                f"  {n} / {_N_TRIALS} Optuna trials complete"
                f"  |  this trial: {_shape_str(trial.params)}"
                f"  |  best so far: {_shape_str(study.best_trial.params)}"
                f"  (val loss: {study.best_value:.6f})",
                flush=True,
            )

    reg = EngineRegressor(ds, n_optuna_trials=_N_TRIALS, optuna_callback=_progress_callback)
    print(f"\nSelected architecture: {reg.model}", flush=True)

    r2_train = reg.r2_train()
    r2_test = reg.r2_test()

    print("\nR^2 scores:")
    for col in r2_train:
        print(f"  {col}")
        print(f"    train: {r2_train[col]:.4f}")
        print(f"    test:  {r2_test[col]:.4f}")

    # Save R^2 bar chart
    labels = ["Specific Thrust\n(train)", "Specific Thrust\n(test)",
              "SFC\n(train)", "SFC\n(test)"]
    values = [
        r2_train["specific_thrust_n_per_kgs"],
        r2_test["specific_thrust_n_per_kgs"],
        r2_train["sfc_kg_per_s_per_n"],
        r2_test["sfc_kg_per_s_per_n"],
    ]
    colors = ["#4c72b0", "#87a9d4", "#c44e52", "#e89b9d"]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("R^2")
    ax.set_title("Surrogate Model R^2 — Train vs Test")
    ax.axhline(1.0, color="gray", linewidth=0.8, linestyle="--")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9)

    _R2_PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(_R2_PLOT_PATH, dpi=150)
    plt.close(fig)
    print(f"\nR^2 plot saved to {_R2_PLOT_PATH}")
    print(f"Model saved to outputs/engine_regressor.pkl")

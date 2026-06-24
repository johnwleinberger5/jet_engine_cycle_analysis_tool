"""# ML Surrogate Model

<p style="color:#888; font-size:0.9em;">v0.2.0</p>

A neural network surrogate trained on
<a href="lhs_study.html">Latin Hypercube Sampling</a>
data to predict engine cycle performance across a four-dimensional input space —
<a href="acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>,
Mach,
<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>,
and altitude — at a fraction of the cost of calling the C++ solver.

<p><em><a href="index.html">Back to trade study results &rarr;</a></em></p>

---

## Why a Surrogate?

The C++ solver evaluates one operating point at a time. The base trade study
(30 x 26 = 780 solver calls) is fast, but sweeping a third or fourth variable
(e.g. animating over
<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
or altitude) would require thousands of calls per frame. The surrogate
evaluates an entire OPR x Mach grid in milliseconds, making animated sweeps
and interactive exploration practical.

---

## Data Generation - Latin Hypercube Sampling

<a href="lhs_study.html#LHSDataset"><code>LHSDataset</code></a> uses
<code>scipy.stats.qmc.LatinHypercube</code> to generate a space-filling
design over the four-dimensional input space. Unlike a full-factorial grid,
LHS guarantees uniform marginal coverage - no input dimension is
over- or under-sampled.

Sweep bounds:

| Input | Min | Max |
|---|---|---|
| OPR | 10 | 40 |
| Mach | 0.5 | 1.7 |
| TIT (K) | 1200 | 1800 |
| Altitude (ft) | 20,000 | 70,000 |

Default dataset: 20,000 samples, seed = 42 for reproducibility.

---

## Model Architecture

<a href="surrogate.html#EngineRegressor"><code>EngineRegressor</code></a>
is a three-hidden-layer MLP (4 inputs -> h1 -> h2 -> h3 -> 2 outputs)
implemented in PyTorch. Nodes per hidden layer are tuned by
<a href="https://optuna.org">Optuna</a> (50 trials, minimizing validation loss).

Data split: 70% train / 15% validation / 15% test. Optuna tunes against
the validation set only - the test set is held out until final R^2 scoring,
ensuring no data leakage into hyperparameter selection.

<a href="acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
is log-transformed before training because it spans orders of magnitude and
has extreme values near zero specific thrust. The network learns log(SFC)
and the inverse transform is applied on prediction.

---

## R^2 Results

<img src="r2_score.png" width="84%" alt="R^2 train and test scores for specific thrust and SFC"/>

---

## TIT Sweep - Specific Thrust

The animation below sweeps
<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
from 1200 K to 1800 K in 10 K steps at fixed altitude = 60,000 ft.
The colorbar and contour levels are anchored to the static trade study
range (TIT = 1600 K) so frames are directly comparable to the
<a href="index.html">front page plots</a>.

<img src="surrogate_tit_sweep_thrust.gif" width="84%"
     alt="Specific thrust over OPR x Mach as TIT sweeps 1200-1800 K"/>

---

## TIT Sweep - SFC

<img src="surrogate_tit_sweep.gif" width="84%"
     alt="SFC over OPR x Mach as TIT sweeps 1200-1800 K"/>

Note: color banding in the GIFs is a hard GIF format limitation (256 colors
per frame). The underlying model resolution is continuous - see the
<a href="index.html">static plots</a> for the true output quality at TIT = 1600 K.

---

## Reproducing the Results

```bash
# 1. Generate LHS dataset (~20k solver calls, ~5 min)
python scripts/run_lhs_study.py

# 2. Train surrogate (50 Optuna trials, ~10 min)
python scripts/train_surrogate.py

# 3. Generate GIF animations
python scripts/run_surrogate_gif.py
```
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from pipeline.lhs_study import LHSDataset, read_pkl, write_pkl

optuna.logging.set_verbosity(optuna.logging.WARNING)

_DEFAULT_MODEL_PATH = Path("outputs/engine_regressor.pkl")

_INPUT_COLS = ["opr", "mach", "tit_k", "altitude_ft"]
_OUTPUT_COLS = ["specific_thrust_n_per_kgs", "sfc_kg_per_s_per_n"]

# Indices of output columns to log-transform before z-scoring.
# SFC spans orders of magnitude and has extreme values near zero thrust,
# so training on log(SFC) produces a much smoother regression surface.
_LOG_OUTPUT_COLS = [1]  # index of sfc_kg_per_s_per_n in _OUTPUT_COLS

_TRAIN_FRAC = 0.70
_VAL_FRAC = 0.15  # remaining 0.15 goes to test
_SEED = 42


class _MLP(nn.Module):
    """Three-hidden-layer fully connected network.

    Args:
        n_inputs: Number of input features.
        n_outputs: Number of output targets.
        hidden_sizes: Sequence of three node counts for the hidden layers.
    """

    def __init__(
        self,
        n_inputs: int,
        n_outputs: int,
        hidden_sizes: tuple[int, int, int],
    ) -> None:
        super().__init__()
        self.hidden_sizes = hidden_sizes
        h1, h2, h3 = hidden_sizes
        self.net = nn.Sequential(
            nn.Linear(n_inputs, h1), nn.ReLU(),
            nn.Linear(h1, h2), nn.ReLU(),
            nn.Linear(h2, h3), nn.ReLU(),
            nn.Linear(h3, n_outputs),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def __repr__(self) -> str:
        h1, h2, h3 = self.hidden_sizes
        return f"MLP(4 -> {h1} -> {h2} -> {h3} -> 2)"


class EngineRegressor:
    """Surrogate model mapping engine cycle inputs to performance outputs.

    Can be constructed from an existing trained model (pkl path) or trained
    fresh from a ``LHSDataset``.

    Attributes:
        model: Trained PyTorch MLP.
    """

    model: _MLP

    def __init__(
        self,
        source: Path | LHSDataset,
        n_optuna_trials: int = 20,
        optuna_callback: Callable | None = None,
    ) -> None:
        """Load an existing model or train a new one.

        Args:
            source: If a ``Path``, load a previously saved
                ``EngineRegressor`` from that pickle file. If a
                ``LHSDataset``, train a new model and save it to
                ``outputs/engine_regressor.pkl``.
            n_optuna_trials: Number of Optuna trials for hyperparameter
                search. Only used when ``source`` is a ``LHSDataset``.
            optuna_callback: Optional callable passed to
                ``study.optimize`` as a callback. Signature:
                ``(study, trial) -> None``. Only used when ``source`` is
                a ``LHSDataset``.

        Raises:
            FileNotFoundError: If ``source`` is a ``Path`` that does not exist.
            TypeError: If ``source`` is neither a ``Path`` nor a ``LHSDataset``.
        """
        if isinstance(source, (str, Path)):
            saved = read_pkl(Path(source))
            self.__dict__.update(saved.__dict__)
        elif isinstance(source, LHSDataset):
            self._prepare_data(source.df)
            self._train(n_optuna_trials, optuna_callback)
            write_pkl(_DEFAULT_MODEL_PATH, self)
        else:
            raise TypeError(
                f"source must be a Path or LHSDataset, got {type(source)}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict specific thrust and SFC for a batch of operating points.

        Args:
            df: DataFrame with columns ``opr``, ``mach``, ``tit_k``,
                ``altitude_ft``.

        Returns:
            DataFrame with columns ``specific_thrust_n_per_kgs`` and
            ``sfc_kg_per_s_per_n``, one row per input row.
        """
        x = torch.tensor(
            self._scale_inputs(df[_INPUT_COLS].values), dtype=torch.float32
        )
        self.model.eval()
        with torch.no_grad():
            y_norm = self.model(x).numpy()
        y = self._unscale_outputs(y_norm)
        return pd.DataFrame(y, columns=_OUTPUT_COLS)

    def r2_train(self) -> dict[str, float]:
        """R² score on the training split for each output.

        Returns:
            Dict mapping output column name to R² value.
        """
        return self._r2(self._x_train, self._y_train)

    def r2_test(self) -> dict[str, float]:
        """R² score on the held-out test split for each output.

        Returns:
            Dict mapping output column name to R² value.
        """
        return self._r2(self._x_test, self._y_test)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _prepare_data(self, df: pd.DataFrame) -> None:
        """Split DataFrame into train/test tensors and compute scale params."""
        # Drop unphysical rows where any log-transformed output is non-positive
        for i in _LOG_OUTPUT_COLS:
            df = df[df[_OUTPUT_COLS[i]] > 0]

        x_raw = df[_INPUT_COLS].values.astype(np.float32)
        y_raw = df[_OUTPUT_COLS].values.astype(np.float32)

        rng = np.random.default_rng(_SEED)
        idx = rng.permutation(len(x_raw))
        n_train = int(len(x_raw) * _TRAIN_FRAC)
        n_val = int(len(x_raw) * _VAL_FRAC)
        train_idx = idx[:n_train]
        val_idx = idx[n_train:n_train + n_val]
        test_idx = idx[n_train + n_val:]

        # Log-transform skewed outputs before fitting normalization stats
        y_log = y_raw.copy()
        y_log[:, _LOG_OUTPUT_COLS] = np.log(y_log[:, _LOG_OUTPUT_COLS])

        # Fit normalization on training set only (using log-transformed values)
        self._x_mean = x_raw[train_idx].mean(axis=0)
        self._x_std = x_raw[train_idx].std(axis=0) + 1e-8
        self._y_mean = y_log[train_idx].mean(axis=0)
        self._y_std = y_log[train_idx].std(axis=0) + 1e-8

        # Z-score the already-logged outputs (no second log)
        def _zscore(y: np.ndarray) -> torch.Tensor:
            return torch.tensor(((y - self._y_mean) / self._y_std).astype(np.float32))

        self._x_train = torch.tensor(self._scale_inputs(x_raw[train_idx]))
        self._y_train = _zscore(y_log[train_idx])
        self._x_val = torch.tensor(self._scale_inputs(x_raw[val_idx]))
        self._y_val = _zscore(y_log[val_idx])
        self._x_test = torch.tensor(self._scale_inputs(x_raw[test_idx]))
        self._y_test = _zscore(y_log[test_idx])

    def _scale_inputs(self, x: np.ndarray) -> np.ndarray:
        return ((x - self._x_mean) / self._x_std).astype(np.float32)

    def _scale_outputs(self, y: np.ndarray) -> np.ndarray:
        y = y.copy()
        y[:, _LOG_OUTPUT_COLS] = np.log(y[:, _LOG_OUTPUT_COLS])
        return ((y - self._y_mean) / self._y_std).astype(np.float32)

    def _unscale_outputs(self, y_norm: np.ndarray) -> np.ndarray:
        y = (y_norm * self._y_std + self._y_mean).astype(np.float64)
        y[:, _LOG_OUTPUT_COLS] = np.exp(y[:, _LOG_OUTPUT_COLS])
        return y

    def _build_model(self, hidden_sizes: tuple[int, int, int]) -> _MLP:
        return _MLP(n_inputs=len(_INPUT_COLS), n_outputs=len(_OUTPUT_COLS),
                    hidden_sizes=hidden_sizes)

    def _fit(
        self,
        model: _MLP,
        epochs: int = 100,
        lr: float = 1e-3,
        batch_size: int = 512,
    ) -> float:
        """Train ``model`` and return final validation loss."""
        loader = DataLoader(
            TensorDataset(self._x_train, self._y_train),
            batch_size=batch_size,
            shuffle=True,
        )
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        loss_fn = nn.MSELoss()
        model.train()
        for _ in range(epochs):
            for xb, yb in loader:
                opt.zero_grad()
                loss_fn(model(xb), yb).backward()
                opt.step()
        model.eval()
        with torch.no_grad():
            val_loss = loss_fn(model(self._x_val), self._y_val).item()
        return val_loss

    def _train(self, n_trials: int, callback: Callable | None = None) -> None:
        """Run Optuna to find best hidden layer sizes, then train final model."""
        def objective(trial: optuna.Trial) -> float:
            h1 = trial.suggest_int("h1", 8, 64)
            h2 = trial.suggest_int("h2", 8, 64)
            h3 = trial.suggest_int("h3", 8, 64)
            m = self._build_model((h1, h2, h3))
            return self._fit(m, epochs=20)

        study = optuna.create_study(direction="minimize")
        callbacks = [callback] if callback is not None else []
        study.optimize(objective, n_trials=n_trials, callbacks=callbacks)

        best = study.best_params
        self.model = self._build_model((best["h1"], best["h2"], best["h3"]))
        self._fit(self.model, epochs=200)

    def _r2(
        self, x: torch.Tensor, y_true: torch.Tensor
    ) -> dict[str, float]:
        self.model.eval()
        with torch.no_grad():
            y_pred = self.model(x).numpy()
        y_true_np = y_true.numpy()
        scores = {}
        for i, col in enumerate(_OUTPUT_COLS):
            ss_res = ((y_true_np[:, i] - y_pred[:, i]) ** 2).sum()
            ss_tot = ((y_true_np[:, i] - y_true_np[:, i].mean()) ** 2).sum()
            scores[col] = float(1 - ss_res / ss_tot)
        return scores

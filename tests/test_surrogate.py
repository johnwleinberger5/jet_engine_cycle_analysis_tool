"""Tests for pipeline.surrogate — EngineRegressor class."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

from pipeline.surrogate import EngineRegressor, _INPUT_COLS, _OUTPUT_COLS
from pipeline.lhs_study import LHSDataset


def _make_synthetic_df(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "opr": rng.uniform(10, 40, n),
        "mach": rng.uniform(0.5, 1.7, n),
        "tit_k": rng.uniform(1200, 1800, n),
        "altitude_ft": rng.uniform(20_000, 70_000, n),
        "specific_thrust_n_per_kgs": rng.uniform(100, 800, n),
        "sfc_kg_per_s_per_n": rng.uniform(5e-6, 5e-5, n),
    })


def _make_regressor(tmp_path: Path) -> EngineRegressor:
    """Train a tiny EngineRegressor (1 Optuna trial) on synthetic data."""
    ds = MagicMock(spec=LHSDataset)
    ds.df = _make_synthetic_df()
    with patch("pipeline.surrogate._DEFAULT_MODEL_PATH", tmp_path / "model.pkl"):
        return EngineRegressor(ds, n_optuna_trials=1)


def test_predict_output_shape(tmp_path):
    reg = _make_regressor(tmp_path)
    query = pd.DataFrame({
        "opr": [20.0, 30.0],
        "mach": [1.0, 1.5],
        "tit_k": [1400.0, 1600.0],
        "altitude_ft": [40_000.0, 60_000.0],
    })
    result = reg.predict(query)
    assert result.shape == (2, 2)
    assert list(result.columns) == _OUTPUT_COLS


def test_predict_returns_finite_values(tmp_path):
    reg = _make_regressor(tmp_path)
    query = pd.DataFrame({
        "opr": [25.0], "mach": [1.2],
        "tit_k": [1600.0], "altitude_ft": [60_000.0],
    })
    result = reg.predict(query)
    assert np.isfinite(result.values).all()


def test_r2_train_keys(tmp_path):
    reg = _make_regressor(tmp_path)
    scores = reg.r2_train()
    assert set(scores.keys()) == set(_OUTPUT_COLS)


def test_r2_test_keys(tmp_path):
    reg = _make_regressor(tmp_path)
    scores = reg.r2_test()
    assert set(scores.keys()) == set(_OUTPUT_COLS)


def test_r2_values_are_floats(tmp_path):
    reg = _make_regressor(tmp_path)
    for v in reg.r2_test().values():
        assert isinstance(v, float)


def test_saves_pkl(tmp_path):
    _make_regressor(tmp_path)
    assert (tmp_path / "model.pkl").exists()


def test_load_from_pkl_roundtrip(tmp_path):
    reg = _make_regressor(tmp_path)
    pkl_path = tmp_path / "model.pkl"
    reg2 = EngineRegressor(pkl_path)
    query = pd.DataFrame({
        "opr": [20.0], "mach": [1.0],
        "tit_k": [1400.0], "altitude_ft": [50_000.0],
    })
    pd.testing.assert_frame_equal(reg.predict(query), reg2.predict(query))


def test_invalid_source_raises(tmp_path):
    with pytest.raises(TypeError):
        EngineRegressor(42)


def test_missing_pkl_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        EngineRegressor(tmp_path / "nonexistent.pkl")

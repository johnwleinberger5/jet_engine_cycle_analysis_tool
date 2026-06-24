"""Tests for pipeline.lhs_study — LHSDataset class."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from pipeline.lhs_study import LHSDataset, _COLUMNS
from pipeline.solver_interface import SolverResult

_MOCK_RESULT = SolverResult(
    specific_thrust_n_per_kgs=500.0,
    sfc_kg_per_s_per_n=1.5e-5,
    t0_stations_k=[216.65] * 6,
    p0_stations_pa=[5000.0] * 6,
)


def _make_dataset(tmp_path: Path, n: int = 8) -> LHSDataset:
    """Generate a small LHSDataset with the solver mocked out."""
    with patch("pipeline.lhs_study.run_solver", return_value=_MOCK_RESULT), \
         patch("pipeline.lhs_study._DEFAULT_DATASET_PATH", tmp_path / "lhs.pkl"):
        return LHSDataset(n)


def test_generate_returns_correct_columns(tmp_path):
    ds = _make_dataset(tmp_path)
    assert list(ds.df.columns) == _COLUMNS


def test_generate_correct_row_count(tmp_path):
    ds = _make_dataset(tmp_path, n=16)
    assert len(ds.df) == 16


def test_generate_saves_pkl(tmp_path):
    _make_dataset(tmp_path)
    assert (tmp_path / "lhs.pkl").exists()


def test_load_from_pkl_roundtrip(tmp_path):
    ds = _make_dataset(tmp_path)
    pkl_path = tmp_path / "lhs.pkl"
    ds2 = LHSDataset(pkl_path)
    pd.testing.assert_frame_equal(ds.df, ds2.df)


def test_bounds_respected(tmp_path):
    from pipeline import constants
    ds = _make_dataset(tmp_path, n=50)
    assert ds.df["opr"].between(constants.LHS_OPR_MIN, constants.LHS_OPR_MAX).all()
    assert ds.df["mach"].between(constants.LHS_MACH_MIN, constants.LHS_MACH_MAX).all()
    assert ds.df["tit_k"].between(constants.LHS_TIT_MIN, constants.LHS_TIT_MAX).all()
    assert ds.df["altitude_ft"].between(constants.LHS_ALT_MIN, constants.LHS_ALT_MAX).all()


def test_invalid_source_type_raises():
    with pytest.raises(TypeError):
        LHSDataset(3.14)


def test_missing_pkl_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        LHSDataset(tmp_path / "nonexistent.pkl")

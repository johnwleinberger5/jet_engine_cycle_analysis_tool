"""Tests for pipeline.trade_study — OPR x Mach grid sweep."""

from unittest.mock import patch

import numpy as np
import pytest

from pipeline.solver_interface import SolverResult
from pipeline.trade_study import run_trade_study, TradeStudyResults


# ---------------------------------------------------------------------------
# Mock run_solver — returns physically plausible values that vary with inputs
# ---------------------------------------------------------------------------

def _mock_run_solver(mach, opr, tit_k=1600.0, altitude_ft=60_000.0,
                     solver_path=None):
    return SolverResult(
        specific_thrust_n_per_kgs=max(10.0, 300.0 * mach + 5.0 * opr),
        sfc_kg_per_s_per_n=max(1e-6, 3e-5 / (mach * opr ** 0.1)),
        t0_stations_k=[216.65, 216.65, 600.0, 1600.0, 1100.0, 1100.0],
        p0_stations_pa=[7170.0, 6500.0, 162750.0, 162750.0, 11500.0, 11500.0],
    )


PATCH_TARGET = "pipeline.trade_study.run_solver"


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_trade_study_results(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(n_mach=3, n_opr=3)
        assert isinstance(result, TradeStudyResults)


# ---------------------------------------------------------------------------
# Grid shape
# ---------------------------------------------------------------------------

class TestGridShape:
    def test_mach_grid_shape(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(n_mach=4, n_opr=5)
        assert result.mach_grid.shape == (4, 5)

    def test_opr_grid_shape(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(n_mach=4, n_opr=5)
        assert result.opr_grid.shape == (4, 5)

    def test_specific_thrust_shape(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(n_mach=4, n_opr=5)
        assert result.specific_thrust.shape == (4, 5)

    def test_sfc_shape(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(n_mach=4, n_opr=5)
        assert result.sfc.shape == (4, 5)


# ---------------------------------------------------------------------------
# Grid values
# ---------------------------------------------------------------------------

class TestGridValues:
    def test_mach_range(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(mach_range=(0.5, 1.7), n_mach=5, n_opr=3)
        assert result.mach_grid[0, 0] == pytest.approx(0.5)
        assert result.mach_grid[-1, 0] == pytest.approx(1.7)

    def test_opr_range(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            result = run_trade_study(opr_range=(10.0, 40.0), n_mach=3, n_opr=5)
        assert result.opr_grid[0, 0] == pytest.approx(10.0)
        assert result.opr_grid[0, -1] == pytest.approx(40.0)


# ---------------------------------------------------------------------------
# Physical plausibility
# ---------------------------------------------------------------------------

class TestPhysicalPlausibility:
    @pytest.fixture(autouse=True)
    def results(self):
        with patch(PATCH_TARGET, side_effect=_mock_run_solver):
            self.result = run_trade_study(n_mach=4, n_opr=4)

    def test_specific_thrust_positive(self):
        assert np.all(self.result.specific_thrust > 0.0)

    def test_sfc_positive(self):
        assert np.all(self.result.sfc > 0.0)

    def test_no_nan_in_thrust(self):
        assert not np.any(np.isnan(self.result.specific_thrust))

    def test_no_nan_in_sfc(self):
        assert not np.any(np.isnan(self.result.sfc))

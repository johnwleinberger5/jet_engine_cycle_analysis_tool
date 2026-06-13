"""Regression tests against the real C++ solver binary.

These tests require the solver binary to be present at solver/build/solver.
They are skipped automatically in environments where the binary is absent
(e.g. CI runs that only install Python dependencies).

Once the binary is built for the first time, the expected values below were
verified by hand against the station-by-station equations in CLAUDE.md and
should not be changed without a physics justification.

Operating point under test: Mach 1.7, OPR 25, TIT 1600 K, alt 60,000 ft
"""

import pytest
from pathlib import Path
from pipeline.solver_interface import run_solver


_build = Path(__file__).parent.parent / "solver" / "build"
SOLVER_PATH = next(
    (p for p in [
        _build / "solver",
        _build / "solver.exe",
        _build / "Release" / "solver.exe",
        _build / "Release" / "solver",
    ] if p.exists()),
    _build / "solver",  # fallback for skip check
)

requires_solver = pytest.mark.skipif(
    not SOLVER_PATH.exists(),
    reason="C++ solver binary not found — run bash build_solver.sh to build it",
)

# Reference operating point
MACH    = 1.7
OPR     = 25.0
TIT_K   = 1600.0
ALT_FT  = 60_000.0


@requires_solver
class TestReferenceOperatingPoint:
    @pytest.fixture(scope="class")
    def result(self):
        return run_solver(MACH, OPR, tit_k=TIT_K, altitude_ft=ALT_FT,
                          solver_path=SOLVER_PATH)

    def test_specific_thrust(self, result):
        assert result.specific_thrust_n_per_kgs == pytest.approx(561.5582628478878, rel=1e-4)

    def test_sfc(self, result):
        assert result.sfc_kg_per_s_per_n == pytest.approx(2.8255016994940187e-05, rel=1e-4)

    def test_six_stations(self, result):
        assert len(result.t0_stations_k) == 6
        assert len(result.p0_stations_pa) == 6

    def test_t0_stations(self, result):
        expected = [341.8737, 341.8737, 927.9091495065514, 1600.0, 1013.9645504934485, 1013.9645504934485]
        assert result.t0_stations_k == pytest.approx(expected, rel=1e-4)

    def test_p0_stations(self, result):
        expected = [35398.16355546892, 30290.954713146763, 757273.867828669, 757273.867828669, 121625.23648519936, 121625.23648519936]
        assert result.p0_stations_pa == pytest.approx(expected, rel=1e-4)

    def test_shock_reduces_total_pressure_at_inlet(self, result):
        assert result.p0_stations_pa[1] < result.p0_stations_pa[0]

    def test_station_temperatures_all_positive(self, result):
        assert all(t > 0.0 for t in result.t0_stations_k)

    def test_station_pressures_all_positive(self, result):
        assert all(p > 0.0 for p in result.p0_stations_pa)

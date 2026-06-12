"""Tests for pipeline.solver_interface — subprocess wrapper and JSON protocol.

Uses unittest.mock to patch subprocess.run so tests are cross-platform and
do not require any binary to be present or executable.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pipeline.solver_interface import run_solver, SolverResult


@pytest.fixture
def fake_solver(tmp_path) -> Path:
    """Create an empty file so path.exists() passes; subprocess.run is mocked."""
    p = tmp_path / "solver"
    p.touch()
    return p


# ---------------------------------------------------------------------------
# Shared mock output — matches the SolverOutput JSON schema exactly
# ---------------------------------------------------------------------------

MOCK_OUTPUT = {
    "specific_thrust_n_per_kgs": 523.4,
    "sfc_kg_per_s_per_n": 3.21e-5,
    "t0_stations_k": [341.8, 341.8, 812.3, 1600.0, 1142.5, 1142.5],
    "p0_stations_pa": [28540.0, 24430.0, 610750.0, 610750.0, 43280.0, 43280.0],
}


def _make_proc(stdout: str = "", returncode: int = 0) -> MagicMock:
    """Return a mock CompletedProcess with the given stdout and returncode."""
    proc = MagicMock()
    proc.returncode = returncode
    proc.stdout = stdout
    proc.stderr = ""
    return proc


# ---------------------------------------------------------------------------
# Return type and shape
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_solver_result(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(json.dumps(MOCK_OUTPUT))):
            result = run_solver(1.7, 25.0, solver_path=fake_solver)
        assert isinstance(result, SolverResult)

    def test_t0_stations_has_six_elements(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(json.dumps(MOCK_OUTPUT))):
            result = run_solver(1.7, 25.0, solver_path=fake_solver)
        assert len(result.t0_stations_k) == 6

    def test_p0_stations_has_six_elements(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(json.dumps(MOCK_OUTPUT))):
            result = run_solver(1.7, 25.0, solver_path=fake_solver)
        assert len(result.p0_stations_pa) == 6


# ---------------------------------------------------------------------------
# Output values match mock
# ---------------------------------------------------------------------------

class TestOutputValues:
    @pytest.fixture(autouse=True)
    def mock_proc(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(json.dumps(MOCK_OUTPUT))):
            self.result = run_solver(1.7, 25.0, solver_path=fake_solver)

    def test_specific_thrust(self):
        assert self.result.specific_thrust_n_per_kgs == pytest.approx(
            MOCK_OUTPUT["specific_thrust_n_per_kgs"], rel=1e-6
        )

    def test_sfc(self):
        assert self.result.sfc_kg_per_s_per_n == pytest.approx(
            MOCK_OUTPUT["sfc_kg_per_s_per_n"], rel=1e-6
        )

    def test_t0_stations(self):
        assert self.result.t0_stations_k == pytest.approx(
            MOCK_OUTPUT["t0_stations_k"], rel=1e-6
        )

    def test_p0_stations(self):
        assert self.result.p0_stations_pa == pytest.approx(
            MOCK_OUTPUT["p0_stations_pa"], rel=1e-6
        )


# ---------------------------------------------------------------------------
# Input serialisation — verify the JSON sent to the solver is correct
# ---------------------------------------------------------------------------

class TestInputSerialisation:
    def test_inputs_passed_correctly(self, fake_solver):
        """Capture what subprocess.run received and verify the JSON payload."""
        captured = {}

        def capture_call(cmd, **kwargs):
            captured["input"] = kwargs.get("input", "")
            return _make_proc(json.dumps(MOCK_OUTPUT))

        with patch("subprocess.run", side_effect=capture_call):
            run_solver(1.7, 25.0, tit_k=1600.0, altitude_ft=60_000.0,
                       solver_path=fake_solver)

        sent = json.loads(captured["input"])
        assert sent["mach"] == pytest.approx(1.7)
        assert sent["opr"] == pytest.approx(25.0)
        assert sent["tit_k"] == pytest.approx(1600.0)
        assert sent["altitude_ft"] == pytest.approx(60_000.0)


# ---------------------------------------------------------------------------
# Default parameter values
# ---------------------------------------------------------------------------

class TestDefaults:
    def _capture_and_run(self, fake_solver, **kwargs):
        captured = {}

        def capture_call(cmd, **kw):
            captured["input"] = kw.get("input", "")
            return _make_proc(json.dumps(MOCK_OUTPUT))

        with patch("subprocess.run", side_effect=capture_call):
            run_solver(1.7, 25.0, solver_path=fake_solver, **kwargs)

        return json.loads(captured["input"])

    def test_default_tit_is_1600(self, fake_solver):
        sent = self._capture_and_run(fake_solver)
        assert sent["tit_k"] == pytest.approx(1600.0)

    def test_default_altitude_is_60000ft(self, fake_solver):
        sent = self._capture_and_run(fake_solver)
        assert sent["altitude_ft"] == pytest.approx(60_000.0)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_missing_binary_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            run_solver(1.7, 25.0, solver_path=Path("/nonexistent/solver"))

    def test_nonzero_exit_raises_runtime_error(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(returncode=1)):
            with pytest.raises(RuntimeError):
                run_solver(1.7, 25.0, solver_path=fake_solver)

    def test_bad_json_raises_value_error(self, fake_solver):
        with patch("subprocess.run", return_value=_make_proc(stdout="not json")):
            with pytest.raises(ValueError):
                run_solver(1.7, 25.0, solver_path=fake_solver)

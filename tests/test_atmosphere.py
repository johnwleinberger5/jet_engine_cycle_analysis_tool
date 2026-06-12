"""Tests for pipeline.atmosphere — ISA standard atmosphere model."""

import pytest
from pipeline.atmosphere import get_ambient_conditions


# ---------------------------------------------------------------------------
# Known ISA values from published standard atmosphere tables
# ---------------------------------------------------------------------------

class TestSeaLevel:
    def test_pressure(self):
        result = get_ambient_conditions(0.0)
        assert abs(result.pressure_pa - 101325.0) < 1.0

    def test_temperature(self):
        result = get_ambient_conditions(0.0)
        assert abs(result.temperature_k - 288.15) < 0.01

    def test_density(self):
        result = get_ambient_conditions(0.0)
        assert abs(result.density_kg_m3 - 1.225) < 0.001


class TestTroposphere:
    def test_pressure_at_10000ft(self):
        # ISA table: ~69,682 Pa at 10,000 ft
        result = get_ambient_conditions(10_000.0)
        assert abs(result.pressure_pa - 69_682.0) < 200.0

    def test_temperature_at_10000ft(self):
        # ISA: T = 288.15 - 0.0065 * (10000 ft * 0.3048 m/ft) = 268.338 K
        result = get_ambient_conditions(10_000.0)
        assert abs(result.temperature_k - 268.338) < 0.01

    def test_temperature_decreases_with_altitude(self):
        low = get_ambient_conditions(5_000.0)
        high = get_ambient_conditions(30_000.0)
        assert high.temperature_k < low.temperature_k

    def test_pressure_decreases_with_altitude(self):
        low = get_ambient_conditions(5_000.0)
        high = get_ambient_conditions(30_000.0)
        assert high.pressure_pa < low.pressure_pa


class TestStratosphere:
    def test_temperature_isothermal_above_tropopause(self):
        # Above ~36,089 ft (11,000 m) temperature is fixed at 216.65 K
        alt1 = get_ambient_conditions(40_000.0)
        alt2 = get_ambient_conditions(60_000.0)
        assert abs(alt1.temperature_k - 216.65) < 0.1
        assert abs(alt2.temperature_k - 216.65) < 0.1

    def test_pressure_at_60000ft(self):
        # ISA table: ~7,170 Pa at 60,000 ft
        result = get_ambient_conditions(60_000.0)
        assert abs(result.pressure_pa - 7_170.0) < 100.0

    def test_pressure_still_decreases_in_stratosphere(self):
        low = get_ambient_conditions(40_000.0)
        high = get_ambient_conditions(60_000.0)
        assert high.pressure_pa < low.pressure_pa


class TestIdealGasConsistency:
    def test_density_consistent_with_ideal_gas(self):
        """rho = P / (R * T) must hold at every altitude."""
        R_AIR = 287.05
        for alt_ft in [0.0, 10_000.0, 36_000.0, 60_000.0]:
            c = get_ambient_conditions(alt_ft)
            expected_rho = c.pressure_pa / (R_AIR * c.temperature_k)
            assert abs(c.density_kg_m3 - expected_rho) < 1e-6


class TestInputValidation:
    def test_negative_altitude_raises(self):
        with pytest.raises(ValueError):
            get_ambient_conditions(-1.0)

    def test_zero_altitude_valid(self):
        result = get_ambient_conditions(0.0)
        assert result.pressure_pa > 0.0

/**
 * C++ unit tests for the engine cycle solver.
 *
 * Reference operating point for full-cycle tests:
 *   Mach 1.7, OPR 25, TIT 1600 K, altitude 60,000 ft
 * Expected values were captured from a verified solver run and must not be
 * changed without a physics justification.
 */

#include <catch2/catch_test_macros.hpp>
#include <catch2/matchers/catch_matchers_floating_point.hpp>

#include "atmosphere.h"
#include "constants.h"
#include "engine_cycle.h"
#include "thermo_utils.h"

using Catch::Matchers::WithinAbs;
using Catch::Matchers::WithinRel;

// ── ISA Atmosphere ────────────────────────────────────────────────────────────

TEST_CASE("Atmosphere - sea level returns ISA standard values", "[atmosphere]") {
    auto amb = atmosphere::get_ambient_conditions(0.0);
    REQUIRE_THAT(amb.temperature_k,  WithinRel(288.15,   1e-4));
    REQUIRE_THAT(amb.pressure_pa,    WithinRel(101325.0, 1e-4));
    REQUIRE_THAT(amb.density_kg_m3,  WithinRel(1.2250,   1e-3));
}

TEST_CASE("Atmosphere - 60,000 ft is in isothermal stratosphere", "[atmosphere]") {
    auto amb = atmosphere::get_ambient_conditions(60000.0);
    // Temperature is constant throughout the stratosphere at T_TROPOPAUSE
    REQUIRE_THAT(amb.temperature_k, WithinAbs(constants::T_TROPOPAUSE, 1e-6));
    // Pressure from ISA tables; verified against full-cycle solver output
    REQUIRE_THAT(amb.pressure_pa,   WithinRel(7171.4, 1e-3));
    REQUIRE(amb.density_kg_m3 > 0.0);
}

TEST_CASE("Atmosphere - pressure decreases monotonically with altitude", "[atmosphere]") {
    auto sl  = atmosphere::get_ambient_conditions(0.0);
    auto mid = atmosphere::get_ambient_conditions(30000.0);
    auto hi  = atmosphere::get_ambient_conditions(60000.0);
    REQUIRE(sl.pressure_pa > mid.pressure_pa);
    REQUIRE(mid.pressure_pa > hi.pressure_pa);
}

TEST_CASE("Atmosphere - negative altitude throws", "[atmosphere]") {
    REQUIRE_THROWS_AS(atmosphere::get_ambient_conditions(-1.0), std::invalid_argument);
}

// ── Isentropic Relations ──────────────────────────────────────────────────────

TEST_CASE("Thermo - total temperature ratio at M=0 is 1", "[thermo]") {
    REQUIRE_THAT(thermo_utils::total_temperature_ratio(0.0), WithinAbs(1.0, 1e-12));
}

TEST_CASE("Thermo - total temperature ratio at M=1.7", "[thermo]") {
    // T0/T = 1 + (gamma-1)/2 * M^2 = 1 + 0.2 * 2.89 = 1.578
    REQUIRE_THAT(thermo_utils::total_temperature_ratio(1.7), WithinRel(1.578, 1e-6));
}

TEST_CASE("Thermo - total pressure ratio at M=0 is 1", "[thermo]") {
    REQUIRE_THAT(thermo_utils::total_pressure_ratio(0.0), WithinAbs(1.0, 1e-12));
}

TEST_CASE("Thermo - total pressure ratio at M=1.7", "[thermo]") {
    // P0/P = (T0/T)^(gamma/(gamma-1)) = 1.578^3.5 ≈ 4.9360
    REQUIRE_THAT(thermo_utils::total_pressure_ratio(1.7), WithinRel(4.9360, 1e-4));
}

TEST_CASE("Thermo - isentropic temperature from pressure ratio at OPR=25", "[thermo]") {
    // T2/T1 = OPR^((gamma-1)/gamma) = 25^(0.4/1.4) = 25^0.28571 ≈ 2.5085
    REQUIRE_THAT(thermo_utils::isentropic_temperature_from_pressure(25.0), WithinRel(2.5085, 1e-4));
}

// ── Normal Shock ──────────────────────────────────────────────────────────────

TEST_CASE("Shock - subsonic Mach returns recovery of 1", "[shock]") {
    REQUIRE_THAT(thermo_utils::normal_shock_total_pressure_recovery(0.8), WithinAbs(1.0, 1e-12));
    REQUIRE_THAT(thermo_utils::normal_shock_total_pressure_recovery(1.0), WithinAbs(1.0, 1e-12));
}

TEST_CASE("Shock - recovery decreases with increasing Mach", "[shock]") {
    double r17 = thermo_utils::normal_shock_total_pressure_recovery(1.7);
    double r20 = thermo_utils::normal_shock_total_pressure_recovery(2.0);
    REQUIRE(r17 > r20);
    REQUIRE(r17 < 1.0);
    REQUIRE(r20 < 1.0);
}

TEST_CASE("Shock - recovery at M=1.7 matches verified value", "[shock]") {
    // Verified from solver debug log: shock_recovery=0.8557
    REQUIRE_THAT(thermo_utils::normal_shock_total_pressure_recovery(1.7), WithinRel(0.8557, 1e-3));
}

// ── Full Engine Cycle ─────────────────────────────────────────────────────────

// Expected values from verified solver run at Mach 1.7, OPR 25, TIT 1600 K, 60,000 ft.
// Do not change without a physics justification.
static const SolverInput REF_INPUT = {1.7, 25.0, 1600.0, 60000.0};

// Performance values: updated after turbine isentropic efficiency fix.
// T0[4] = T0[3] - compressor_work (power balance; independent of eta_t).
// P0[4] unchanged — computed from isentropic equivalent temperature T0_4s.
// specific_thrust and sfc confirmed from solver run after fix.
static const double EXP_SPECIFIC_THRUST = 561.5582628478878;
static const double EXP_SFC             = 2.8255016994940187e-05;

static const std::array<double, 6> EXP_T0 = {
    341.8737, 341.8737, 927.9091495065514, 1600.0, 1013.9645504934485, 1013.9645504934485
};
static const std::array<double, 6> EXP_P0 = {
    35398.16355546892, 30290.954713146763, 757273.867828669, 757273.867828669,
    121625.23648519936, 121625.23648519936
};

TEST_CASE("Full cycle - specific thrust at reference point", "[cycle]") {
    auto out = EngineCycle(REF_INPUT).run();
    REQUIRE_THAT(out.specific_thrust_n_per_kgs, WithinRel(EXP_SPECIFIC_THRUST, 1e-4));
}

TEST_CASE("Full cycle - SFC at reference point", "[cycle]") {
    auto out = EngineCycle(REF_INPUT).run();
    REQUIRE_THAT(out.sfc_kg_per_s_per_n, WithinRel(EXP_SFC, 1e-4));
}

TEST_CASE("Full cycle - total temperature stations at reference point", "[cycle]") {
    auto out = EngineCycle(REF_INPUT).run();
    for (int i = 0; i < constants::N_STATIONS; ++i)
        REQUIRE_THAT(out.t0_stations_k[i], WithinRel(EXP_T0[i], 1e-4));
}

TEST_CASE("Full cycle - total pressure stations at reference point", "[cycle]") {
    auto out = EngineCycle(REF_INPUT).run();
    for (int i = 0; i < constants::N_STATIONS; ++i)
        REQUIRE_THAT(out.p0_stations_pa[i], WithinRel(EXP_P0[i], 1e-4));
}

TEST_CASE("Full cycle - physical consistency checks", "[cycle]") {
    auto out = EngineCycle(REF_INPUT).run();

    // Shock drops total pressure at inlet
    REQUIRE(out.p0_stations_pa[1] < out.p0_stations_pa[0]);

    // Compressor raises T0 and P0
    REQUIRE(out.t0_stations_k[2]  > out.t0_stations_k[1]);
    REQUIRE(out.p0_stations_pa[2] > out.p0_stations_pa[1]);

    // Combustor raises T0 to TIT, P0 unchanged
    REQUIRE_THAT(out.t0_stations_k[3], WithinAbs(REF_INPUT.tit_k, 1e-6));
    REQUIRE_THAT(out.p0_stations_pa[3], WithinRel(out.p0_stations_pa[2], 1e-9));

    // Turbine drops both T0 and P0
    REQUIRE(out.t0_stations_k[4]  < out.t0_stations_k[3]);
    REQUIRE(out.p0_stations_pa[4] < out.p0_stations_pa[3]);

    // All stations positive
    for (int i = 0; i < constants::N_STATIONS; ++i) {
        REQUIRE(out.t0_stations_k[i]  > 0.0);
        REQUIRE(out.p0_stations_pa[i] > 0.0);
    }

    // Positive performance outputs
    REQUIRE(out.specific_thrust_n_per_kgs > 0.0);
    REQUIRE(out.sfc_kg_per_s_per_n        > 0.0);
}

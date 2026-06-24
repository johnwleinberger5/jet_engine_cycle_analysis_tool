#include "engine_cycle.h"
#include "atmosphere.h"
#include "thermo_utils.h"
#include "constants.h"
#include "error_utils.h"

#include <cmath>
#include <stdexcept>
#include <spdlog/spdlog.h>
#include <spdlog/fmt/fmt.h>

using namespace constants;

EngineCycle::EngineCycle(const SolverInput& input) : input_(input) {
    if (input_.mach <= 0.0)
        log_and_throw<std::invalid_argument>(__FUNCTION__,
            fmt::format("Mach must be > 0, got {:.3f}", input_.mach));
    if (input_.opr <= 1.0)
        log_and_throw<std::invalid_argument>(__FUNCTION__,
            fmt::format("OPR must be > 1, got {:.2f}", input_.opr));
    if (input_.tit_k <= 0.0)
        log_and_throw<std::invalid_argument>(__FUNCTION__,
            fmt::format("TIT must be > 0 K, got {:.2f} K", input_.tit_k));
    if (input_.altitude_ft < 0.0)
        log_and_throw<std::invalid_argument>(__FUNCTION__,
            fmt::format("Altitude must be >= 0 ft, got {:.1f} ft", input_.altitude_ft));
}

SolverOutput EngineCycle::run() {
    spdlog::info("Starting engine cycle solve: Mach={:.3f}, OPR={:.1f}, TIT={:.1f} K, Alt={:.0f} ft",
                 input_.mach, input_.opr, input_.tit_k, input_.altitude_ft);

    calculate_atmosphere();
    calculate_inlet();
    calculate_compressor();
    calculate_combustor();
    calculate_turbine();
    calculate_nozzle();

    double specific_thrust = v_exit_m_s_ - v_inlet_m_s_;
    double sfc             = fuel_air_ratio_ / specific_thrust;

    if (specific_thrust <= 0.0)
        spdlog::warn("Non-positive specific thrust: {:.2f} N/(kg/s) — check inputs", specific_thrust);

    spdlog::info("Cycle complete: specific_thrust={:.2f} N/(kg/s), SFC={:.6f} kg/(s*N)",
                 specific_thrust, sfc);

    return {specific_thrust, sfc, t0_k_, p0_pa_};
}

// Station 0 — freestream total conditions (isentropic ram)
void EngineCycle::calculate_atmosphere() {
    auto amb = atmosphere::get_ambient_conditions(input_.altitude_ft);
    t_ambient_k_  = amb.temperature_k;
    p_ambient_pa_ = amb.pressure_pa;

    t0_k_[0]  = t_ambient_k_  * thermo_utils::total_temperature_ratio(input_.mach);
    p0_pa_[0] = p_ambient_pa_ * thermo_utils::total_pressure_ratio(input_.mach);

    v_inlet_m_s_ = input_.mach * thermo_utils::speed_of_sound(t_ambient_k_);

    spdlog::debug("[{}] Station 0 (freestream): T_amb={:.2f} K, P_amb={:.1f} Pa, "
                  "T0={:.2f} K, P0={:.1f} Pa, V_inlet={:.2f} m/s",
                  __FUNCTION__, t_ambient_k_, p_ambient_pa_,
                  t0_k_[0], p0_pa_[0], v_inlet_m_s_);
}

// Station 1 — inlet exit — Rayleigh Pitot normal shock total pressure recovery
// T0 is conserved across an adiabatic shock
void EngineCycle::calculate_inlet() {
    double recovery = thermo_utils::normal_shock_total_pressure_recovery(input_.mach);

    t0_k_[1]  = t0_k_[0];
    p0_pa_[1] = p0_pa_[0] * recovery;

    spdlog::debug("[{}] Station 1 (inlet exit): shock_recovery={:.4f}, "
                  "T0={:.2f} K, P0={:.1f} Pa",
                  __FUNCTION__, recovery, t0_k_[1], p0_pa_[1]);

    if (input_.mach > 1.0)
        spdlog::debug("[{}] Supersonic inlet — normal shock applied at M={:.3f}",
                      __FUNCTION__, input_.mach);
}

// Station 2 — compressor exit — isentropic compression with isentropic efficiency eta_c
// T0_exit = T0_inlet * (1 + (OPR^((gamma-1)/gamma) - 1) / eta_c)
// P0_exit = P0_inlet * OPR
void EngineCycle::calculate_compressor() {
    double ideal_temp_ratio = thermo_utils::isentropic_temperature_from_pressure(input_.opr);
    t0_k_[2]  = t0_k_[1] * (1.0 + (ideal_temp_ratio - 1.0) / ETA_C);
    p0_pa_[2] = p0_pa_[1] * input_.opr;

    spdlog::debug("[{}] Station 2 (compressor exit): ideal_temp_ratio={:.4f}, "
                  "T0={:.2f} K, P0={:.1f} Pa",
                  __FUNCTION__, ideal_temp_ratio, t0_k_[2], p0_pa_[2]);
}

// Station 3 — combustor exit (turbine inlet) — fixed TIT, energy balance for fuel/air ratio
// mdot_f/mdot_a = cp * (TIT - T0_compressor) / (eta_b * LHV)
// Combustor pressure drop neglected (P0_exit = P0_inlet)
void EngineCycle::calculate_combustor() {
    t0_k_[3]  = input_.tit_k;
    p0_pa_[3] = p0_pa_[2];

    fuel_air_ratio_ = CP * (input_.tit_k - t0_k_[2]) / (ETA_B * LHV);

    if (fuel_air_ratio_ < 0.0)
        log_and_throw(__FUNCTION__, fmt::format(
            "Negative fuel-air ratio ({:.6f}) — TIT ({:.2f} K) is below compressor exit temperature ({:.2f} K)",
            fuel_air_ratio_, input_.tit_k, t0_k_[2]));

    spdlog::debug("[{}] Station 3 (combustor exit / TIT): T0={:.2f} K, P0={:.1f} Pa, "
                  "fuel_air_ratio={:.6f}",
                  __FUNCTION__, t0_k_[3], p0_pa_[3], fuel_air_ratio_);
}

// Station 4 — turbine exit — power balance with isentropic efficiency eta_t
// eta_t is turbine isentropic efficiency: actual_work = eta_t * ideal_work
// Power balance (neglecting fuel mass fraction): cp*(T0[3]-T0[4]) = cp*(T0[2]-T0[1])
//   => T0_exit = TIT - (T0_compressor_exit - T0_inlet)  [independent of eta_t]
// Isentropic equivalent exit temperature (more pressure drop due to irreversibility):
//   T0_4s = TIT - (T0_compressor_exit - T0_inlet) / eta_t
// P0_exit = P0_inlet * (T0_4s / TIT)^(gamma/(gamma-1))
void EngineCycle::calculate_turbine() {
    double compressor_work = t0_k_[2] - t0_k_[1];
    t0_k_[4] = input_.tit_k - compressor_work;

    double t0_4s = input_.tit_k - compressor_work / ETA_T;
    double isentropic_temp_ratio = t0_4s / t0_k_[3];
    p0_pa_[4] = p0_pa_[3] * std::pow(isentropic_temp_ratio, GAMMA / (GAMMA - 1.0));

    if (t0_k_[4] <= 0.0)
        log_and_throw(__FUNCTION__, fmt::format(
            "Non-positive turbine exit temperature ({:.2f} K) — cycle is non-physical",
            t0_k_[4]));

    spdlog::debug("[{}] Station 4 (turbine exit): compressor_work={:.2f} K, "
                  "T0_4s={:.2f} K, T0={:.2f} K, P0={:.1f} Pa",
                  __FUNCTION__, compressor_work, t0_4s, t0_k_[4], p0_pa_[4]);
}

// Station 5 — nozzle exit — isentropic expansion to ambient pressure
// T_exit = T0_turbine * (P_amb / P0_turbine)^((gamma-1)/gamma)
// V_exit = sqrt(2 * cp * (T0_turbine - T_exit))   [from stagnation enthalpy drop]
void EngineCycle::calculate_nozzle() {
    double nozzle_pressure_ratio = p_ambient_pa_ / p0_pa_[4];
    double t_exit_k = t0_k_[4] * thermo_utils::isentropic_temperature_from_pressure(nozzle_pressure_ratio);

    v_exit_m_s_ = std::sqrt(2.0 * CP * (t0_k_[4] - t_exit_k));

    // Nozzle exit total conditions — fully expanded to ambient, so P0 = P0_turbine
    t0_k_[5]  = t0_k_[4];
    p0_pa_[5] = p0_pa_[4];

    spdlog::debug("[{}] Station 5 (nozzle exit): nozzle_PR={:.4f}, T_exit={:.2f} K, "
                  "V_exit={:.2f} m/s",
                  __FUNCTION__, nozzle_pressure_ratio, t_exit_k, v_exit_m_s_);
}

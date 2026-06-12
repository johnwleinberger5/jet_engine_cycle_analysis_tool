#pragma once

#include "constants.h"
#include <cmath>
#include <stdexcept>

namespace thermo_utils {

// Isentropic total-to-static temperature ratio: T0/T = 1 + (gamma-1)/2 * M^2
inline double total_temperature_ratio(double mach,
                                      double gamma = constants::GAMMA) {
    return 1.0 + (gamma - 1.0) / 2.0 * mach * mach;
}

// Isentropic total-to-static pressure ratio: P0/P = (T0/T)^(gamma/(gamma-1))
inline double total_pressure_ratio(double mach,
                                   double gamma = constants::GAMMA) {
    double t_ratio = total_temperature_ratio(mach, gamma);
    return std::pow(t_ratio, gamma / (gamma - 1.0));
}

// Isentropic temperature ratio across a pressure ratio: T2/T1 = (P2/P1)^((gamma-1)/gamma)
inline double isentropic_temperature_from_pressure(double pressure_ratio,
                                                   double gamma = constants::GAMMA) {
    return std::pow(pressure_ratio, (gamma - 1.0) / gamma);
}

// Rayleigh Pitot formula — normal shock total pressure recovery
// P0_exit/P0_inlet = f(M, gamma), exact closed-form solution
// Valid for M >= 1; returns 1.0 for M < 1 (no shock)
inline double normal_shock_total_pressure_recovery(double mach,
                                                   double gamma = constants::GAMMA) {
    if (mach <= 1.0) return 1.0;

    // Term 1: isentropic compression to the shock from supersonic side
    double term1 = std::pow(
        ((gamma + 1.0) / 2.0 * mach * mach) /
        (1.0 + (gamma - 1.0) / 2.0 * mach * mach),
        gamma / (gamma - 1.0)
    );

    // Term 2: entropy rise across the shock
    double term2 = std::pow(
        (gamma + 1.0) / (2.0 * gamma * mach * mach - (gamma - 1.0)),
        1.0 / (gamma - 1.0)
    );

    return term1 * term2;
}

// Speed of sound: a = sqrt(gamma * R * T)
inline double speed_of_sound(double t_static,
                              double gamma = constants::GAMMA,
                              double r     = constants::R_AIR) {
    return std::sqrt(gamma * r * t_static);
}

} // namespace thermo_utils

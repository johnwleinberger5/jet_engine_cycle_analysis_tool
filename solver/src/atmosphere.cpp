#include "atmosphere.h"
#include "constants.h"
#include "error_utils.h"
#include <cmath>
#include <stdexcept>
#include <spdlog/spdlog.h>
#include <spdlog/fmt/fmt.h>

namespace atmosphere {

// ISA standard atmosphere
// Troposphere  (0 - 11 000 m): T decreases at 6.5 K/km, P by hydrostatic integral
// Stratosphere (11 000 - 20 000 m): isothermal at 216.65 K
AmbientConditions get_ambient_conditions(double altitude_ft) {
    using namespace constants;

    if (altitude_ft < 0.0)
        log_and_throw<std::invalid_argument>(__FUNCTION__,
            fmt::format("Altitude must be >= 0 ft, got {:.1f} ft", altitude_ft));

    double alt_m = altitude_ft * FT_TO_M;

    double t_k, p_pa;

    if (alt_m <= TROPOPAUSE_M) {
        // Troposphere — linear temperature lapse (ISA)
        t_k = T_SEA_LEVEL - LAPSE_RATE * alt_m;
        double exp = G / (R_AIR * LAPSE_RATE);
        p_pa = P_SEA_LEVEL * std::pow(t_k / T_SEA_LEVEL, exp);
    } else {
        // Stratosphere — isothermal layer
        t_k = T_TROPOPAUSE;
        double p_tropo = P_SEA_LEVEL *
                         std::pow(T_TROPOPAUSE / T_SEA_LEVEL,
                                  G / (R_AIR * LAPSE_RATE));
        p_pa = p_tropo * std::exp(-G * (alt_m - TROPOPAUSE_M) / (R_AIR * T_TROPOPAUSE));
    }

    double rho = p_pa / (R_AIR * t_k);
    return {p_pa, t_k, rho};
}

} // namespace atmosphere

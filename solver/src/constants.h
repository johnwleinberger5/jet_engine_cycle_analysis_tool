#pragma once

namespace constants {

// Thermodynamic
constexpr double GAMMA        = 1.4;          // ratio of specific heats (calorically perfect air)
constexpr double CP           = 1005.0;       // J/(kg·K), specific heat at constant pressure
constexpr double R_AIR        = 287.05;       // J/(kg·K), specific gas constant for air

// Engine model — fixed per CLAUDE.md
constexpr double ETA_C        = 0.88;         // compressor isentropic efficiency
constexpr double ETA_T        = 0.90;         // turbine isentropic efficiency
constexpr double ETA_B        = 0.99;         // combustor efficiency
constexpr double LHV          = 43.0e6;       // J/kg, lower heating value (Jet-A)
constexpr double TIT_K        = 1600.0;       // K, turbine inlet temperature (default)

// Atmosphere model
constexpr double ALT_FT       = 60000.0;      // ft, default cruise altitude

// Standard sea-level atmosphere (ISA)
constexpr double P_SEA_LEVEL  = 101325.0;     // Pa
constexpr double T_SEA_LEVEL  = 288.15;       // K
constexpr double LAPSE_RATE   = 0.0065;       // K/m, troposphere
constexpr double TROPOPAUSE_M = 11000.0;      // m, tropopause altitude
constexpr double T_TROPOPAUSE = 216.65;       // K
constexpr double G            = 9.80665;      // m/s²
constexpr double FT_TO_M      = 0.3048;

// Number of thermodynamic stations
constexpr int N_STATIONS = 6;

} // namespace constants

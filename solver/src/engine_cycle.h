#pragma once

#include "constants.h"
#include <array>

struct SolverInput {
    double mach;
    double opr;
    double tit_k;
    double altitude_ft;
};

struct SolverOutput {
    double specific_thrust_n_per_kgs;
    double sfc_kg_per_s_per_n;
    std::array<double, constants::N_STATIONS> t0_stations_k;
    std::array<double, constants::N_STATIONS> p0_stations_pa;
};

class EngineCycle {
public:
    explicit EngineCycle(const SolverInput& input);

    SolverOutput run();

private:
    SolverInput input_;

    // Per-station calculation methods — stations 0-5:
    // [freestream, inlet exit, compressor exit, combustor exit, turbine exit, nozzle exit]
    void calculate_atmosphere();
    void calculate_inlet();
    void calculate_compressor();
    void calculate_combustor();
    void calculate_turbine();
    void calculate_nozzle();

    // Station state arrays — indexed 0-5
    std::array<double, constants::N_STATIONS> t0_k_{};
    std::array<double, constants::N_STATIONS> p0_pa_{};

    // Derived quantities set during the solve
    double t_ambient_k_    = 0.0;
    double p_ambient_pa_   = 0.0;
    double v_inlet_m_s_    = 0.0;
    double v_exit_m_s_     = 0.0;
    double fuel_air_ratio_ = 0.0;
};

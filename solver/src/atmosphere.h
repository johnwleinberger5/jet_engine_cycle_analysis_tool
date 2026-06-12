#pragma once

namespace atmosphere {

struct AmbientConditions {
    double pressure_pa;     // static pressure [Pa]
    double temperature_k;   // static temperature [K]
    double density_kg_m3;   // density [kg/m^3]
};

// ISA standard atmosphere — valid from sea level through stratosphere
// altitude_ft: geometric altitude in feet
AmbientConditions get_ambient_conditions(double altitude_ft);

} // namespace atmosphere

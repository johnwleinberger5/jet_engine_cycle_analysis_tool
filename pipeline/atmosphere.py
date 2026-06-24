"""ISA standard atmosphere model.

Covers the troposphere (0-11,000 m) with a linear temperature lapse and
the lower stratosphere (11,000-20,000 m) isothermal layer. Valid from sea
level through the stratosphere — sufficient for the 60,000 ft cruise altitude
used in the trade study.
"""

import math
from dataclasses import dataclass
from pipeline import constants


@dataclass
class AmbientConditions:
    """Static atmospheric conditions at a given altitude.

    Attributes:
        pressure_pa: Static pressure in Pascals.
        temperature_k: Static temperature in Kelvin.
        density_kg_m3: Air density in kg/m³.
    """
    pressure_pa: float
    temperature_k: float
    density_kg_m3: float


def get_ambient_conditions(altitude_ft: float) -> AmbientConditions:
    """Return ISA standard atmosphere conditions at the given altitude.

    Uses the linear lapse rate in the troposphere and the isothermal layer
    in the stratosphere. Density is derived from the ideal gas law.

    Args:
        altitude_ft: Geometric altitude in feet. Must be >= 0.

    Returns:
        AmbientConditions with static pressure, temperature, and density.

    Raises:
        ValueError: If altitude_ft < 0.
    """
    if altitude_ft < 0.0:
        raise ValueError(f"Altitude must be >= 0 ft, got {altitude_ft:.1f} ft")

    alt_m = altitude_ft * constants.FT_TO_M

    if alt_m <= constants.TROPOPAUSE_M:
        # Troposphere — linear temperature lapse (ISA)
        t_k = constants.T_SEA_LEVEL - constants.LAPSE_RATE * alt_m
        exponent = constants.G / (constants.R_AIR * constants.LAPSE_RATE)
        p_pa = constants.P_SEA_LEVEL * (t_k / constants.T_SEA_LEVEL) ** exponent
    else:
        # Stratosphere — isothermal layer
        t_k = constants.T_TROPOPAUSE
        p_tropo = constants.P_SEA_LEVEL * (
            constants.T_TROPOPAUSE / constants.T_SEA_LEVEL
        ) ** (constants.G / (constants.R_AIR * constants.LAPSE_RATE))
        p_pa = p_tropo * math.exp(
            -constants.G
            * (alt_m - constants.TROPOPAUSE_M)
            / (constants.R_AIR * constants.T_TROPOPAUSE)
        )

    rho = p_pa / (constants.R_AIR * t_k)
    return AmbientConditions(pressure_pa=p_pa, temperature_k=t_k, density_kg_m3=rho)

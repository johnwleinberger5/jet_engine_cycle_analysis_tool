"""Physical and model constants for the engine cycle analysis.

All values are fixed for the base trade study per the model specification.
No magic numbers should appear elsewhere in the pipeline — import from here.
"""

# Thermodynamic
GAMMA: float = 1.4        # ratio of specific heats, calorically perfect air
CP: float = 1005.0        # J/(kg·K), specific heat at constant pressure
R_AIR: float = 287.05     # J/(kg·K), specific gas constant for air

# Engine model
ETA_C: float = 0.88       # compressor isentropic efficiency
ETA_T: float = 0.90       # turbine isentropic efficiency
ETA_B: float = 0.99       # combustor efficiency
LHV: float = 43.0e6       # J/kg, lower heating value (Jet-A)
TIT_K: float = 1600.0     # K, turbine inlet temperature

# Mission
ALT_FT: float = 60_000.0  # ft, cruise altitude

# ISA standard atmosphere — sea level
P_SEA_LEVEL: float = 101_325.0   # Pa
T_SEA_LEVEL: float = 288.15      # K
LAPSE_RATE: float = 0.0065       # K/m, tropospheric temperature lapse rate
TROPOPAUSE_M: float = 11_000.0   # m, tropopause altitude
T_TROPOPAUSE: float = 216.65     # K, isothermal stratosphere temperature
G: float = 9.80665               # m/s², gravitational acceleration
FT_TO_M: float = 0.3048          # feet to metres conversion

# Trade study sweep bounds (default)
MACH_MIN: float = 0.5
MACH_MAX: float = 1.7
OPR_MIN: float = 10.0
OPR_MAX: float = 40.0
N_MACH: int = 26
N_OPR: int = 30

# Symphony-like reference operating point
SYMPHONY_MACH: float = 1.7
SYMPHONY_OPR: float = 25.0

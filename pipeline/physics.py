# MAINTAINER NOTE — ACRONYM CONVENTION
# Every acronym in this docstring uses the pattern:
#   <a href="acronyms.html#ID"><abbr title="Full Name">ACRONYM</abbr></a>
# When adding or editing content, follow this convention for all acronyms.
# Full reference: pipeline/acronyms.py
"""
# Physics, Equations & Assumptions

This page documents the physical model underlying the engine cycle solver —
what is computed at each station, what is assumed, and where the model
intentionally departs from higher-fidelity practice.

---

## Station Diagram

<p align="center">
  <img src="../assets/jet_engine_cross_section.svg" width="680"
       alt="Jet engine station diagram — freestream through nozzle exit"/>
</p>

Six stations are tracked through the cycle:

| Station | Location |
|---|---|
| 0 | Freestream (far upstream) |
| 1 | Inlet exit (post-shock) |
| 2 | Compressor exit |
| 3 | Combustor exit / turbine inlet |
| 4 | Turbine exit |
| 5 | Nozzle exit |

---

## Station-by-Station Equations

### Station 0 — Freestream (isentropic ram)

Ambient conditions set by the
<a href="acronyms.html#ISA"><abbr title="International Standard Atmosphere">ISA</abbr></a>
model at 60,000 ft. Total conditions from isentropic ram compression:

```
T0[0] = T_amb × (1 + (gamma-1)/2 × M²)
P0[0] = P_amb × (T0[0] / T_amb)^(gamma/(gamma-1))
V_inlet = M × sqrt(gamma × R × T_amb)
```

### Station 1 — Inlet exit (normal shock)

Total temperature is conserved across an adiabatic shock.
Total pressure recovery uses the Rayleigh Pitot formula (exact closed form):

```
T0[1] = T0[0]
P0[1] = P0[0] × recovery(M, gamma)

recovery = [((gamma+1)/2 × M²) / (1 + (gamma-1)/2 × M²)]^(gamma/(gamma-1))
         × [(gamma+1) / (2×gamma×M² - (gamma-1))]^(1/(gamma-1))
```

For subsonic Mach, recovery = 1.0 (no shock).

### Station 2 — Compressor exit (isentropic efficiency
<a href="acronyms.html#eta_c"><abbr title="Compressor isentropic efficiency">eta_c</abbr></a>)

```
T0[2] = T0[1] × (1 + (OPR^((gamma-1)/gamma) - 1) / eta_c)
P0[2] = P0[1] × OPR
```

### Station 3 — Combustor exit / turbine inlet

<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
is fixed. Fuel-air ratio from energy balance (combustor pressure drop neglected):

```
T0[3] = TIT  (fixed at 1600 K)
P0[3] = P0[2]
f = cp × (TIT - T0[2]) / (eta_b × LHV)    where f = mdot_f / mdot_a
```

### Station 4 — Turbine exit (isentropic efficiency
<a href="acronyms.html#eta_t"><abbr title="Turbine isentropic efficiency">eta_t</abbr></a>)

Power balance (fuel mass fraction neglected, ~1.6% error):

```
T0[4] = TIT - (T0[2] - T0[1])              (actual exit temperature)
T0_4s = TIT - (T0[2] - T0[1]) / eta_t     (isentropic equivalent)
P0[4] = P0[3] × (T0_4s / TIT)^(gamma/(gamma-1))
```

`T0[4]` is set by energy conservation and is independent of `eta_t`.
`eta_t` determines how much pressure drop the turbine requires to deliver that work —
a less efficient turbine needs a larger pressure drop to produce the same shaft work,
leaving less pressure available for nozzle expansion.

### Station 5 — Nozzle exit (isentropic expansion to ambient)

```
T_exit = T0[4] × (P_amb / P0[4])^((gamma-1)/gamma)
V_exit = sqrt(2 × cp × (T0[4] - T_exit))
T0[5]  = T0[4]   (adiabatic nozzle preserves total temperature)
P0[5]  = P0[4]   (isentropic nozzle preserves total pressure)
```

### Performance Outputs

```
Specific thrust = V_exit - V_inlet           [N/(kg/s)]
SFC             = f / (V_exit - V_inlet)     [kg/(N·s)]
```

---

## Fixed Parameters

| Parameter | Value | Description |
|---|---|---|
| Altitude | 60,000 ft | Fixed cruise altitude — sets ISA ambient P and T |
| <a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a> | 1600 K | Fixed turbine inlet temperature |
| Bypass ratio | 0 | Pure turbojet — no fan or bypass stream |
| <a href="acronyms.html#gamma"><abbr title="Ratio of specific heats">gamma</abbr></a> | 1.4 | Calorically perfect air |
| <a href="acronyms.html#cp"><abbr title="Specific heat at constant pressure">cp</abbr></a> | 1005 J/(kg·K) | Specific heat at constant pressure |
| R | 287.05 J/(kg·K) | Specific gas constant for air |
| <a href="acronyms.html#eta_c"><abbr title="Compressor isentropic efficiency">eta_c</abbr></a> | 0.88 | Compressor isentropic efficiency |
| <a href="acronyms.html#eta_t"><abbr title="Turbine isentropic efficiency">eta_t</abbr></a> | 0.90 | Turbine isentropic efficiency |
| <a href="acronyms.html#eta_b"><abbr title="Combustor efficiency">eta_b</abbr></a> | 0.99 | Combustor efficiency |
| <a href="acronyms.html#LHV"><abbr title="Lower Heating Value">LHV</abbr></a> | 43 MJ/kg | Jet-A lower heating value |

---

## Model Assumptions & Limitations

- **Calorically perfect gas** — gamma and cp are constant. Real gas properties vary
  significantly with temperature above ~1000 K (NASA-7 polynomials would capture this).
- **Fixed
  <a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>**
  — real engines vary TIT with throttle setting and altitude.
- **Zero bypass ratio** — Symphony is a turbofan; bypass ratio is a key design variable
  omitted here for simplicity.
- **Normal shock inlet** — at Mach 1.7 a normal shock gives ~86% total pressure recovery.
  Real supersonic inlets use oblique shock trains to achieve 95–98%.
- **Zero combustor pressure drop** — real combustors drop ~3–5% of total pressure.
- **Fuel mass fraction neglected** — the fuel-air ratio (~0.016) introduces a ~1.6% error
  in the power balance and thrust calculation.
- **Steady, 1D, single operating point** — no off-design analysis, no transients,
  no thermal soaking, no bleed air or cooling flows.

---

## What Higher Fidelity Would Add

**Level 1 — Enhanced cycle model:**
Variable
<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
sweep, turbofan bypass ratio, real gas properties (NASA-7 polynomials), oblique shock
inlet model, combustor pressure drop.

**Level 2 — Component-level fidelity:**
1D meanline turbomachinery (stage-by-stage), CFD for individual components,
cooling flow modelling, full mission analysis across climb, cruise, and descent.
"""

# This module exists solely as a documentation page rendered by pdoc.
# It contains no executable code.
_DOCS_ONLY = True

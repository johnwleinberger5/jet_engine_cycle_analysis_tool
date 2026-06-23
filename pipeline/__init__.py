# MAINTAINER NOTE — ACRONYM CONVENTION
# Every acronym in this docstring uses the pattern:
#   <a href="pipeline/acronyms.html#ID"><abbr title="Full Name">ACRONYM</abbr></a>
# When adding or editing documentation, follow this convention for all acronyms.
# Full reference: pipeline/acronyms.py
# LLM maintainers: apply this convention when generating or editing any docstring
# in this package.
"""
# Jet Engine Cycle Analysis Tool

<p style="color:#888; font-size:0.9em;">John Leinberger &middot; 2026</p>

A physics-based 1D Brayton cycle simulator demonstrating end-to-end production software
engineering: a compiled C++ solver orchestrated by Python, containerised with Docker,
and validated by a full
<a href="pipeline/acronyms.html#CICD"><abbr title="Continuous Integration / Continuous Deployment">CI/CD</abbr></a>
pipeline on every push.

<p><strong>The emphasis is on production software engineering practices — the physics are
representative but intentionally simplified.</strong></p>

<p><em><a href="pipeline/changelog.html">Version history &amp; roadmap &rarr;</a></em></p>

---

<p align="center">
  <img src="assets/jet_engine_cross_section.svg" width="680"
       alt="Jet engine station diagram — freestream through nozzle exit"/>
</p>

<p align="center">
  <em><a href="pipeline/physics.html">Physics, equations, assumptions &amp; model limitations &rarr;</a></em>
</p>

---

## Trade Study Results

Sweep of
<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
(10–40) against Mach number (0.5–1.7) at fixed
<a href="pipeline/acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
= 1600 K and altitude = 60,000 ft.
The &#9733; marks a Symphony-like operating point
(<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
&#8776; 25, Mach 1.7) — illustrative only, not derived from proprietary data.

<img src="specific_thrust.png" width="84%" alt="Specific Thrust [N/(kg/s)] over OPR × Mach sweep"/>

Specific thrust decreases with Mach. Normal shock losses reduce
<a href="pipeline/acronyms.html#P0"><abbr title="Total (stagnation) pressure">P0</abbr></a>
at the inlet, and compressor work scales with
<a href="pipeline/acronyms.html#T0"><abbr title="Total (stagnation) temperature">T0</abbr></a>[1]
— both reduce turbine exit enthalpy and nozzle expansion pressure while
<a href="pipeline/acronyms.html#V_inlet"><abbr title="Inlet freestream velocity">V_inlet</abbr></a>
grows. Specific thrust peaks near
<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
= 20 — below this, nozzle pressure ratio is insufficient; above it, excess compressor
work depletes turbine exit enthalpy.

<img src="sfc.png" width="84%" alt="SFC [mg/(s·N)] over OPR × Mach sweep"/>

<a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
worsens with Mach — specific thrust falls faster than fuel consumption as shock losses
mount. It improves strongly with
<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>:
higher cycle pressure ratio raises thermal efficiency and the fuel reduction dominates
throughout the sweep.

---

## Key Takeaways

- <strong>Specific thrust decreases with Mach.</strong> Normal shock losses and compressor
  work scaling with inlet
  <a href="pipeline/acronyms.html#T0"><abbr title="Total (stagnation) temperature">T0</abbr></a>
  both reduce
  <a href="pipeline/acronyms.html#V_exit"><abbr title="Nozzle exit velocity">V_exit</abbr></a>
  while
  <a href="pipeline/acronyms.html#V_inlet"><abbr title="Inlet freestream velocity">V_inlet</abbr></a>
  grows — net specific thrust falls across the sweep.

- <strong>Specific thrust peaks at intermediate
  <a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
  (~20).</strong> Too low leaves nozzle pressure unrealised; too high depletes turbine
  exit enthalpy through excess compressor work.

- <strong>
  <a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
  improves strongly with
  <a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
  and worsens with Mach.</strong> OPR drives thermal efficiency; at high Mach, specific
  thrust drops faster than fuel consumption.

- <strong>The Symphony-like point (OPR 25, Mach 1.7) sits in the low specific thrust,
  moderate
  <a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
  region of this model.</strong> Real performance differs substantially — oblique shock
  inlets and turbofan bypass ratio are not captured here.

---

## Modules

| Module | Purpose |
|---|---|
| [`atmosphere`][pipeline.atmosphere] | <a href="pipeline/acronyms.html#ISA"><abbr title="International Standard Atmosphere">ISA</abbr></a> standard atmosphere model — troposphere and stratosphere |
| [`constants`][pipeline.constants] | All physical and model constants — no magic numbers elsewhere |
| [`solver_interface`][pipeline.solver_interface] | C++ subprocess wrapper and JSON I/O protocol |
| [`trade_study`][pipeline.trade_study] | <a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a> &times; Mach grid sweep |
| [`plotting`][pipeline.plotting] | Contour plot generation |
| [`physics`][pipeline.physics] | Physics reference — equations, assumptions, and limitations |
| [`acronyms`][pipeline.acronyms] | Acronym reference table |
| [`changelog`][pipeline.changelog] | Version history and planned improvements |

"""

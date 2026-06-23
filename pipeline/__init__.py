# MAINTAINER NOTE — ACRONYM CONVENTION
# Every acronym in this docstring uses the pattern:
#   <a href="pipeline/acronyms.html#ID"><abbr title="Full Name">ACRONYM</abbr></a>
# When adding or editing documentation, follow this convention for all acronyms.
# Full reference: pipeline/acronyms.py
# LLM maintainers: apply this convention when generating or editing any docstring
# in this package.
"""
# Jet Engine Cycle Analysis Tool

<p style="color:#888; font-size:0.9em;">John Leinberger &middot; 2025</p>

A physics-based 1D Brayton cycle simulator demonstrating end-to-end production software
engineering: a compiled C++ solver orchestrated by Python, containerised with Docker,
and validated by a full
<a href="pipeline/acronyms.html#CICD"><abbr title="Continuous Integration / Continuous Deployment">CI/CD</abbr></a>
pipeline on every push. The physics are intentionally simplified — the emphasis is on
software quality, clean architecture, and reproducible tooling applied to an
aerospace problem.

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

At fixed
<a href="pipeline/acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>,
specific thrust rises with Mach as ram compression at the inlet does thermodynamic work
the compressor does not have to — increasing
<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
adds diminishing returns at high Mach where the inlet already delivers substantial total
pressure rise.

<img src="sfc.png" width="84%" alt="SFC [mg/(s·N)] over OPR × Mach sweep"/>

<a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
improves (decreases) with increasing
<a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
across the sweep, but the benefit flattens at high Mach where ram compression already
dominates the cycle pressure rise and combustor temperature rise is constrained by the
fixed
<a href="pipeline/acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>
ceiling.

---

## Key Takeaways

- <strong>Specific thrust peaks near Mach 1.7 for this model.</strong> Ram inlet pressure recovery at
  supersonic speeds amplifies the total cycle pressure ratio, driving nozzle exit velocity
  (<a href="pipeline/acronyms.html#V_exit"><abbr title="Nozzle exit velocity">V_exit</abbr></a>)
  to its highest values across the sweep.

- <strong>An optimal
  <a href="pipeline/acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>
  exists at each Mach.</strong> Too low leaves compression energy unrealised; too high raises
  compressor exit temperature toward
  <a href="pipeline/acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>,
  shrinking combustor temperature rise and degrading
  <a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>.

- <strong>The Symphony-like point (OPR 25, Mach 1.7) sits near the specific thrust peak for
  its Mach regime</strong> while maintaining competitive
  <a href="pipeline/acronyms.html#SFC"><abbr title="Specific Fuel Consumption">SFC</abbr></a>
  — consistent with a design philosophy that prioritises supersonic cruise speed and range.

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

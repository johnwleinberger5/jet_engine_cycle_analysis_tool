# MAINTAINER NOTE — ACRONYM CONVENTION
# Every acronym used across this documentation suite links here using the pattern:
#   <a href="acronyms.html#ID"><abbr title="Full Name">ACRONYM</abbr></a>
# When adding new acronyms: add an entry to the <dl> below with a matching id="ID",
# then apply the link+abbr pattern everywhere that acronym appears in any docstring.
# LLM maintainers: follow this convention when generating or editing docstrings.
"""
# Acronym Reference

All acronyms used across the engine cycle analysis documentation.

<dl>

<dt id="OPR"><strong>OPR</strong></dt>
<dd>Overall Pressure Ratio — ratio of compressor exit total pressure to compressor inlet
total pressure. Primary design variable in the trade study sweep (10–40).</dd>

<dt id="TIT"><strong>TIT</strong></dt>
<dd>Turbine Inlet Temperature — temperature of combustion gases entering the turbine.
Fixed at 1600 K for this model.</dd>

<dt id="SFC"><strong>SFC</strong></dt>
<dd>Specific Fuel Consumption — fuel mass flow rate per unit thrust [kg/(N·s)].
Lower is better. A measure of fuel efficiency.</dd>

<dt id="LHV"><strong>LHV</strong></dt>
<dd>Lower Heating Value — usable energy content of a fuel per unit mass,
excluding latent heat of water vapour in combustion products.
Jet-A: 43 MJ/kg.</dd>

<dt id="ISA"><strong>ISA</strong></dt>
<dd>International Standard Atmosphere — the ICAO-defined model of how atmospheric
temperature and pressure vary with altitude. Used to set ambient conditions at
60,000 ft cruise altitude.</dd>

<dt id="SAF"><strong>SAF</strong></dt>
<dd>Sustainable Aviation Fuel — bio-derived or synthetic drop-in replacement for
conventional Jet-A with a lower lifecycle carbon footprint.</dd>

<dt id="CICD"><strong>CI/CD</strong></dt>
<dd>Continuous Integration / Continuous Deployment — automated pipeline that builds,
tests, and deploys software on every code push. Implemented here via GitHub Actions.</dd>

<dt id="P0"><strong>P0</strong></dt>
<dd>Total (stagnation) pressure — pressure a moving fluid would reach if brought to rest
isentropically. Conserved across adiabatic, isentropic processes.</dd>

<dt id="T0"><strong>T0</strong></dt>
<dd>Total (stagnation) temperature — temperature a moving fluid would reach if brought to
rest adiabatically. Conserved across adiabatic shocks.</dd>

<dt id="gamma"><strong>gamma (γ)</strong></dt>
<dd>Ratio of specific heats — cp / cv. Fixed at 1.4 for calorically perfect air.</dd>

<dt id="cp"><strong>cp</strong></dt>
<dd>Specific heat at constant pressure — energy required to raise 1 kg of air by 1 K at
constant pressure. Fixed at 1005 J/(kg·K).</dd>

<dt id="eta_c"><strong>eta_c (η<sub>c</sub>)</strong></dt>
<dd>Compressor isentropic efficiency — ratio of ideal compressor work to actual compressor
work for a given pressure ratio. Set to 0.88.</dd>

<dt id="eta_t"><strong>eta_t (η<sub>t</sub>)</strong></dt>
<dd>Turbine isentropic efficiency — ratio of actual turbine work to ideal turbine work for
a given pressure ratio. Set to 0.90. Used here to determine the isentropic equivalent
exit temperature for the turbine pressure calculation.</dd>

<dt id="eta_b"><strong>eta_b (η<sub>b</sub>)</strong></dt>
<dd>Combustor efficiency — fraction of fuel energy released as heat in the combustor.
Set to 0.99.</dd>

<dt id="mdot_a"><strong>mdot_a (ṁ<sub>a</sub>)</strong></dt>
<dd>Mass flow rate of air through the engine [kg/s]. All specific quantities are
normalised per unit mdot_a.</dd>

<dt id="mdot_f"><strong>mdot_f (ṁ<sub>f</sub>)</strong></dt>
<dd>Mass flow rate of fuel [kg/s]. Determined by the combustor energy balance.</dd>

<dt id="V_exit"><strong>V_exit</strong></dt>
<dd>Nozzle exit velocity [m/s] — jet velocity after isentropic expansion to ambient
pressure. Primary driver of specific thrust.</dd>

<dt id="V_inlet"><strong>V_inlet</strong></dt>
<dd>Inlet freestream velocity [m/s] — aircraft flight speed. Equals Mach × speed of sound
at ambient temperature.</dd>

<dt id="PR"><strong>PR</strong></dt>
<dd>Pressure Ratio — generic term for the ratio of total pressures across a component
(compressor, turbine, or nozzle).</dd>

</dl>
"""

# This module exists solely as a documentation page rendered by pdoc.
# It contains no executable code.
_DOCS_ONLY = True

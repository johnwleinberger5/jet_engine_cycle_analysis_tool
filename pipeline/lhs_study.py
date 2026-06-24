"""Latin Hypercube Sampling dataset for engine cycle parameter space exploration.

Generates a space-filling design over four inputs —
<a href="acronyms.html#OPR"><abbr title="Overall Pressure Ratio">OPR</abbr></a>,
Mach,
<a href="acronyms.html#TIT"><abbr title="Turbine Inlet Temperature">TIT</abbr></a>,
and altitude — then evaluates the
<a href="solver_interface.html"><code>run_solver</code></a> at each point.
The resulting dataset is the training corpus for
<a href="surrogate.html"><code>EngineRegressor</code></a>.

Sweep bounds are defined in
<a href="constants.html"><code>constants</code></a>.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats.qmc import LatinHypercube

from pipeline import constants
from pipeline.io_utils import read_pkl, write_pkl
from pipeline.solver_interface import run_solver

_DEFAULT_DATASET_PATH = Path("outputs/lhs_dataset.pkl")

_COLUMNS = [
    "opr",
    "mach",
    "tit_k",
    "altitude_ft",
    "specific_thrust_n_per_kgs",
    "sfc_kg_per_s_per_n",
]


class LHSDataset:
    """Space-filling engine cycle dataset generated via Latin Hypercube Sampling.

    Attributes:
        df: ``pd.DataFrame`` with columns ``opr``, ``mach``, ``tit_k``,
            ``altitude_ft``, ``specific_thrust_n_per_kgs``, ``sfc_kg_per_s_per_n``.
    """

    df: pd.DataFrame

    def __init__(self, source: Path | int = _DEFAULT_DATASET_PATH, seed: int = 42) -> None:
        """Load an existing dataset or generate a new one.

        Args:
            source: If a ``Path``, load a previously saved dataset from that
                pickle file. If an ``int``, generate a new dataset with that
                many sample points and save it to ``outputs/lhs_dataset.pkl``.
            seed: Random seed for the Latin Hypercube sampler. Only used when
                ``source`` is an ``int``. Defaults to 42.

        Raises:
            FileNotFoundError: If ``source`` is a ``Path`` that does not exist.
            TypeError: If ``source`` is neither a ``Path`` nor an ``int``.
        """
        if isinstance(source, (str, Path)):
            self.df = read_pkl(Path(source))
        elif isinstance(source, int):
            self.df = self._generate(source, seed)
            write_pkl(_DEFAULT_DATASET_PATH, self.df)
        else:
            raise TypeError(f"source must be a Path or int, got {type(source)}")

    @staticmethod
    def _generate(n_samples: int, seed: int) -> pd.DataFrame:
        """Run the LHS sweep and return results as a DataFrame.

        Args:
            n_samples: Number of sample points to evaluate.
            seed: Random seed for the Latin Hypercube sampler.

        Returns:
            DataFrame with all input and output columns.
        """
        sampler = LatinHypercube(d=4, seed=seed)
        unit_samples = sampler.random(n=n_samples)

        lows = np.array([
            constants.LHS_OPR_MIN,
            constants.LHS_MACH_MIN,
            constants.LHS_TIT_MIN,
            constants.LHS_ALT_MIN,
        ])
        highs = np.array([
            constants.LHS_OPR_MAX,
            constants.LHS_MACH_MAX,
            constants.LHS_TIT_MAX,
            constants.LHS_ALT_MAX,
        ])
        samples = lows + unit_samples * (highs - lows)

        rows = []
        for opr, mach, tit_k, altitude_ft in samples:
            result = run_solver(mach=mach, opr=opr, tit_k=tit_k, altitude_ft=altitude_ft)
            rows.append({
                "opr": opr,
                "mach": mach,
                "tit_k": tit_k,
                "altitude_ft": altitude_ft,
                "specific_thrust_n_per_kgs": result.specific_thrust_n_per_kgs,
                "sfc_kg_per_s_per_n": result.sfc_kg_per_s_per_n,
            })

        return pd.DataFrame(rows, columns=_COLUMNS)

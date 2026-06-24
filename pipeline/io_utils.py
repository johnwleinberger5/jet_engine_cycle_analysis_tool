"""Pickle read/write utilities for persisting pipeline artifacts.

Used by <a href="lhs_study.html"><code>LHSDataset</code></a> and
<a href="surrogate.html"><code>EngineRegressor</code></a> to save and load
trained models and datasets.
"""

import pickle
from pathlib import Path


def read_pkl(pkl_path: Path) -> object:
    """Load a pickled object from disk.

    Args:
        pkl_path: Path to the ``.pkl`` file to read.

    Returns:
        The unpickled Python object.

    Raises:
        FileNotFoundError: If ``pkl_path`` does not exist.
    """
    pkl_path = Path(pkl_path)
    if not pkl_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {pkl_path}")
    with open(pkl_path, "rb") as f:
        return pickle.load(f)


def write_pkl(pkl_path: Path, obj: object) -> None:
    """Persist a Python object to disk as a pickle file.

    Creates parent directories if they do not exist.

    Args:
        pkl_path: Destination path for the ``.pkl`` file.
        obj: Any picklable Python object.
    """
    pkl_path = Path(pkl_path)
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl_path, "wb") as f:
        pickle.dump(obj, f)

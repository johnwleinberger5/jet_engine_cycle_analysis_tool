"""Generate the LHS dataset and save to outputs/lhs_dataset.pkl."""

from pipeline.lhs_study import LHSDataset
from pipeline import constants

if __name__ == "__main__":
    print(f"Generating {constants.LHS_N_SAMPLES:,} LHS samples...", flush=True)
    ds = LHSDataset(constants.LHS_N_SAMPLES)
    print(f"Done. Dataset shape: {ds.df.shape}")
    print(ds.df.describe())

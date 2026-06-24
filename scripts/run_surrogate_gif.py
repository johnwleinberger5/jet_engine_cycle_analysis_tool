"""Generate animated GIF sweeping TIT over the OPR × Mach grid using the surrogate.

Loads the trained EngineRegressor and sweeps TIT from LHS_TIT_MIN to LHS_TIT_MAX
across N_FRAMES frames. Each frame is a full OPR × Mach grid prediction at fixed
TIT and ALT_FT. Colorbar and contour levels are fixed across all frames so the
animation shows continuous physical change rather than rescaled axes.

Output: outputs/surrogate_tit_sweep.gif
"""

from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from pipeline import constants
from pipeline.surrogate import EngineRegressor
from pipeline.trade_study import TradeStudyResults, run_trade_study, _plot_specific_thrust, _plot_sfc

_MODEL_PATH = Path("outputs/engine_regressor.pkl")
_GIF_PATH = Path("outputs/surrogate_tit_sweep.gif")

_FPS = 4
_ALT_FT = constants.ALT_FT


def _build_grid_df(tit_k: float) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Build the full OPR × Mach input DataFrame for a single TIT value."""
    machs = np.linspace(constants.MACH_MIN, constants.MACH_MAX, constants.GIF_N_MACH)
    oprs = np.linspace(constants.OPR_MIN, constants.OPR_MAX, constants.GIF_N_OPR)
    mach_grid, opr_grid = np.meshgrid(machs, oprs)

    df = pd.DataFrame({
        "opr": opr_grid.ravel(),
        "mach": mach_grid.ravel(),
        "tit_k": tit_k,
        "altitude_ft": _ALT_FT,
    })
    return df, mach_grid, opr_grid


def _predictions_to_results(
    pred: pd.DataFrame,
    mach_grid: np.ndarray,
    opr_grid: np.ndarray,
) -> TradeStudyResults:
    """Reshape surrogate predictions into a TradeStudyResults for plotting."""
    shape = mach_grid.shape
    return TradeStudyResults(
        mach_grid=mach_grid,
        opr_grid=opr_grid,
        specific_thrust=pred["specific_thrust_n_per_kgs"].values.reshape(shape),
        sfc=pred["sfc_kg_per_s_per_n"].values.reshape(shape),
    )


if __name__ == "__main__":
    print("Loading surrogate model...", flush=True)
    reg = EngineRegressor(_MODEL_PATH)

    # Run solver trade study at design-point TIT/Alt to anchor color scale.
    # This ensures GIF frames are directly comparable to the static plots.
    print("Running solver trade study to anchor color scale...", flush=True)
    anchor = run_trade_study()
    thrust_vmin = float(anchor.specific_thrust.min())
    thrust_vmax = float(anchor.specific_thrust.max())
    sfc_vmin = float((anchor.sfc * 1e6).min())
    sfc_vmax = float((anchor.sfc * 1e6).max())
    thrust_levels = np.linspace(thrust_vmin, thrust_vmax, 15)
    sfc_levels = np.linspace(sfc_vmin, sfc_vmax, 15)
    print(f"  Thrust range: {thrust_vmin:.0f} - {thrust_vmax:.0f} N/(kg/s)", flush=True)
    print(f"  SFC range:    {sfc_vmin:.2f} - {sfc_vmax:.2f} mg/(s*N)", flush=True)

    tit_values = np.arange(constants.LHS_TIT_MIN, constants.LHS_TIT_MAX + constants.LHS_TIT_STEP, constants.LHS_TIT_STEP)
    _N_FRAMES = len(tit_values)
    print(f"  {_N_FRAMES} frames ({constants.LHS_TIT_STEP:.0f} K steps, "
          f"{constants.LHS_TIT_MIN:.0f}-{constants.LHS_TIT_MAX:.0f} K)", flush=True)

    # Pre-compute surrogate predictions for all frames
    print(f"Pre-computing {_N_FRAMES} surrogate frames...", flush=True)
    all_results = []
    for tit_k in tit_values:
        df, mach_grid, opr_grid = _build_grid_df(tit_k)
        pred = reg.predict(df)
        all_results.append(_predictions_to_results(pred, mach_grid, opr_grid))

    op = (constants.SYMPHONY_MACH, constants.SYMPHONY_OPR)

    def _fig_to_pil(fig: plt.Figure) -> Image.Image:
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).copy()

    # Render frames — close each figure immediately to avoid memory buildup
    print(f"Rendering {_N_FRAMES} frames...", flush=True)
    thrust_frames, sfc_frames = [], []
    for i, (tit_k, results) in enumerate(zip(tit_values, all_results)):
        suffix = f"TIT = {tit_k:.0f} K, Alt = {_ALT_FT:,.0f} ft"

        fig_t = _plot_specific_thrust(
            results, out=None, operating_point=op,
            vmin=thrust_vmin, vmax=thrust_vmax,
            levels=thrust_levels, title_suffix=suffix,
        )
        fig_s = _plot_sfc(
            results, out=None, operating_point=op,
            vmin=sfc_vmin, vmax=sfc_vmax,
            levels=sfc_levels, title_suffix=suffix,
        )
        thrust_frames.append(_fig_to_pil(fig_t))
        sfc_frames.append(_fig_to_pil(fig_s))

        if (i + 1) % max(1, _N_FRAMES // 10) == 0:
            print(f"  {i + 1} / {_N_FRAMES} frames rendered", flush=True)

    # Compile GIFs
    def _save_gif(frames: list[Image.Image], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Quantize each frame independently with dithering.
        # Color consistency across frames is enforced by fixed vmin/vmax, not the palette.
        quantized = [
            f.quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG)
            for f in frames
        ]
        quantized[0].save(
            str(path),
            save_all=True,
            append_images=quantized[1:],
            duration=1000 // _FPS,
            loop=0,
            optimize=False,
        )
        print(f"Saved: {path}", flush=True)

    print("Compiling GIFs...", flush=True)
    _save_gif(thrust_frames, _GIF_PATH.parent / "surrogate_tit_sweep_thrust.gif")
    _save_gif(sfc_frames, _GIF_PATH)

    print("Done.")

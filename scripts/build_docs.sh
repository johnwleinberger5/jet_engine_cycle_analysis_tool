#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="site"

echo "Building documentation..."
rm -rf "$OUTPUT_DIR"

# Static assets
mkdir -p "$OUTPUT_DIR/assets"
cp assets/jet_engine_cross_section.svg "$OUTPUT_DIR/assets/"

# Generate HTML from module docstrings
pdoc pipeline -o "$OUTPUT_DIR"

# Embed trade study plots and surrogate outputs.
# PNGs go to site/ (for pipeline.html) and site/pipeline/ (for surrogate.html etc).
# GIFs go to site/pipeline/ only (referenced from surrogate.html).
mkdir -p "$OUTPUT_DIR/pipeline"
if ls outputs/*.png 1>/dev/null 2>&1; then
    cp outputs/*.png "$OUTPUT_DIR/"
    cp outputs/*.png "$OUTPUT_DIR/pipeline/"
    echo "Trade study plots embedded."
else
    echo "WARNING: No PNG plots found in outputs/ — run the trade study first."
fi
if ls outputs/*.gif 1>/dev/null 2>&1; then
    cp outputs/*.gif "$OUTPUT_DIR/pipeline/"
    echo "Surrogate GIFs embedded."
else
    echo "WARNING: No GIFs found in outputs/ — run scripts/run_surrogate_gif.py first."
fi

# Root redirect so the deployed Pages URL lands on the package landing page
echo '<meta http-equiv="refresh" content="0;url=pipeline.html">' > "$OUTPUT_DIR/index.html"

echo ""
echo "Docs written to $OUTPUT_DIR/"
echo "Preview (Windows/Edge):"
echo "  start msedge \"\$(pwd -W)/site/pipeline.html\""
echo "Note: open site/pipeline.html directly — the root index.html redirect is"
echo "      blocked by browsers on local file:// URLs."

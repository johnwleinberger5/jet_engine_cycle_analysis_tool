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

# Embed trade study plots (must run the trade study first)
# Plots go alongside pipeline.html (site root), not inside site/pipeline/
if ls outputs/*.png 1>/dev/null 2>&1; then
    cp outputs/*.png "$OUTPUT_DIR/"
    echo "Trade study plots embedded."
else
    echo "WARNING: No plots found in outputs/ — images will be broken."
    echo "Run the trade study first: python scripts/run_trade_study.py"
fi

# Root redirect so the deployed Pages URL lands on the package landing page
echo '<meta http-equiv="refresh" content="0;url=pipeline.html">' > "$OUTPUT_DIR/index.html"

echo ""
echo "Docs written to $OUTPUT_DIR/"
echo "Preview (Windows/Edge):"
echo "  start msedge \"\$(pwd -W)/site/pipeline.html\""
echo "Note: open site/pipeline.html directly — the root index.html redirect is"
echo "      blocked by browsers on local file:// URLs."

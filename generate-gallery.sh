#!/usr/bin/env bash
set -euo pipefail

SCRIPT="./tries.py"
OUTDIR="EXAMPLES"

mkdir -p "$OUTDIR"

echo
echo "=========================================="
echo "  tries — THEME GALLERY"
echo "=========================================="
echo

echo "- Listing themes..."
mapfile -t THEMES < <("$SCRIPT" --list-themes)

for theme in "${THEMES[@]}"; do
    outfile="${OUTDIR}/theme-${theme}.pdf"

    echo "  - Rendering theme: ${theme}"
    echo "    Command: $SCRIPT --sample-hosts -H -T ${theme} | dot -Tpdf -o ${outfile}"

    "$SCRIPT" --sample-hosts -H -T "${theme}" \
        | dot -Tpdf -o "${outfile}"
done

echo
echo "- Theme gallery complete."
echo
echo "Examples: ${OUTDIR}/"
echo "=========================================="
echo

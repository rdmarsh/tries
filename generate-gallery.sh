#!/usr/bin/env bash
set -euo pipefail

SCRIPT="./build_tries.py"
OUTDIR="EXAMPLES"

mkdir -p "$OUTDIR"

echo
echo "=========================================="
echo "  build_tries — THEME GALLERY"
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
echo "Theme gallery complete. Files written to ${OUTDIR}/"
echo "=========================================="
echo

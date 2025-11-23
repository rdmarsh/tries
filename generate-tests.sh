#!/usr/bin/env bash
set -euo pipefail

SCRIPT="./build_tries.py"
OUTDIR="EXAMPLES"
TESTDIR="${OUTDIR}/tests"

mkdir -p "$TESTDIR"

echo
echo "=========================================="
echo "  build_tries — FEATURE TEST SUITE"
echo "=========================================="
echo

run_test() {
    name="$1"
    shift
    args=( "$@" )   # preserve quoting exactly

    dotfile="${TESTDIR}/${name}.dot"
    pngfile="${TESTDIR}/${name}.png"

    echo "  - ${name}"
    echo "    Command: $SCRIPT ${args[*]}"

    "$SCRIPT" "${args[@]}" > "$dotfile"
    dot -Tpng "$dotfile" -o "$pngfile"
}

echo "- Running tests..."
echo

# Character-mode tests
run_test "hosts_default"            --sample-hosts
run_test "hosts_head"               --sample-hosts -H
run_test "hosts_mark_oob"           --sample-hosts -m oob
run_test "hosts_ignore_case"        --sample-hosts --ignore-case
run_test "hosts_keep_prefix"        --sample-hosts --keep-prefix
run_test "hosts_keep_prefix_ignore_case"        --sample-hosts --keep-prefix --ignore-case
run_test "hosts_keep_fqdn"          --sample-hosts --keep-fqdn
run_test "hosts_no_labels"          --sample-hosts --no-labels

# Token-mode tests
run_test "ips_token"                --sample-ips -D .
run_test "paths_token"              --sample-paths -D /
run_test "urls_token"               --sample-urls -D /

# Head sorting tests
run_test "nato_token"               --sample-nato -T none
run_test "nato_token_head"          --sample-nato -H -T none

# Combined sample tests
run_test "combined_hosts_ips"       --sample-hosts --sample-ips -D .
run_test "combined_hosts_paths"     --sample-hosts --sample-paths -D /

# Theme tests
run_test "theme_midnight"           --sample-hosts -T midnight
run_test "theme_hotdog"             --sample-hosts -T hotdog
run_test "theme_tacky_test"         --sample-hosts -T tacky-test

echo
echo "Test suite complete."
echo "Examples: ${OUTDIR}/"
echo "Tests:    ${TESTDIR}/"
echo "=========================================="
echo

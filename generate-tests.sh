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
    args=( "$@" )   # preserve exact quoting

    dotfile="${TESTDIR}/${name}.dot"
    pngfile="${TESTDIR}/${name}.png"

    echo "  - ${name}"
    echo "    Command: $SCRIPT ${args[*]}"

    "$SCRIPT" "${args[@]}" > "$dotfile"
    dot -Tpng "$dotfile" -o "$pngfile"
}

echo
echo "- Running tests..."
echo

###############################################################################
# Character-mode tests
###############################################################################

run_test "hosts_default"                   --sample-hosts
run_test "hosts_TB"                        --sample-hosts -d TB
run_test "hosts_head"                      --sample-hosts -H
run_test "hosts_mark_nothing"              --sample-hosts -m ''
run_test "hosts_mark_srv"                  --sample-hosts -m srv
run_test "hosts_mark_fw_and_sw"            --sample-hosts -m fw sw
run_test "hosts_filter_fw"                 --sample-hosts -f fw
run_test "hosts_ignore_case"               --sample-hosts --ignore-case
run_test "hosts_keep_prefix"               --sample-hosts --keep-prefix
run_test "hosts_keep_prefix_ignore_case"   --sample-hosts --keep-prefix --ignore-case
run_test "hosts_keep_fqdn"                 --sample-hosts --keep-fqdn
run_test "hosts_no_labels"                 --sample-hosts --no-labels

#head sorting using nato
run_test "nato_head"                       --sample-nato -H

# head + no-labels (important behaviour case)
run_test "hosts_head_no_labels"            --sample-hosts -H --no-labels

###############################################################################
# Token-mode tests
###############################################################################

run_test "ips_token"                       --sample-ips -D .
run_test "paths_token"                     --sample-paths -D /
run_test "urls_token"                      --sample-urls -D /
run_test "emails_token"                      --sample-emails -D @ --rtl

# head-mode ignored in token-mode
run_test "ips_token_head_ignored"          --sample-ips -D . -H

# deeper marking in token-mode
run_test "paths_token_mark_share"          --sample-paths -D / -m share

# mixed-case token-mode + ignore-case
run_test "paths_mixed_case_ignore"         --sample-paths -D / --ignore-case

###############################################################################
# Token-mode corner cases
###############################################################################

# Empty input in token-mode (should not crash)
echo "" | run_test "empty_token_input"       -D .

# Combined multiple datasets + delimiter + filter
run_test "combined_filter_token"           --sample-hosts --sample-ips -D . -f 192

###############################################################################
# Combined samples (character-mode + token-mode)
###############################################################################

run_test "combined_hosts_ips"              --sample-hosts --sample-ips -D .
run_test "combined_hosts_paths"            --sample-hosts --sample-paths -D /

###############################################################################
# Theme sanity tests
###############################################################################

run_test "theme_default"                   --sample-hosts -T default
run_test "theme_midnight"                  --sample-hosts -T midnight
run_test "theme_hotdog"                    --sample-hosts -T hotdog
run_test "theme_tacky"                     --sample-hosts -T tacky-test
run_test "theme_none"                      --sample-hosts -T none

###############################################################################
# Override tests (only ONE of each type is needed)
###############################################################################

# Colour override test (one test is enough)
run_test "override_all_colours" \
    --sample-hosts \
    -cn red -cm green -ch blue -ce orange -cp purple

# Text (font colour) override test
run_test "override_all_text" \
    --sample-hosts \
    -tn red -tm green -th blue

# Font family test (single test)
run_test "font_menlo" \
    --sample-hosts -F menlo

###############################################################################

echo
echo "- Test suite complete."
echo
echo "Examples: ${OUTDIR}/"
echo "Tests:    ${TESTDIR}/"
echo "=========================================="
echo

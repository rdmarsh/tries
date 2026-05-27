#!/usr/bin/env python3
# encoding: utf-8
# test_tries.py — behaviour tests for tries.py
# Run with: python3 -m pytest test_tries.py  OR  python3 test_tries.py

import io
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import tries as T


def run(*args):
    """Run tries.main() with the given args and return the DOT output."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        T.main(list(args))
    finally:
        sys.stdout = old
    return buf.getvalue()


def nodes(dot):
    """Return the set of quoted node names declared in a DOT string."""
    import re
    return set(re.findall(r'^\s+"([^"]+)"\s+\[', dot, re.MULTILINE))


def has_attr(dot, node, key, value):
    """Return True if node declaration contains key="value"."""
    import re
    pattern = rf'"{re.escape(node)}"\s+\[([^\]]+)\]'
    m = re.search(pattern, dot)
    if not m:
        return False
    return f'{key}="{value}"' in m.group(1)


class TestVersion(unittest.TestCase):

    def test_version_output(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            T.main(["--version"])
        finally:
            sys.stdout = old
        self.assertIn(T.__version__, buf.getvalue())


class TestListThemes(unittest.TestCase):

    def test_lists_default(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            T.main(["--list-themes"])
        finally:
            sys.stdout = old
        self.assertIn("default", buf.getvalue().splitlines())

    def test_lists_midnight(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            T.main(["--list-themes"])
        finally:
            sys.stdout = old
        self.assertIn("midnight", buf.getvalue().splitlines())


class TestDumpThemes(unittest.TestCase):

    def test_dump_contains_themes(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            T.main(["--dump-themes"])
        finally:
            sys.stdout = old
        out = buf.getvalue()
        self.assertIn("THEMES", out)
        self.assertIn("FONT_MAP", out)


class TestEmptyInput(unittest.TestCase):

    def test_empty_input_produces_valid_graph(self):
        old_stdin = sys.stdin
        sys.stdin = io.StringIO("")
        try:
            dot = run()
        finally:
            sys.stdin = old_stdin
        self.assertTrue(dot.strip().startswith("graph tries {"))
        self.assertTrue(dot.strip().endswith("}"))


class TestCharacterMode(unittest.TestCase):

    def test_sample_hosts_contains_terminal_nodes(self):
        dot = run("--sample-hosts")
        ns = nodes(dot)
        self.assertIn("acmefw01", ns)
        self.assertIn("acmefw02", ns)
        self.assertIn("acmesw01", ns)
        self.assertIn("localhost", ns)

    def test_filter_keeps_matching(self):
        dot = run("--sample-hosts", "-f", "fw")
        ns = nodes(dot)
        self.assertIn("acmefw01", ns)
        self.assertIn("acmefw02", ns)

    def test_filter_excludes_non_matching(self):
        dot = run("--sample-hosts", "-f", "fw")
        ns = nodes(dot)
        self.assertNotIn("acmesw01", ns)
        self.assertNotIn("acmesw02", ns)
        self.assertNotIn("localhost", ns)

    def test_invert_filter_excludes_matching(self):
        dot = run("--sample-hosts", "-f", "fw", "--invert-filter")
        ns = nodes(dot)
        self.assertNotIn("acmefw01", ns)
        self.assertNotIn("acmefw02", ns)

    def test_invert_filter_keeps_non_matching(self):
        dot = run("--sample-hosts", "-f", "fw", "--invert-filter")
        ns = nodes(dot)
        self.assertIn("acmesw01", ns)
        self.assertIn("localhost", ns)

    def test_mark_applies_mark_color_to_oob(self):
        dot = run("--sample-hosts", "-M", "oob")
        # oob nodes should have the mark fillcolor
        self.assertTrue(has_attr(dot, "acmefw01-oob", "fillcolor", T.THEMES["default"]["mark"]))

    def test_mark_does_not_mark_non_matching(self):
        dot = run("--sample-hosts", "-M", "oob")
        # non-oob terminal should have normal color
        self.assertTrue(has_attr(dot, "acmefw01", "fillcolor", T.THEMES["default"]["normal"]))

    def test_mark_empty_marks_nothing(self):
        dot = run("--sample-hosts", "-M", "")
        mark_color = T.THEMES["default"]["mark"]
        # no node should have the mark fillcolor
        self.assertNotIn(f'fillcolor="{mark_color}"', dot)

    def test_ignore_case_lowercases_nodes(self):
        dot = run("--sample-hosts", "--ignore-case")
        ns = nodes(dot)
        # ACME-prefixed entries should be folded into lowercase
        self.assertIn("acmesrv01", ns)
        self.assertIn("acmesrv02", ns)
        for n in ns:
            self.assertEqual(n, n.lower(), f"node '{n}' is not lowercase")

    def test_keep_fqdn_includes_domain(self):
        dot = run("--sample-hosts", "--keep-fqdn")
        ns = nodes(dot)
        self.assertIn("acmefw01.domain.local", ns)
        # acmefw01 still appears as an internal prefix node in char-mode
        self.assertTrue(has_attr(dot, "acmefw01.domain.local", "shape", "Mrecord"))

    def test_default_strips_fqdn(self):
        dot = run("--sample-hosts")
        ns = nodes(dot)
        self.assertIn("acmefw01", ns)
        self.assertNotIn("acmefw01.domain.local", ns)

    def test_keep_prefix_retains_domain(self):
        dot = run("--sample-hosts", "--keep-prefix")
        ns = nodes(dot)
        self.assertTrue(any("acmesrv" in n for n in ns))

    def test_no_labels_produces_empty_labels(self):
        dot = run("--sample-hosts", "--no-labels")
        # terminal Mrecord nodes should have label=""
        self.assertIn('label=""', dot)
        # and no non-empty label for a known terminal
        self.assertNotIn('label="acmefw01"', dot)

    def test_head_mode_produces_circle(self):
        dot = run("--sample-hosts", "-H")
        self.assertIn('shape="circle"', dot)

    def test_direction_tb(self):
        dot = run("--sample-hosts", "-d", "TB")
        self.assertIn('rankdir="TB"', dot)

    def test_direction_lr(self):
        dot = run("--sample-hosts", "-d", "LR")
        self.assertIn('rankdir="LR"', dot)

    def test_output_ends_with_newline(self):
        dot = run("--sample-hosts")
        self.assertTrue(dot.endswith("\n"))

    def test_output_is_valid_graph_wrapper(self):
        dot = run("--sample-hosts")
        self.assertTrue(dot.strip().startswith("graph tries {"))
        self.assertTrue(dot.strip().endswith("}"))

    def test_deduplication(self):
        # Two identical inputs should produce the same node count as one
        dot_single = run("--sample-hosts")
        dot_double = run("--sample-hosts", "--sample-hosts")
        self.assertEqual(nodes(dot_single), nodes(dot_double))


class TestTokenMode(unittest.TestCase):

    def test_ips_token_splits_on_dot(self):
        dot = run("--sample-ips", "-D", ".")
        ns = nodes(dot)
        # Top-level octets should appear as root nodes
        self.assertIn("10", ns)
        self.assertIn("192", ns)

    def test_paths_token_splits_on_slash(self):
        dot = run("--sample-paths", "-D", "/")
        ns = nodes(dot)
        # leading slash produces an empty first token which is skipped,
        # so root-level nodes are the first non-empty segment
        self.assertIn("usr", ns)
        self.assertIn("opt", ns)

    def test_rtl_reverses_email_tokens(self):
        dot = run("--sample-emails", "-D", "@", "--rtl")
        ns = nodes(dot)
        # RTL: domain appears first, so top-level nodes should be domains
        self.assertIn("example.com", ns)

    def test_head_ignored_in_token_mode(self):
        dot = run("--sample-ips", "-D", ".", "-H")
        # head mode is disabled in token mode — no circle shapes
        self.assertNotIn('shape="circle"', dot)

    def test_token_mark_applies(self):
        dot = run("--sample-paths", "-D", "/", "-M", "share")
        mark_color = T.THEMES["default"]["mark"]
        self.assertIn(f'fillcolor="{mark_color}"', dot)


class TestThemes(unittest.TestCase):

    def test_midnight_theme_applied(self):
        dot = run("--sample-hosts", "-T", "midnight")
        self.assertIn(T.THEMES["midnight"]["normal"], dot)

    def test_none_theme_has_no_fillcolor(self):
        dot = run("--sample-hosts", "-T", "none")
        self.assertNotIn("fillcolor", dot)

    def test_color_override_applied(self):
        dot = run("--sample-hosts", "-cn", "red")
        self.assertIn('fillcolor="red"', dot)


if __name__ == "__main__":
    unittest.main()

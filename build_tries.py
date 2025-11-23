#!/usr/bin/env python3
# encoding: utf-8

#    build_tries.py
#    DOT-only trie generator with theme, color, and per-node text color support.
#    GPLv3 — David Marsh, 2019–2025
#
#    Includes:
#      * Character-level trie mode (default)
#      * Delimiter-mode (token-mode) via -D/--delim
#      * Hostname normalisation with --keep-prefix and --keep-fqdn
#      * Sample data flags (--sample-hosts, --sample-ips, --sample-paths, --sample-urls, sample-nato)
#      * Combined input: samples + files + stdin
#      * Theme loading, dumping, and saving support
#
#    Clarity is prioritised over cleverness.

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional

__version__ = "4.1.3"

# ---------------------------------------------------------------------------
# Default mark patterns
# ---------------------------------------------------------------------------

DEFAULT_MARK_PATTERNS = [
    "new",
    "old",
    "oob",
    "ilo",
    "trap",
    "traps",
    r"lm[0-9][0-9]$",
]

# ---------------------------------------------------------------------------
# Built-in fallback themes
# ---------------------------------------------------------------------------

FALLBACK_THEMES = {
    "default": {
        "normal": "cornsilk2",
        "mark": "palegreen2",
        "head": "lightblue2",
        "edge": "gray60",
        "point": "gray60",
        "text_normal": "black",
        "text_mark": "black",
        "text_head": "black",
    }
}

FALLBACK_FONTS = {
    "courier": "Courier",
    "menlo": "Menlo",
    "consolas": "Consolas",
}

# ---------------------------------------------------------------------------
# Load and merge external themes if present
# ---------------------------------------------------------------------------

try:
    from themes import THEMES as EXT_THEMES, FONT_MAP as EXT_FONTS
    THEMES = {**FALLBACK_THEMES, **EXT_THEMES}
    FONT_MAP = {**FALLBACK_FONTS, **EXT_FONTS}

    # Optional custom themes
    try:
        from themes_custom import THEMES as CUSTOM_THEMES
        THEMES = {**THEMES, **CUSTOM_THEMES}
    except Exception:
        pass

except Exception:
    # No external themes.py — fallback only
    THEMES = FALLBACK_THEMES
    FONT_MAP = FALLBACK_FONTS

# Always ensure one canonical "default"
THEMES["default"] = THEMES.get("default", FALLBACK_THEMES["default"])

# ---------------------------------------------------------------------------
# Debug helper
# ---------------------------------------------------------------------------

def dbg(enabled: bool, msg: str) -> None:
    if enabled:
        sys.stderr.write(f"[DEBUG] {msg}\n")

# ---------------------------------------------------------------------------
# DOT escaping
# ---------------------------------------------------------------------------

def dot_escape(s: str) -> str:
    if s is None:
        return ""

    s = unicodedata.normalize("NFC", s)

    translate_map = {
        ord("\\"): "\\\\",
        ord("\""): "\\\"",
        ord("\n"): "\\n",
        ord("\r"): "",
        ord("\t"): "\\t",
        ord("{"): "\\{",
        ord("}"): "\\}",
        ord("|"): "\\|",
        ord("<"): "\\<",
        ord(">"): "\\>",
    }

    return s.translate(translate_map)

# ---------------------------------------------------------------------------
# Pretty dictionary dumper (zero dependencies)
# ---------------------------------------------------------------------------

def dump_python_dict(name, dct, indent=0):
    pad = " " * indent
    out = [f"{name} = {{"]
    for key in sorted(dct.keys()):
        val = dct[key]
        if isinstance(val, dict):
            out.append(f'{pad}    "{key}": {{')
            for k2, v2 in sorted(val.items()):
                v2_repr = "None" if v2 is None else f'"{v2}"'
                out.append(f'{pad}        "{k2}": {v2_repr},')
            out.append(f"{pad}    }},")
        else:
            v_repr = "None" if val is None else f'"{val}"'
            out.append(f'{pad}    "{key}": {v_repr},')
    out.append(f"{pad}}}")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# Hostname normalisation
# ---------------------------------------------------------------------------

def extract_hostname(raw: str, keep_prefix: bool, keep_fqdn: bool) -> str:
    r"""
    Normalise hostnames.

    Defaults:
      - Strip Windows DOMAIN\\ prefix (unless --keep-prefix).
      - Strip DNS domain (server.domain.local -> server) unless --keep-fqdn.
    """
    tmp = raw.strip()

    # Windows DOMAIN\host
    if not keep_prefix and "\\" in tmp:
        tmp = tmp.split("\\", 1)[1]

    # DNS suffix
    if not keep_fqdn and "." in tmp:
        tmp = tmp.split(".", 1)[0]

    # Clean any leading slashes/backslashes (e.g. \\server, /server)
    tmp = tmp.lstrip("\\/").strip()
    return tmp

# ---------------------------------------------------------------------------
# Input processing
# ---------------------------------------------------------------------------

def read_lines(files):
    """
    Yield lines from files, or stdin if no files are provided.
    """
    if not files:
        for line in sys.stdin:
            yield line.rstrip("\n")
        return

    for f in files:
        with f:
            for line in f:
                yield line.rstrip("\n")

def filter_lines(lines, regex):
    pat = re.compile(regex, re.IGNORECASE)
    return [l for l in lines if pat.search(l)]

def resolve_theme_values(args):
    parser = args._parser
    th = THEMES[args.theme]

    # Colors (only override theme if user changed the CLI default)
    cn = args.color_normal if args.color_normal != parser.get_default("color_normal") else th["normal"]
    cm = args.color_mark   if args.color_mark   != parser.get_default("color_mark")   else th["mark"]
    ch = args.color_head   if args.color_head   != parser.get_default("color_head")   else th["head"]
    ce = args.color_edge   if args.color_edge   != parser.get_default("color_edge")   else th["edge"]
    cp = args.color_point  if args.color_point  != parser.get_default("color_point")  else th["point"]

    # Font colors
    tn = args.text_normal or th.get("text_normal")
    tm = args.text_mark   or th.get("text_mark")
    th = args.text_head   or th.get("text_head")

    return cn, cm, ch, ce, cp, tn, tm, th

# ---------------------------------------------------------------------------
# Trie building
# ---------------------------------------------------------------------------

def build_trie(
    lines: Iterable[str],
    mark_patterns: List[str],
    mark_is_default: bool,
    head_mode: bool,
    color_normal: Optional[str],
    color_mark: Optional[str],
    color_head: Optional[str],
    keep_prefix: bool,
    keep_fqdn: bool,
    ignore_case: bool,
    no_labels: bool,
    text_normal: Optional[str],
    text_mark: Optional[str],
    text_head: Optional[str],
    delim: Optional[str],
):

    edges = set()
    node_meta: Dict[str, Dict[str, str]] = {}

    # Compile marking patterns
    patterns = [p if (mark_is_default and p.endswith("$")) else p for p in mark_patterns]
    if mark_is_default:
        patterns = [p if p.endswith("$") else p + "$" for p in patterns]
    mark_regex = [re.compile(p, re.IGNORECASE) for p in patterns]

    def marked(name: str) -> bool:
        return any(p.search(name) for p in mark_regex)

    # -------------------------------------------------------------
    # TOKEN MODE
    # -------------------------------------------------------------
    if delim:
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue

            tokens = [t for t in raw.split(delim) if t]
            if not tokens:
                continue

            token_labels = tokens
            tokens_norm = [t.lower() for t in tokens] if ignore_case else tokens

            is_marked = any(p.search(raw) for p in mark_regex)
            fill = color_mark if is_marked else color_normal
            text = text_mark if is_marked else text_normal

            parent = tokens_norm[0]

            if parent not in node_meta:
                nm = {"shape": "Mrecord"}
                nm["label"] = "" if no_labels else token_labels[0]
                if fill:
                    nm["style"] = "filled"
                    nm["fillcolor"] = fill
                if text:
                    nm["fontcolor"] = text
                node_meta[parent] = nm

            for i in range(1, len(tokens_norm)):
                token = tokens_norm[i]
                child = parent + delim + token

                edges.add((parent, child))

                if child not in node_meta:
                    nm = {"shape": "Mrecord"}
                    nm["label"] = "" if no_labels else token_labels[i]
                    if fill:
                        nm["style"] = "filled"
                        nm["fillcolor"] = fill
                    if text:
                        nm["fontcolor"] = text
                    node_meta[child] = nm

                parent = child

        # mark trie as TOKEN MODE for rendering
        node_meta["_delim_mode"] = True

        return edges, node_meta

    # -------------------------------------------------------------
    # CHARACTER MODE
    # -------------------------------------------------------------
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue

        base = extract_hostname(raw, keep_prefix, keep_fqdn)
        if not base:
            continue

        label_text = base
        base_norm = base.lower() if ignore_case else base

        fill = color_mark if marked(base_norm) else color_normal
        text = text_mark if marked(base_norm) else text_normal

        if base_norm not in node_meta:
            nm = {"shape": "Mrecord"}
            nm["label"] = "" if no_labels else label_text
            if fill:
                nm["style"] = "filled"
                nm["fillcolor"] = fill
            if text:
                nm["fontcolor"] = text
            node_meta[base_norm] = nm

        # Build all prefix nodes first, then apply terminal styling
        parent = base_norm[0]

        # Head node (single-character prefix) if needed
        if parent not in node_meta:
            if head_mode:
                attrs = {"shape": "circle"}
                attrs["label"] = "" if no_labels else parent
                if color_head:
                    attrs["style"] = "filled"
                    attrs["fillcolor"] = color_head
                if text_head:
                    attrs["fontcolor"] = text_head
                node_meta[parent] = attrs
            else:
                node_meta[parent] = {"shape": "point"}

        # Walk remaining characters, creating point nodes for internal prefixes
        for ch in base_norm[1:]:
            child = parent + ch
            edges.add((parent, child))
            if child not in node_meta:
                node_meta[child] = {"shape": "point"}
            parent = child

    return edges, node_meta

# ---------------------------------------------------------------------------
# DOT output
# ---------------------------------------------------------------------------

def to_dot(
    edges,
    nodes,
    *,
    rankdir,
    edge_color,
    point_color,
    fontname,
):

    out = []
    out.append("graph tries {")
    out.append(f'  graph [fontname="{fontname}"];')
    out.append(f'  node  [fontname="{fontname}"];')
    out.append(f'  rankdir="{rankdir}";')

    if edge_color:
        out.append(f'  edge [color="{edge_color}"];')

    delim_mode = nodes.get("_delim_mode", False)

    # Node declarations
    for name in sorted(nodes.keys()):
        if name == "_delim_mode":
            continue

        attrs = dict(nodes[name])
        safe = dot_escape(name)

        if attrs.get("shape") == "point" and point_color:
            attrs.setdefault("color", point_color)

        parts = []
        for k, v in attrs.items():
            if k == "label":
                v = dot_escape(v)
            parts.append(f'{k}="{v}"')

        out.append(f'  "{safe}" [{", ".join(parts)}];')

    # ---------------------------------------------------------
    # CHARACTER MODE ONLY: alphabetical single-character heads
    # ---------------------------------------------------------
    if not delim_mode:
        heads = sorted([n for n in nodes.keys() if len(n) == 1])
        if heads:
            out.append(
                "  { rank = same; " +
                "; ".join(f'"{dot_escape(h)}"' for h in heads) +
                " }"
            )
            for a, b in zip(heads, heads[1:]):
                out.append(f'  "{dot_escape(a)}" -- "{dot_escape(b)}" [style=invis];')

    # Real edges
    for p, c in sorted(edges):
        out.append(f'  "{dot_escape(p)}" -- "{dot_escape(c)}";')

    out.append("}")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_HOSTS = [
    "acmefw01.domain.local",
    "acmefw02.domain.local",
    "acmefw01-oob.domain.local",
    "acmefw02-oob.domain.local",
    "acmesw01.domain.local",
    "acmesw02.domain.local",
    "acmeweb01.domain.local",
    "localhost.localdomain",
    r"ACME\\acmesrv01.domain.local",
    r"ACME\\acmesrv02.domain.local",
]

SAMPLE_IPS = [
    "10.0.0.1",
    "10.0.0.2",
    "10.0.1.20",
    "10.0.1.21",
    "10.0.2.20",
    "10.0.2.21",
    "10.20.30.40",
    "192.168.0.1",
    "192.168.1.1",
    "192.168.1.2",
    "172.16.5.100",
    "8.8.8.8",
]

SAMPLE_PATHS = [
    "/usr/local/bin",
    "/usr/local/sbin",
    "/usr/local/share",
    "/usr/bin",
    "/usr/sbin",
    "/usr/share",
    "/opt/tools",
    "/opt/scripts",
    "/etc/nginx",
    "/etc/ssh",
    "/var/log",
    "/var/tmp",
    "/var/www",
    "/var/www/html",
]

SAMPLE_URLS = [
    "http://example.com/about",
    "https://example.com",
    "https://example.com/about",
    "https://example.com/login",
    "https://example.com/admin",
    "https://acme.local",
    "https://acme.local/app",
    "https://acme.local/app/api",
    "https://portal.example.net",
    "https://portal.example.net/customers",
    "https://portal.example.net/customers/acme",
]

SAMPLE_NATO = [
	"acme",
	"brav",
	"char",
	"delt",
	"echo",
	"foxt",
	"gamm",
	"hote",
	"indi",
	"juli",
	"kilo",
	"lima",
	"mang",
	"nove",
	"osca",
	"papa",
	"quar",
	"rome",
	"sier",
	"tang",
	"umbr",
	"vict",
	"whis",
	"xeno",
	"yank",
	"zulu",
]


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="build_tries.py",
        description=(
            "Build a character-level trie or token-based trie and emit Graphviz DOT.\n"
            "Filtering (-f) and marking (-m) are case-insensitive.\n"
            "Supports themes, font families, hostname normalisation, and sample data.\n"
            "Graphviz is required to render the DOT output."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "files",
        nargs="*",
        type=argparse.FileType("r"),
        help="Input files (if omitted, read from stdin unless sample flags are used).",
    )

    parser.add_argument(
        "--keep-prefix",
        action="store_true",
        help="Keep Windows DOMAIN\\host prefix (default is to strip it).",
    )

    parser.add_argument(
        "--keep-fqdn",
        action="store_true",
        help="Keep full DNS name (default is to strip after first '.').",
    )

    parser.add_argument(
        "-f", "--filter",
        default=".*",
        help="Regex filter applied to input lines (case-insensitive).",
    )

    parser.add_argument(
        "-m", "--mark",
        nargs="*",
        default=list(DEFAULT_MARK_PATTERNS),
        help="Regex patterns used to mark terminal nodes.",
    )

    parser.add_argument(
        "-i", "--ignore-case",
        action="store_true",
        help="Normalise internal node IDs to lowercase.",
    )

    parser.add_argument(
        "--no-labels",
        action="store_true",
        help="Remove labels from terminal and head nodes.",
    )

    parser.add_argument(
        "-H", "--head",
        action="store_true",
        help="Render first character as a filled circle (ignored in --delim mode).",
    )

    parser.add_argument(
        "-d", "--dir",
        default="LR",
        choices=["LR", "TB"],
        help="Graph direction (LR=Left-to-Right, TB=Top-to-Bottom).",
    )

    parser.add_argument(
        "-D", "--delim",
        metavar="CHAR",
        help=(
            "Split input strings on this delimiter to build a token-based trie "
            "instead of a character-level trie (e.g. '.' for IPs, '/' for paths/URLs)."
        ),
    )

    parser.add_argument(
        "-o", "--output",
        help="Write DOT output to this file instead of stdout.",
    )

    parser.add_argument(
        "-T", "--theme",
        choices=sorted(THEMES.keys()),
        default="default",
        help="Color theme to apply to nodes.",
    )

    parser.add_argument(
        "-F", "--font",
        choices=sorted(FONT_MAP.keys()),
        default="courier",
        help="Font family for labels (safe, cross-platform choices).",
    )

    # Color overrides
    parser.add_argument(
        "-cn", "--color-normal",
        dest="color_normal",
        default="lightgoldenrod1",
        help="Override theme normal terminal color.",
    )
    parser.add_argument(
        "-cm", "--color-mark",
        dest="color_mark",
        default="palegreen3",
        help="Override theme marked terminal color.",
    )
    parser.add_argument(
        "-ch", "--color-head",
        dest="color_head",
        default="lightblue",
        help="Override theme head-node color.",
    )
    parser.add_argument(
        "-ce", "--color-edge",
        dest="color_edge",
        default="gray60",
        help="Override theme edge color.",
    )
    parser.add_argument(
        "-cp", "--color-point",
        dest="color_point",
        default="gray60",
        help="Override theme point-node color.",
    )

    # Font-color overrides
    parser.add_argument(
        "-tn", "--text-normal",
        dest="text_normal",
        default=None,
        help="Override text color for normal terminal nodes.",
    )
    parser.add_argument(
        "-tm", "--text-mark",
        dest="text_mark",
        default=None,
        help="Override text color for marked terminal nodes.",
    )
    parser.add_argument(
        "-th", "--text-head",
        dest="text_head",
        default=None,
        help="Override text color for head node.",
    )

    # Sample flags (can be combined; also combine with real input)
    parser.add_argument(
        "--sample-hosts",
        action="store_true",
        help="Include built-in sample hostnames.",
    )
    parser.add_argument(
        "--sample-ips",
        action="store_true",
        help="Include built-in sample IPv4 addresses.",
    )
    parser.add_argument(
        "--sample-paths",
        action="store_true",
        help="Include built-in sample UNIX-style directory paths.",
    )
    parser.add_argument(
        "--sample-urls",
        action="store_true",
        help="Include built-in sample URLs.",
    )
    parser.add_argument(
        "--sample-nato",
        action="store_true",
        help="Include built-in sample NATO words.",
    )

    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit.",
    )

    parser.add_argument(
        "--dump-themes",
        action="store_true",
        help="Dump merged themes.py content (THEMES + FONT_MAP) and exit.",
    )

    parser.add_argument(
        "--save-theme",
        metavar="NAME",
        help="Save current color/font settings as a theme NAME to themes_custom.py.",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Write debug information to stderr.",
    )

    args = parser.parse_args(argv)
    args._parser = parser
    return args

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)

    # Simple info modes first
    if args.dump_themes:
        print("# autogenerated themes.py template\n")
        print(dump_python_dict("THEMES", THEMES))
        print()
        print(dump_python_dict("FONT_MAP", FONT_MAP))
        return

    if args.version:
        print(f"build_tries v{__version__}")
        return

    if args.list_themes:
        for name in sorted(THEMES.keys()):
            print(name)
        return

    dbg(args.debug, f"Version: {__version__}")
    dbg(args.debug, f"Args: {args}")

    # Resolve theme colors and text
    cn, cm, ch, ce, cp, text_normal, text_mark, text_head = resolve_theme_values(args)

    # ----------------------------------------------------------------------
    # Save theme (uses resolved values)
    # ----------------------------------------------------------------------
    if args.save_theme:
        theme_name = args.save_theme

        data = {
            "normal": cn,
            "mark": cm,
            "head": ch,
            "edge": ce,
            "point": cp,
            "text_normal": text_normal,
            "text_mark": text_mark,
            "text_head": text_head,
        }

        custom_path = Path("themes_custom.py")
        custom_themes = {}

        # Load existing custom themes if file exists
        if custom_path.exists():
            namespace = {}
            exec(custom_path.read_text(), namespace)
            custom_themes = namespace.get("THEMES", {})

        # Update / add the new theme
        custom_themes[theme_name] = data

        # Write back out
        with custom_path.open("w", encoding="utf-8") as fp:
            fp.write("# Auto-generated custom themes\n\n")
            fp.write(dump_python_dict("THEMES", custom_themes))
            fp.write("\n")

        print(f"Saved theme '{theme_name}' to themes_custom.py")

        # **Do NOT continue into trie-building or DOT output**
        return

    # ----------------------------------------------------------------------
    # Combine samples + files + stdin (Option C)
    # ----------------------------------------------------------------------
    combined = []

    if args.sample_hosts:
        combined.extend(SAMPLE_HOSTS)
    if args.sample_ips:
        combined.extend(SAMPLE_IPS)
    if args.sample_paths:
        combined.extend(SAMPLE_PATHS)
    if args.sample_urls:
        combined.extend(SAMPLE_URLS)
    if args.sample_nato:
        combined.extend(SAMPLE_NATO)

    if args.files:
        for line in read_lines(args.files):
            combined.append(line)

    if combined:
        raw_lines = combined
    else:
        # No samples and no files: read stdin
        raw_lines = read_lines(args.files)

    # Strip and dedupe
    raw_lines = [line.strip() for line in raw_lines if line.strip()]
    lines = sorted(set(raw_lines))

    dbg(args.debug, f"Read {len(raw_lines)} raw lines, {len(lines)} unique after dedupe.")
    dbg(args.debug, f"Lines: {lines}")

    # Filtering
    matched = filter_lines(lines, args.filter)
    dbg(args.debug, f"Filter regex: {args.filter}")
    dbg(args.debug, f"{len(matched)} lines matched filter.")
    dbg(args.debug, f"Matched: {matched}")

    # Marking patterns
    mark_is_default = (args.mark == DEFAULT_MARK_PATTERNS)

    dbg(args.debug, "Resolved colors & text:")
    dbg(args.debug, f"  normal={cn}, mark={cm}, head={ch}, edge={ce}, point={cp}")
    dbg(args.debug, f"  text_normal={text_normal}, text_mark={text_mark}, text_head={text_head}")

    # Head-mode is only meaningful in character-mode
    if args.delim:
        args.head = False

    # Build trie
    edges, node_meta = build_trie(
        matched,
        mark_patterns=args.mark,
        mark_is_default=mark_is_default,
        head_mode=args.head,
        color_normal=cn,
        color_mark=cm,
        color_head=ch,
        keep_prefix=args.keep_prefix,
        keep_fqdn=args.keep_fqdn,
        ignore_case=args.ignore_case,
        no_labels=args.no_labels,
        text_normal=text_normal,
        text_mark=text_mark,
        text_head=text_head,
        delim=args.delim,
    )

    dbg(args.debug, f"Final edge count: {len(edges)}")
    dbg(args.debug, f"Final node count: {len(node_meta)}")

    fontname = FONT_MAP[args.font]

    dot = to_dot(
        edges,
        node_meta,
        rankdir=args.dir,
        edge_color=ce,
        point_color=cp,
        fontname=fontname,
    )

    if args.output:
        dbg(args.debug, f"Writing DOT to {args.output}")
        Path(args.output).write_text(dot)
    else:
        dbg(args.debug, "Writing DOT to stdout")
        sys.stdout.write(dot)

if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 expandtab:

# build_tries

`build_tries` converts a list of hostnames, IPs, paths, or tokens into a
**trie** and outputs **Graphviz DOT**.

You can then use Graphviz to render the text output into PDF, PNG, SVG,
etc.

*A trie is a tree-like structure used for storing strings in a way that
exposes shared prefixes.*

It is useful for:

- Visualising naming conventions
- Discovering embedded structure in text
- Analysing patterns in hostnames, IPs, or path structures
- Documenting legacy naming schemes
- Seeing structure that is usually hidden

There are **no Python dependencies** to produce DOT output.

**Graphviz** is needed if you want to render the DOT into PDF or PNG.

![Example Trie Output](example.png)

---

## Features

- Reads from files or STDIN
- Character-level trie mode
- Token mode via `-D "CHAR"`
- **Themes** (color + text presets)
- Per-node color overrides
- Per-node text color overrides
- Case-insensitive tries (`--ignore-case`)
- Windows `DOMAIN\host` prefix stripping (`--include-domain`)
- Optional FQDN stripping (`--include-fqdn`)
- Hide labels (`--no-labels`)
- Multiple sample datasets:
  - `--sample-hosts`
  - `--sample-ips`
  - `--sample-paths`
  - `--sample-urls`
  - `--sample-nato`
- Automatically combines sample data + file input
- Fully standalone, no imports beyond Python stdlib
- Per-node color control
  - normal terminals
  - marked terminals
  - head node
- Per-node **text colors**
  - `text_normal`
  - `text_mark`
  - `text_head`
- Cross-platform safe font choices
- Case-insensitive filtering and marking
- Included theme-gallery generator script
- Simple `--version` flag and `--debug` output

---

## Installation

Just copy `build_tries.py` and optionally `themes.py` somewhere into your `$PATH`.

Requirements:

- Python 3.6+
- Graphviz (only for rendering)

macOS install:

```
brew install graphviz
```

---

## Basic Usage

Render a trie from a file:

```
./build_tries.py servers.txt | dot -Tpdf -o trie.pdf
```

Render PNG:

```
./build_tries.py servers.txt | dot -Tpng -o trie.png
```

Read from STDIN:

```
cat servers.txt | ./build_tries.py | dot -Tpng -o trie.png
```

Print the version and exit:

```
./build_tries.py --version
```

Enable debug logging:

```
./build_tries.py --debug file.txt
```

---

## Examples

### Hosts

![Example Hosts Trie Output](example_hosts.png)

This image was generated using:

```
./build_tries.py --sample-hosts -H -m oob \
    | dot -Tpng -o example_hosts.png
```

### Paths

![Example Paths Trie Output](example_paths.png)

This image was generated using:

```
./build_tries.py --sample-paths -D "/" -m usr \
    | dot -Tpng -o example_paths.png
```

### IPs

![Example IPs Trie Output](example_ips.png)

This image was generated using:

```
./build_tries.py --sample-ips -D "." -m 192 \
    | dot -Tpng -o example_ips.png
```

### URLs

![Example HTML Trie Output](example_urls.png)

This image was generated using:

```
./build_tries.py --sample-urls -D "/" -m login \
    | dot -Tpng -o example_urls.png
```

These demonstrate:

- The default theme (`warm-sand`)
- Head-node highlighting (`-H`)
- Character-mode
- Token-mode (`-D`)
- Marking (`-m`)
- Sample datasets

---

## Themes

Themes define all colors for:

- Normal terminal nodes
- Marked terminal nodes
- Head node (`-H`)
- Edges
- Point nodes
- Node text colors

List available themes:

```
./build_tries.py --list-themes
```

To use a theme, for example midnight:

```
./build_tries.py --sample-hosts -T midnight | dot -Tpdf -o midnight.pdf
```

Generate a gallery:

```
./generate-theme-gallery.sh
```

### Custom Themes

You can save your current color and text overrides as a reusable theme:

```
./build_tries.py \
    -cn lightskyblue1 \
    -cm mediumspringgreen \
    -ch royalblue3 \
    -ce cyan3 \
    -cp gray50 \
    -tn black \
    -tm black \
    -th white \
    --save-theme electric-dusk
```

This creates (or updates) `themes_custom.py` with a theme called
`electric-dusk`.

You can then use it later:

```
./build_tries.py --sample-hosts -T electric-dusk | dot -Tpng -o dusk.png
```

---

## Colors and Fonts

All colors used by build_tries.py - including theme colors and
CLI overrides - use the X11 color palette supported by Graphviz.

This means you can use any standard color name such as cornsilk2,
palegreen3, royalblue3, gray60, or lightskyblue1 without needing hex
codes.

The full list of valid color names is available here:

https://graphviz.org/doc/info/colors.html

### Theme Color Overrides

Override theme colors with:

- `-cn`, `--color-normal`
- `-cm`, `--color-mark`
- `-ch`, `--color-head`
- `-ce`, `--color-edge`
- `-cp`, `--color-point`

Example:

```
./build_tries.py --sample -H -T warm-sand \
    -cn mistyrose -ch skyblue \
    | dot -Tpdf -o custom.pdf
```

### Font Color Overrides

Override per-node label colors:

- `-tn`, `--text-normal`   (normal terminal)
- `-tm`, `--text-mark`     (marked terminal)
- `-th`, `--text-head`     (head node)

Example:

```
./build_tries.py --sample -H -T nightfall -fh black \
    | dot -Tpdf -o out.pdf
```

---

## Font Family Selection

Use a safe cross-platform font family:

- `-F courier`
- `-F courier-new`
- `-F dejavu`
- `-F liberation`
- `-F nimbus`
- `-F helvetica`
- `-F menlo`
- `-F consolas`

Example:

```
./build_tries.py --sample-hosts -F menlo | dot -Tpdf -o out.pdf
```

---

## Filter Input (`-f`)

Filter text via regex:

```
./build_tries.py -f 'fw' servers.txt
```

Filtering is case-insensitive.

---

## Marking Terminal Nodes

Use `--mark` (`-m`) with regex patterns:

```
./build_tries.py -m 'prod$' servers.txt
```

Multiple patterns:

```
./build_tries.py -m 'oob$' 'fw$' 'lm[0-9][0-9]$' servers.txt
```

Regex is case-insensitive by default.

---

## Head Node Rendering

To display the first character as a filled circle:

```
./build_tries.py -H servers.txt
```

---

## Case-Insensitive Tries (`--ignore-case`)

To treat upper and lower case as equivalent in the trie:

```
./build_tries.py --ignore-case servers.txt
```

This normalises internal trie IDs but keeps labels unchanged.

When `--ignore-case` is enabled:

- Internal trie nodes IDs are lowercased
- Mixed-case variants (e.g. `acmeweb01` and `ACMEWEB02`) share the same root path
- Labels retain their original case
- Prevents mixed-case duplication caused by case-only differences

When `--ignore-case` is **not** set, case is preserved in node IDs and the trie
structure is strictly case-sensitive.

---

## DOMAIN\host Prefixes

Strip:

```
ACME\server01
ACME\server02
```

Normally becomes:

```
server01
server02
```

To keep the domain:

```
./build_tries.py --include-domain
```

---

## Including FQDN

Input:

```
server01.domain.local
```

Default becomes:

```
server01
```

Keep the full FQDN:

```
./build_tries.py --include-fqdn
```

---

## Removing Labels

Remove labels from terminal and head nodes:

```
./build_tries.py --no-labels
```

---

## Sample Datasets

The sample flags are useful for:
- Testing themes
- Rendering example outputs
- Verifying colors and texts
- Ensuring Graphviz output works

```
./build_tries.py --sample-hosts
./build_tries.py --sample-ips
./build_tries.py --sample-paths
./build_tries.py --sample-urls
./build_tries.py --sample-nato
```

---

## Output Format

DOT output always goes to STDOUT unless `-o` is used.

Example DOT output:

```
graph tries {
  graph [fontname="Courier"];
  node  [fontname="Courier"];
  rankdir="LR";
  "a" [shape="point"];
  "ac" [shape="Mrecord", label="ac"];
  { rank = same; "a" }
  "a" -- "ac";
}
```

Render (using Graphviz):

```
dot -Tpdf -o trie.pdf
```

---

## Workflow Example

```
./build_tries.py servers.txt -H -T safe \
    | dot -Tpdf -o networks.pdf
```

---

## License

GPLv3 (c) David Marsh
2019–2025

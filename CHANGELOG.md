# Changelog
All notable changes to **build_tries** are documented here

This project adheres to the structure and spirit of
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning is semantic-style but practical rather than strict

---
## [4.2.3] - 2025-11-28
### Changed
- Moved all sample data into samples.py

---
## [4.2.2] - 2025-11-27
### Changed
- Small improvement to compile marking patterns

---
## [4.2.1] - 2025-11-27
### Changed
- filter and match are now case sensitive

---

## [4.2.0] – 2025-11-24
### Added
- `--invert-filter` flag for negative filtering (select all non-matching lines)

### Changed
- Calling feature comp

---
### [4.1.6] - 2025-11-24
### Added
- added `--sample-emails` flag
- added `--rtl` option, reverse token order (token mode only)
- Test suite expanded to cover RTL mode and new sample set
- Documentation updated for RTL mode, email examples, and improved filter section

---
### [4.1.5] - 2025-11-23
### Fixed
- allow `-m ''` to not mark any nodes, overriding defaults

---
### [4.1.4] - 2025-11-23
### Fixed
- Corrected terminal-node rendering where a full hostname (e.g. `acmefw01`)
  was incorrectly left as an internal point node when a longer variant
  (e.g. `acmefw01-oob`) appeared later in the input.
  Terminal nodes are now always upgraded to proper `Mrecord` nodes with labels
  and colours applied after all prefixes are constructed.

---
## [4.1.3] - 2025-11-23
### Added
- sample-nato to list words to check sorting of head nodes

### Changed
- fixed rank same for IP addresses

---
## [4.1.2] - 2025-11-23
### Added
- added new theme `tacky-test`

---
## [4.1.1] - 2025-11-23
### Changed
- changed flags for font normal head and mark to text normal head and mark
  - `-fn, --font-normal`: `-tn, --text-normal`: 
  - `-fm, --font-mark`: `-tm, --text-mark`
  - `-fh, --font-head`: `-th, --text-head`

---

## [4.1.0] – 2025-11-23
### Added
- **Token-mode hierarchical IDs** (`a/b/c` → `a`, `a/b`, `a/b/c`)
- **Token-mode marking** now applies to the full raw input line
- **URL sample dataset** (`--sample-urls`)
- Combined sample flags now merge input from:
  - `--sample-hosts`
  - `--sample-ips`
  - `--sample-paths`
  - `--sample-urls`
  - plus files + STDIN
- Added persistent user-defined theme support via `themes_custom.py`

### Changed
- Token-mode now correctly creates **unique mid-nodes**
- Token mid-nodes are now **Mrecord nodes**, not points
- Internal branching logic in token-mode simplified
- `--head` is automatically disabled in token-mode

---

## [4.0.9] – 2025-11-23
### Added
- Full **URL sample dataset**

### Fixed
- Windows domain-prefix handling:
  - Correctly strips `DOMAIN\host`
  - Correctly strips `\\server`
  - Handles mixed slash variants consistently
- Improved merging of sample data + stdin + file input

---

## [4.0.8] – 2025-11-23
### Added
- **Delimiter mode** (`-D`, `--delim`) for token-based tries  
  Ideal for:
  - IPs (`-D .`)
  - Paths (`-D /`)
  - URLs (`-D /`)
- Support for multi-depth hierarchical token structures

### Fixed
- `--keep-prefix` and `--keep-fqdn` now operate independently
- Removed lingering `SyntaxWarning` around docstrings
- Marking logic functioning correctly inside token-mode

---
### [4.0.4] - 2025-11-18
### Changed
- Now fully supports case-insensitive operation via --ignore-case

---

### [4.0.3] - 2025-11-18
### Changed
- Extended escaping for characters that will break dot

---

### [4.0.2] - 2025-11-18
### Added
- Force font colors in theme rather than debault to black

---

### [4.0.1] - 2025-11-18
### Added
- More debugging output

---

### [4.0.0] - 2025-11-18
### Changed
- Rollback to known good base
- Renamed from `build-char-tries.py` to `build_tries.py`
- Moved themes to `themes.py` to stop cluttering the main script

---

## [3.8.0] – 2025-11-17
### Added
- Per-node **font color system**:
  - `font_normal`
  - `font_mark`
  - `font_head`
- CLI overrides:
  - `-fn, --font-normal`
  - `-fm, --font-mark`
  - `-fh, --font-head`
- All themes updated to include font color fields
- Hotdog Stand theme now renders head node label in white/black appropriately

### Changed
- Removed global “font” fallback; explicit per-node colors are now used everywhere
- Readability improvements throughout code

---

## [3.7.9] – 2025-11-16
### Added
- Per-theme **font_head** override
- Hotdog Stand head node label now correctly drawn in white
- Expanded theme system for greater flexibility

---

## [3.7.8] – 2025-11-16
### Fixed
- Removed Python `SyntaxWarning` by switching to **raw docstrings** for domain-prefix help
- Cleaned all remaining escape-sequence issues

---

## [3.7.7] – 2025-11-16
### Changed
- “Palettes” renamed to **“themes”** across UI and code
- Flags updated to `-t, --theme`
- Help text improved for clarity
- All color override flags moved to consistent “short-left” format

---

## [3.7.6] – 2025-11-16
### Added
- Proper label removal via `--no-labels` (terminal + head nodes)
- Case-insensitive matching behaviour clarified in help text

### Fixed
- Domain prefix help text causing invalid escape warnings

---

## [3.7.5] – 2025-11-16
### Added
- Curated font list:
  - courier, courier-new, dejavu, liberation, nimbus, helvetica, menlo, consolas
- Theme override flags for color:
  - `-cn`, `-cm`, `-ch`, `-ce`, `-cp`
- Improved DOT rendering reliability across macOS/Linux

---

## [3.7.4] – 2025-11-15
### Added
- Full theme system (formerly palettes)
- Dark-mode friendly themes (`nightfall`, `midnight`)
- Hotdogstand theme (Windows 3.11)

---

## [3.7.3] – 2025-11-15
### Added
- Sample dataset improvements
- Cleaner domain-prefix stripping rules

---

## [3.7.0–3.7.2] – 2025-11-14
### Added
- Large theme rework and color cleanup
- Starting transition from palettes → themes
- Head-node circle rendering improvements

---

## [3.6.x] – 2025-11-13
### Added
- Configurable node colors
- Regex-based node marking rules
- Begin rewrite for DOT-only output (no graphviz Python dependency)

---

## [3.5.x] – 2025-11-10
### Added
- Initial palette system
- Rank direction control (`--dir`)
- Regex filtering (`--filter`)
- Initial color override support

---

## [3.x early] – 2025
### Changed
- Major internal rewrite
- Vastly improved trie generation logic
- Removed deprecated code paths from v2
- Switched from Python Graphviz bindings to pure DOT output

---

## [2.x] – 2020
### Added
- Early graph generation using Python graphviz module
- Basic node building
- Initial regex support

### Removed (later)
- All graphviz Python dependency usage (moved to pure DOT output)

---

## [1.x] – 2019
### Added
- First working trie builder
- Basic text processing
- Very early prototype

---

## [0.x] – 2019 (Initial)
- Project created
- Experimental parsing and debugging utilities

---

## Legend
- **Added** — new features
- **Changed** — updates or modifications
- **Fixed** — bug fixes
- **Removed** — features removed or replaced

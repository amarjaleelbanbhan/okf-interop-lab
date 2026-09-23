# OKF Interop Lab

An installable, local **Open Knowledge Format (OKF) Markdown concept-link checker** for developers maintaining knowledge bundles. It reports missing internal concepts and unsafe paths, exports a directed relationship graph, and produces JSON or SARIF for CI workflows. Scanning requires no LLM, network access or paid API.

> Independent community project. Not affiliated with Google or Microsoft. This is an experimental development version, not a complete OKF validator or cross-implementation conformance suite.

## Installation and usage

Python 3.11+ is required.

```bash
git clone https://github.com/amarjaleelbanbhan/okf-interop-lab.git
cd okf-interop-lab
python -m pip install -e .
okf-linkcheck examples/bundle
okf-linkcheck /path/to/your/bundle --format json --output links.json
okf-linkcheck /path/to/your/bundle --format sarif --output links.sarif
```

Expected sample output:

```text
3 concepts; 4 internal .md links; 3 resolved; 1 missing; 0 unsafe
notes/order-guide.md:5: missing-target: /tables/future.md
```

The checked-in synthetic bundle deliberately contains a reference to an unfinished concept.

**Important:** OKF v0.2 §6.1 allows broken cross-links. They are warnings, **not OKF conformance failures**. The default CLI exit code is 0 even with missing links. Teams may opt into stricter repository policies:

```bash
okf-linkcheck /path/to/your/bundle --fail-on missing
okf-linkcheck /path/to/your/bundle --fail-on all
```

Exit codes: 0 = scan complete, no findings matching the chosen failure policy; 1 = opt-in failure policy triggered; 2 = scan or I/O error. The tool reports source filenames and approximate containing-block line numbers. JSON paths are relative to the bundle root; edges are deduplicated, while resolved link counts include repeated link occurrences. SARIF is version 2.1.0; the tool outputs a file but does not upload it to GitHub.

## Scope and limitations

The checker handles CommonMark inline and reference links, bundle-relative and file-relative `.md` targets, optional URL-encoded paths, and links with heading fragments (it verifies that the Markdown file exists, **not** that the heading exists). It skips fenced code, inline code, image links, external URLs, non-Markdown assets, directory links, in-page anchors, and the reserved `index.md` and `log.md` pages. It does not inspect `sources[].resource` frontmatter, raw HTML or wiki-links, and does not audit arbitrary-size adversarial bundles, trust, metadata, or YAML conformance. It does not execute Markdown, referenced code or network requests.

## Tests

```bash
python -m unittest discover -s tests -v
okf-linkcheck examples/bundle --format json
```

The CI workflow runs the test suite and CLI JSON/SARIF smoke checks on Python 3.11, 3.12 and 3.13. These are tests of this tool, not independent consumer compatibility benchmarks.

## Experimental historical reference-viewer comparison

The original `interop.py` remains available for a narrowly scoped comparison with a pinned official reference viewer revision. Clone the [official OKF repository](https://github.com/GoogleCloudPlatform/open-knowledge-format) and check out commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`, then run:

```bash
python interop.py examples/bundle --upstream ../open-knowledge-format
```

The historical `raw-results.json` describes the earlier prototype comparison, not a new result from this checker. Official [issue #14](https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/14) and existing [PR #23](https://github.com/GoogleCloudPlatform/open-knowledge-format/pull/23) already address much of the reference-viewer discrepancy. We have not submitted a competing upstream fix.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the historical research files. Those reports are a snapshot of earlier prototype work, not a claim of a complete 15-project source-code audit.

License: [MIT](LICENSE).

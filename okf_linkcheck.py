"""Audit Markdown concept links in an OKF bundle without changing the bundle.

Broken cross-links are explicitly permitted by OKF v0.2 §6.1. Findings are
advisory unless a caller opts into --fail-on missing or --fail-on all.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from interop import MARKDOWN, RESERVED, markdown_body


def _target(bundle: Path, source: Path, href: str) -> tuple[str, str | None]:
    """Return (ignored|resolved|missing|unsafe, concept ID or intended path)."""
    if not href or href.startswith("#"):
        return "ignored", None
    if "\\" in href or any(ord(ch) < 32 for ch in href):
        return "unsafe", None
    try:
        parts = urlsplit(href)
    except ValueError:
        return "unsafe", None
    if parts.scheme or parts.netloc or href.startswith("//"):
        return "ignored", None
    path = unquote(parts.path)
    if not path.endswith(".md"):
        return "ignored", None  # assets, anchors, directory links, other formats
    if "\\" in path or "\x00" in path or any(ord(ch) < 32 for ch in path):
        return "unsafe", None
    base = bundle if path.startswith("/") else source.parent
    target = (base / path.lstrip("/")).resolve()
    try:
        relative = target.relative_to(bundle)
    except ValueError:
        return "unsafe", None
    if target.name in RESERVED:
        return "ignored", None  # reserved navigation/history pages are not concepts
    normalized = relative.as_posix()
    if not target.is_file():
        return "missing", normalized
    return "resolved", relative.with_suffix("").as_posix()


def _iter_links(body: str):
    for token in MARKDOWN.parse(body):
        if token.type != "inline":
            continue
        # CommonMark token.map points at the first line of the block. This is
        # a block-level position, not the exact position within a long paragraph.
        line = (token.map[0] + 1) if token.map else 1
        for child in token.children or []:
            if child.type == "link_open":
                href = child.attrGet("href")
                if href:
                    yield line, href


def scan(bundle: Path) -> dict:
    """Return deterministic, JSON-serializable link graph and advisory findings."""
    root = bundle.resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not an OKF bundle directory: {bundle}")
    diagnostics: list[dict] = []
    edges: set[tuple[str, str]] = set()
    count = checked = resolved = 0
    for source in sorted(root.rglob("*.md")):
        if source.name in RESERVED:
            continue
        # Never traverse into files symlinked outside the bundle.
        try:
            source.relative_to(root)
            source.resolve().relative_to(root)
        except ValueError:
            continue
        if not source.is_file():
            continue
        source_name = source.relative_to(root).as_posix()
        count += 1
        raw = source.read_text(encoding="utf-8")
        frontmatter_lines = len(raw.splitlines(keepends=True)) - len(markdown_body(raw).splitlines(keepends=True))
        body = markdown_body(raw)
        for local_line, href in _iter_links(body):
            status, target = _target(root, source, href)
            if status == "ignored":
                continue
            checked += 1
            if status == "resolved":
                resolved += 1
                edges.add((source_name.removesuffix(".md"), target))
            else:
                kind = "missing-target" if status == "missing" else "unsafe-path"
                diagnostics.append({"rule_id": kind, "source": source_name,
                                    "line": local_line + frontmatter_lines,
                                    "href": href, "target": target,
                                    "message": ("Target does not exist in this bundle"
                                                if status == "missing" else
                                                "Target has an unsafe or out-of-bundle path")})
    diagnostics.sort(key=lambda d: (d["source"], d["line"], d["rule_id"], d["href"]))
    return {"tool": "okf-linkcheck", "concepts": count, "links_checked": checked,
            "resolved_links": resolved, "missing_links": sum(d["rule_id"] == "missing-target" for d in diagnostics),
            "unsafe_links": sum(d["rule_id"] == "unsafe-path" for d in diagnostics),
            "edges": [{"from": a, "to": b} for a, b in sorted(edges)],
            "diagnostics": diagnostics}


def as_sarif(report: dict) -> dict:
    """Produce SARIF 2.1.0 for code-scanning or CI artifact upload."""
    rules = [("missing-target", "Link target not present (OKF permits broken links)"),
             ("unsafe-path", "Internal concept link escapes the bundle")]
    return {"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{"tool": {"driver": {"name": "okf-linkcheck", "rules": [
                {"id": name, "shortDescription": {"text": description}} for name, description in rules]}},
                "results": [{"ruleId": d["rule_id"],
                             "level": "warning" if d["rule_id"] == "missing-target" else "error",
                             "message": {"text": f'{d["message"]}: {d["href"]}'},
                             "locations": [{"physicalLocation": {
                                 "artifactLocation": {"uri": d["source"]},
                                 "region": {"startLine": d["line"]}}}]} for d in report["diagnostics"]]}]}


def _human(report: dict) -> str:
    summary = (f'{report["concepts"]} concepts; {report["links_checked"]} internal .md links; '
               f'{report["resolved_links"]} resolved; {report["missing_links"]} missing; '
               f'{report["unsafe_links"]} unsafe')
    lines = [summary]
    for d in report["diagnostics"]:
        lines.append(f'{d["source"]}:{d["line"]}: {d["rule_id"]}: {d["href"]}')
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="OKF bundle directory")
    parser.add_argument("--format", choices=("text", "json", "sarif"), default="text")
    parser.add_argument("--output", type=Path, help="write report to this file instead of stdout")
    parser.add_argument("--fail-on", choices=("none", "missing", "all"), default="none",
                        help="opt-in CI exit policy; broken links are allowed by OKF")
    args = parser.parse_args(argv)
    try:
        report = scan(args.bundle)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"okf-linkcheck: {exc}", file=sys.stderr)
        return 2
    result = report if args.format == "json" else as_sarif(report) if args.format == "sarif" else None
    rendered = (json.dumps(result, indent=2, ensure_ascii=False) + "\n") if result is not None else _human(report)
    if args.output:
        try:
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"okf-linkcheck: {exc}", file=sys.stderr)
            return 2
    else:
        sys.stdout.write(rendered)
    if args.fail_on == "all" and report["diagnostics"]:
        return 1
    if args.fail_on == "missing" and report["missing_links"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

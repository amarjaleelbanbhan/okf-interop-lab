"""Narrow OKF concept-link probe, not a full OKF conformance validator."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

MARKDOWN = MarkdownIt("commonmark")
FRONTMATTER = re.compile(r"\A(?:\ufeff)?---[ \t]*\r?\n.*?^(?:---|\.\.\.)[ \t]*\r?\n", re.S | re.M)
RESERVED = {"index.md", "log.md"}


def markdown_body(text: str) -> str:
    """Strip frontmatter only at the beginning, never split later horizontal rules."""
    match = FRONTMATTER.match(text)
    return text[match.end():] if match else text


def resolve(root: Path, source: Path, href: str) -> str | None:
    """Return an existing concept ID; reject non-concepts and bundle escapes."""
    if "\\" in href or any(ord(c) < 32 for c in href):
        return None
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or href.startswith("//"):
        return None
    path = unquote(parts.path)
    if not path.endswith(".md") or "\x00" in path or "\\" in path:
        return None
    root = root.resolve()
    source = source.resolve()
    try:
        source.relative_to(root)
    except ValueError:
        return None
    base = root if path.startswith("/") else source.parent
    candidate = (base / path.lstrip("/")).resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.name in RESERVED or not candidate.is_file():
        return None
    return relative.with_suffix("").as_posix()


def markdown_hrefs(body: str) -> list[str]:
    """Read CommonMark inline/reference links, excluding fenced and inline code."""
    hrefs = []
    for token in MARKDOWN.parse(body):
        if token.type != "inline":
            continue
        for child in token.children or []:
            if child.type == "link_open":
                href = child.attrGet("href")
                if href:
                    hrefs.append(href)
    return hrefs


def edges(root: Path, source: Path) -> list[str]:
    body = markdown_body(source.read_text(encoding="utf-8"))
    return sorted({concept for href in markdown_hrefs(body)
                   if (concept := resolve(root, source, href)) is not None})


def probe(root: Path, upstream: Path | None = None) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    results = []
    upstream_extractor = None
    if upstream is not None:
        sys.path.insert(0, str(upstream.resolve() / "src"))
        from reference_agent.viewer.generator import _extract_links
        upstream_extractor = _extract_links
    for source in sorted(root.rglob("*.md")):
        if source.name in RESERVED or not source.resolve().is_relative_to(root):
            continue
        expected = edges(root, source)
        row = {"source": source.relative_to(root).as_posix(), "resolved": expected}
        if upstream_extractor is not None:
            body = markdown_body(source.read_text(encoding="utf-8"))
            actual = sorted(set(upstream_extractor(body, source.parent, root)))
            row.update(upstream_edges=actual, missing=sorted(set(expected) - set(actual)),
                       extra=sorted(set(actual) - set(expected)))
        results.append(row)
    return {"bundle": str(root), "upstream": str(upstream) if upstream else None,
            "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--upstream", type=Path, help="local checkout of pinned OKF reference viewer")
    args = parser.parse_args()
    print(json.dumps(probe(args.bundle, args.upstream), indent=2))


if __name__ == "__main__":
    main()

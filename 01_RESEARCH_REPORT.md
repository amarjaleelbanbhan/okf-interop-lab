# Research report — 2026-09-23

## Findings

- **VERIFIED:** Google's June 2026 announcement described OKF v0.1 as a portable Markdown/YAML knowledge format. The canonical repository now documents v0.2; the older knowledge-catalog directory explicitly says its copy is frozen. Sources: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing, https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md, https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/README.md.
- **VERIFIED:** Current OKF §6.1 supports bundle-relative and file-relative Markdown links, treats them as untyped directed relationships, and requires consumers to tolerate missing targets. It does not define a graph query engine. Source: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/ad30107c31c06aec8a7d5636e0d1058118604e6f/SPEC.md#L439-L466.
- **VERIFIED:** Microsoft GraphRAG uses LLM extraction, graph construction and community summaries; its local/global search are retrieval strategies, not an OKF interchange implementation. Sources: https://github.com/microsoft/graphrag/blob/main/docs/index.md, https://github.com/microsoft/graphrag/blob/main/docs/query/overview.md.
- **INFERENCE:** OKF can carry curated knowledge that a RAG/GraphRAG consumer could ingest, but the two are distinct layers. A conversion requires preserving source IDs and independently testing query behavior.
- **VERIFIED:** Issue #14 describes a viewer link mismatch; open PR #23 targets much of it. Sources: https://github.com/GoogleCloudPlatform/open-knowledge-format/issues/14, https://github.com/GoogleCloudPlatform/open-knowledge-format/pull/23. A duplicate upstream fix would waste review effort.
- **UNKNOWN:** Real-world adoption, production security, full compliance and maintainers' future decisions were not independently reproduced. Stars were not used as adoption evidence.

## Method and limitations

Read the canonical specification and checked-out source at `ad30107c31c06aec8a7d5636e0d1058118604e6f`; inspected issue pages and open PR list on 2026-09-23. Only the reference viewer was executed locally. The 15-project inventory is a discovery screen, **not** a 15-way source audit: unverified license, dependencies, maintenance and gaps are marked UNKNOWN. No paid APIs or interviews were used. Issues #24 and #26 were located in the current issue listing but individual pages could not be opened reliably; #29 could not be verified.
## Unreleased

- Local prototype and three unit tests; no versioned public release yet.

## Unreleased local revision (2026-09-24)

- Replace regex Markdown link scanner with CommonMark token parsing.
- Add six regression tests; nine local tests pass.
- Add Python package metadata and GitHub Actions CI configuration.
- Preserve the original pinned-upstream comparison as a historical baseline, and add separately named local-only v2 output.

## Unreleased: installable link checker

- Added `okf-linkcheck` console command with whole-bundle text, JSON, and SARIF results.
- Added advisory diagnostics for missing `.md` targets and unsafe paths, deduplicated graph edges and opt-in CI failure policies.
- Added nine checker tests, documented exclusions, and CI command-line smoke checks.
- Preserved historical upstream prototype results as earlier evidence; no independent consumer compatibility benchmark or versioned release has been claimed.

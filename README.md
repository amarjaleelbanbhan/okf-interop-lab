# OKF link interoperability probe

An experimental, runnable fixture for testing how OKF consumers resolve Markdown concept links. It compares an independent CommonMark-based resolver against the official reference viewer at a pinned revision.

This is **not** a general OKF validator, GraphRAG engine, conformance certificate, or official Google project.

## Install and test

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python interop.py examples/bundle
```

To compare against the pinned reference viewer, clone `https://github.com/GoogleCloudPlatform/open-knowledge-format`, check out `ad30107c31c06aec8a7d5636e0d1058118604e6f`, and run `python interop.py examples/bundle --upstream ../upstream-okf` with the checkout at the indicated path. See `07_TEST_AND_BENCHMARK_RESULTS.md` for recorded findings.

The test fixture demonstrates a missing bundle-relative concept edge in the pinned viewer; official issue #14 documents the problem and open PR #23 already addresses much of it. **Do not open a competing upstream fix without checking its status.**

## Scope and limitations

The local resolver handles CommonMark inline and reference links, file-relative and bundle-relative concept paths, fragments, and safe path traversal. It does not evaluate `sources[].resource`, raw HTML, images, or wiki-style links as concept edges. Cross-consumer compatibility has **not** been established. The historical `raw-results.json` came from the earlier regex-based probe; `raw-results-local-v2.json` contains the newer local-only run.

All reports and evidence files reflect a prototype, not a public benchmark or general compatibility claim.

Licensed under Apache-2.0.
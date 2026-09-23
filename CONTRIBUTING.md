# Contributing

Use a small, reproducible fixture and regression test for each change. Install with `python -m pip install -e .`, then run `python -m unittest discover -s tests -v` and `okf-linkcheck examples/bundle` before opening a PR.

The format explicitly permits broken cross-links; do not turn advisory missing-target findings into unconditional conformance failures. Keep contributions focused on the checker's stated Markdown concept-link scope, document assumptions, and preserve deterministic and bundle-relative JSON paths. For an interoperability claim, include exact upstream tool/version or commit, raw results and a competing interpretation when applicable. Discuss major parser or specification changes before implementation.

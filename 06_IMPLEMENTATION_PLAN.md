# Plan and acceptance criteria

Completed: minimal fixture, local resolver, CLI JSON comparison, unit tests, pinned source comparison and raw result. Acceptance: both OKF §6.1 forms resolve, duplicates collapse, nonexistent links are tolerated, path escapes are rejected, and a pinned upstream omission is reproducible.

Next: use a CommonMark parser to prevent code-fence false positives; add encoded-path and fragment navigation browser checks; pin two other consumers and document setup; get maintainer feedback in #14 or PR #23 before proposing any upstream change. Do not call the current probe a complete validator.

Follow-up local revision: parser limitations for code blocks/reference links and frontmatter horizontal rules now have regression tests. Next prerequisites remain independent consumer comparison, upstream pinned revision re-run, browser navigation checks, and actual GitHub CI execution. Do not infer upstream behavior from the new local-only JSON.

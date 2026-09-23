# Security

Please report suspected vulnerabilities privately to the repository maintainer through GitHub's available private reporting channels rather than posting exploit details publicly.

The checker reads Markdown files locally and does not execute referenced code, follow HTTP links, or load third-party plugins. It checks resolved paths for escape outside the bundle and skips symlinked source files that resolve outside the root. It has not been audited for filesystem race conditions, resource exhaustion, untrusted huge directory trees, or malicious archive extraction. Do not point it at confidential or adversarial bundles in a privileged environment. Do not treat its link diagnostics as content-trust or authorization decisions.

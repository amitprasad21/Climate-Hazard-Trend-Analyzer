# Documentation checks

`check_docs.py` uses only Python's standard library. Run from the workspace root:

```powershell
python scripts/check_docs.py --self-test
python scripts/check_docs.py
```

It checks local Markdown links, fences, unique task definitions/statuses, complete metadata/ownership/concept IDs, referenced task/requirement IDs, dependency cycles, summary-status agreement, required documents (including the canonical AI development workflow), canonical grayscale palette and 13 opaque token contrast pairs from frontend/docs/design.md (root DESIGN is navigation only). The concept matrix must have original IDs/names 1–85 exactly once, nine nonempty fields, valid statuses, linked authorities and reciprocal task mappings. Generated dependency/cache directories are excluded.

Self-tests cover broken links/fences, task/reference/cycle errors, missing metadata, inconsistent summary status, missing/duplicate concepts, invalid concept status, undefined task mappings, nonreciprocal mappings, non-grayscale tokens/overlays, insufficient control contrast, missing tokens and contrast. These are documentation checks, not application acceptance.

It does not fetch remote links, validate Markdown anchors, render Mermaid, inspect a browser, test APIs, audit dependencies or prove scientific correctness. Manual consistency review remains required. Update this checker only when the document conventions change; it is not an application test suite.

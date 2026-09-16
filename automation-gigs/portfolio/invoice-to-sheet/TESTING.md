| # | Input | Expected |
|---|-------|----------|
| 1 | Clean vendor invoice PDF | Row with all fields, `needs_review` empty, email labelled processed |
| 2 | Scanned image-only PDF (no text layer) | Row with `needs_review = YES`, total 0 |
| 3 | Anthropic API down | Email labelled needs-review, no row, no crash |

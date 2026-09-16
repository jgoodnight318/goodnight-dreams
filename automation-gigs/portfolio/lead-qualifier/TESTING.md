| # | Input | Expected |
|---|-------|----------|
| 1 | Email: "Hi, interested in a quote for 20 units, what's your pricing?" | score ≥ 60, Slack alert, row in Sheet |
| 2 | Email: "Unsubscribe me" | score < 60, no Slack alert, row in Sheet |
| 3 | Anthropic key revoked | "Report API failure" Slack message; workflow does not error out |

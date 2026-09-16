Hi,

I run a version of this stack myself, so I will answer your design questions directly rather than describe experience in general.

What I have built: a local-first LLM router used by my own scheduled monitoring and document-scoring jobs. It tries a local Ollama model first (health check before every call, so a dead server costs under two seconds, not a hung connect), then a remote Ollama host, then a hosted provider, then a last-resort CLI backend. Every call records which backend answered, latency, and the full attempt trail including the failures before the winner. JSON replies are validated against a schema and a bad reply triggers escalation instead of a silently degraded answer. That is the core of what you are asking for, minus the OpenAI-compatible front door and the cost ledger, which are the first two things I would add.

For low-confidence handling I use the same rule you described: accept only when the reply passes validation and a confidence threshold, otherwise escalate with the reason attached. A public example of that pattern, fail-closed, with tests: https://github.com/jgoodnight318/document-pipeline-demo

How I would build yours:

1. LiteLLM Proxy as the single OpenAI-compatible endpoint, with a thin FastAPI policy layer in front of it that reads your routing matrix from YAML (task type, sensitivity, freshness, citation need, cost ceiling). Changing a route or adding a provider is a config edit, not a code change.
2. vLLM in Docker Compose for the local model, with quantization, context window, concurrency and timeout set per model. Confidential documents and internal RAG default to local and never leave unless a rule explicitly allows it. If local is down, confidential requests fail closed with a clear error rather than leaking to Perplexity.
3. Perplexity as the premium route for current information, citations, and hard reasoning, and as the automatic fallback on timeout, validation failure, or low confidence.
4. One JSON line per request: provider, model, routing reason, latency, tokens, estimated cost, escalation and fallback status. A small report over that log gives you local versus premium mix, cost by workflow, and escalation and failure rates, which is what tells you whether the local box is paying for itself.
5. RAG on pgvector with local embeddings, chunking with source traceability so every answer cites the passage it came from.
6. An evaluation suite built from your real task types (filing extraction, narrative to table, sourced summaries, code assistance) that scores local against Perplexity on quality, latency and cost, and sets the escalation thresholds from measured numbers instead of guesses.

Hardware, honestly: for the proof of concept I would rent a cloud GPU for a few weeks and measure your actual mix before buying anything. For a single-GPU production box, a 24 GB card runs 7B to 14B models at full context comfortably; 30B class models want 48 GB or two cards. I will size it from the eval results, not from a spec sheet.

Timeline: week one, workflow inventory, routing matrix, and a working gateway against mock providers so you can see the routing decisions on your tasks; week two, vLLM deployment, Perplexity integration, logging and the cost report; week three, RAG ingestion, the evaluation report, documentation and a handoff session.

Two questions so I scope it right: which open-weight models have you already tried, if any, and roughly how many documents and requests a day are we routing?

James

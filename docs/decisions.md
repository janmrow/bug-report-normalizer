# Decisions

This document captures the main engineering decisions for the MVP.

## 1. CLI first, no web UI

Why:
- keeps the project small,
- makes the end-to-end flow easy to understand,
- reduces non-essential UI work,
- keeps the focus on LLM integration and testing strategy.

Trade-off:
- less visually impressive than a web app,
- but much stronger for scope control.

## 2. Contract first, prompt second

Why:
- the output contract is the source of truth,
- the model should produce data that fits our schema,
- validation belongs to our code, not to model optimism.

Trade-off:
- slightly more upfront work,
- but much better testability and failure handling.

## 3. Ollama as the only provider in MVP

Why:
- enough to learn real local LLM integration,
- avoids premature multi-provider abstraction,
- keeps the request/response boundary visible.

Trade-off:
- less feature breadth,
- but better clarity and less scope creep.

## 4. Structured JSON output validated with Pydantic

Why:
- easier contract testing,
- easier rendering,
- easier future integration,
- much better than parsing loose prose.

Trade-off:
- the model can still fail to respect the contract,
- but those failures are explicit and testable.

## 5. Simple HTTP client over heavy SDK abstraction

Why:
- makes the network boundary obvious,
- keeps the integration educational,
- simplifies testing and reasoning about failures.

Trade-off:
- a bit more manual code,
- but clearer ownership of request and response handling.

## 6. Minimal integration tests, strong deterministic tests

Why:
- LLM behavior is nondeterministic,
- deterministic layers should carry most of the quality burden,
- integration tests should confirm the real path, not define correctness word-for-word.

Trade-off:
- less confidence in exact phrasing,
- but much better long-term stability.

## 7. Honest failure over silent fallback

Why:
- invalid JSON should fail clearly,
- contract mismatch should fail clearly,
- debugging is easier when errors are visible.

Trade-off:
- fewer "rescued" responses,
- but a much more trustworthy MVP.

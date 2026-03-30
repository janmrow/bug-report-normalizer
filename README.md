# Bug Report Normalizer

Bug Report Normalizer is a small Python CLI tool that turns messy, incomplete bug notes into a structured draft bug report.

## Why this project exists

Bug reports are often written as raw notes:

- incomplete,
- chaotic,
- mixed with guesses,
- missing reproduction steps,
- missing environment details,
- missing key information needed by QA or developers.

This project explores a pragmatic LLM use case:

raw bug note -> structured draft bug report + missing information list

The tool is intentionally small and heavily designed for testability.

## Product goal

The goal is not to let the model invent facts.

The goal is to:

- structure what is actually present,
- preserve useful signals from the source note,
- identify what is still missing,
- validate the final output against a clear data contract.

## MVP scope

Input:

- raw bug note from a user

Output:

- `title`
- `summary`
- `observed_behavior`
- `steps_to_reproduce`
- `environment`
- `missing_information`

Possible extension later:

- `follow_up_questions`

Out of scope for MVP:

- web UI
- database
- auth
- Jira integration
- Slack integration
- RAG
- multi-provider support as a product feature
- prompt over-optimization
- heavy infrastructure

## Engineering goals

This project is meant to show:

- pragmatic LLM integration,
- contract-first thinking,
- validation with Pydantic,
- thoughtful testing of a system with a nondeterministic component,
- clean, small-scope engineering.

## Planned architecture

```text
bug-report-normalizer/
├─ src/
│  └─ bug_report_normalizer/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ exceptions.py
│     ├─ llm_client.py
│     ├─ models.py
│     ├─ prompts.py
│     └─ service.py
├─ tests/
│  ├─ unit/
│  ├─ contract/
│  ├─ integration/
│  ├─ fixtures/
│  └─ fakes.py
├─ docs/
├─ .env.example
├─ README.md
├─ pyproject.toml
└─ .gitignore
```

Current implemented layers:

- package bootstrap
- CLI skeleton
- data contract with Pydantic models
- model validation tests
- initial contract tests
- prompt builder
- Ollama client
- fake client for testing higher layers
- application service that parses and validates LLM output

Next planned step:

- CLI input handling
- JSON rendering
- reading from argument, file, or stdin
- user-facing error handling
- CLI tests

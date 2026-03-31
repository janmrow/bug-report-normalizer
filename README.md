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
│     ├─ renderer.py
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
- CLI entrypoint
- data contract with Pydantic models
- prompt builder
- Ollama client
- application service
- JSON and text rendering
- CLI input handling from argument, file, or stdin
- unit and contract tests for the deterministic layers

Next planned step:

- small regression dataset
- contract and smoke integration tests
- architecture notes in `docs/decisions.md`
- README polish for portfolio presentation

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Configuration

You can configure the model and Ollama base URL with environment variables:

```bash
export OLLAMA_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

## Run checks

```bash
pytest
ruff check .
ruff format --check .
```

## CLI usage

Pass the raw note directly:

```bash
bug-report-normalizer \
  --model "$OLLAMA_MODEL" \
  --note "Checkout is broken. Spinner stays forever after clicking Pay now on Safari on iPhone."
```

Read the note from a file:

```bash
bug-report-normalizer \
  --model "$OLLAMA_MODEL" \
  --input-file ./examples/checkout-note.txt
```

Pipe the note through stdin:

```bash
cat ./examples/checkout-note.txt | bug-report-normalizer --model "$OLLAMA_MODEL"
```

Render human-readable text instead of JSON:

```bash
bug-report-normalizer \
  --model "$OLLAMA_MODEL" \
  --output-format text \
  --note "Search page looks broken. Empty results for known products on Chrome."
```

You can also run the package directly:

```bash
python -m bug_report_normalizer --model "$OLLAMA_MODEL" --note "Login button does nothing."
```

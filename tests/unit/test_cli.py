from __future__ import annotations

import io

from bug_report_normalizer import cli
from bug_report_normalizer.models import BugReportDraft, EnvironmentInfo


def _sample_draft() -> BugReportDraft:
    return BugReportDraft(
        title="Search returns no results",
        summary="Searching for a known item returns an empty state.",
        observed_behavior="Results list stays empty.",
        steps_to_reproduce=[
            "Open search page",
            "Enter a known product name",
            "Press Enter",
        ],
        environment=EnvironmentInfo(
            environment_name="staging",
            browser="Chrome",
            operating_system="Ubuntu 24.04",
            device="desktop",
        ),
        missing_information=[
            "Whether the issue is reproducible every time",
        ],
    )


class DummyOllamaClient:
    def __init__(self, *, model: str, base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url


def test_build_parser_has_expected_program_name() -> None:
    parser = cli.build_parser()
    assert parser.prog == "bug-report-normalizer"


def test_main_reads_note_argument_and_renders_json(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_draft_bug_report(*, raw_note: str, client: object) -> BugReportDraft:
        captured["raw_note"] = raw_note
        captured["client"] = client
        return _sample_draft()

    monkeypatch.setattr(cli, "OllamaClient", DummyOllamaClient)
    monkeypatch.setattr(cli, "draft_bug_report", fake_draft_bug_report)

    exit_code = cli.main(
        [
            "--note",
            "Search page looks broken.",
            "--model",
            "llama3.2",
        ]
    )

    captured_output = capsys.readouterr()

    assert exit_code == 0
    assert '"title": "Search returns no results"' in captured_output.out
    assert captured_output.err == ""
    assert captured["raw_note"] == "Search page looks broken."
    assert isinstance(captured["client"], DummyOllamaClient)
    assert captured["client"].model == "llama3.2"


def test_main_reads_note_from_file(monkeypatch, tmp_path, capsys) -> None:
    note_file = tmp_path / "note.txt"
    note_file.write_text("Checkout looks broken on Firefox.", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_draft_bug_report(*, raw_note: str, client: object) -> BugReportDraft:
        captured["raw_note"] = raw_note
        return _sample_draft()

    monkeypatch.setattr(cli, "OllamaClient", DummyOllamaClient)
    monkeypatch.setattr(cli, "draft_bug_report", fake_draft_bug_report)

    exit_code = cli.main(
        [
            "--input-file",
            str(note_file),
            "--model",
            "llama3.2",
        ]
    )

    captured_output = capsys.readouterr()

    assert exit_code == 0
    assert captured["raw_note"] == "Checkout looks broken on Firefox."
    assert captured_output.err == ""


def test_main_reads_note_from_stdin_when_no_note_flags_are_used(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_draft_bug_report(*, raw_note: str, client: object) -> BugReportDraft:
        captured["raw_note"] = raw_note
        return _sample_draft()

    monkeypatch.setattr(cli, "OllamaClient", DummyOllamaClient)
    monkeypatch.setattr(cli, "draft_bug_report", fake_draft_bug_report)

    exit_code = cli.main(
        ["--model", "llama3.2"],
        stdin=io.StringIO("Profile page is blank on Chrome."),
    )

    captured_output = capsys.readouterr()

    assert exit_code == 0
    assert captured["raw_note"] == "Profile page is blank on Chrome."
    assert captured_output.err == ""


def test_main_renders_text_output(monkeypatch, capsys) -> None:
    def fake_draft_bug_report(*, raw_note: str, client: object) -> BugReportDraft:
        return _sample_draft()

    monkeypatch.setattr(cli, "OllamaClient", DummyOllamaClient)
    monkeypatch.setattr(cli, "draft_bug_report", fake_draft_bug_report)

    exit_code = cli.main(
        [
            "--note",
            "Search page looks broken.",
            "--model",
            "llama3.2",
            "--output-format",
            "text",
        ]
    )

    captured_output = capsys.readouterr()

    assert exit_code == 0
    assert "Title:" in captured_output.out
    assert "Summary:" in captured_output.out
    assert '"title":' not in captured_output.out


def test_main_returns_error_when_model_is_missing(monkeypatch, capsys) -> None:
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    exit_code = cli.main(
        ["--note", "Login is broken."],
    )

    captured_output = capsys.readouterr()

    assert exit_code == 1
    assert "Provide the Ollama model" in captured_output.err


def test_main_returns_error_when_no_input_is_provided(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "OllamaClient", DummyOllamaClient)

    exit_code = cli.main(
        ["--model", "llama3.2"],
        stdin=io.StringIO(""),
    )

    captured_output = capsys.readouterr()

    assert exit_code == 1
    assert "Bug note input must not be empty." in captured_output.err

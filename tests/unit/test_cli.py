from bug_report_normalizer.cli import build_parser, main


def test_build_parser_has_expected_program_name() -> None:
    parser = build_parser()
    assert parser.prog == "bug-report-normalizer"


def test_main_returns_zero_and_prints_bootstrap_message(capsys) -> None:
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Bootstrap complete" in captured.out

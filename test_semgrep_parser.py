from analyzers.semgrep_runner import run_semgrep
from parsers.semgrep_parser import parse_semgrep

issues = parse_semgrep(
    run_semgrep(
        "app.py",
        set(),
        config="semgrep_test_rule.yml"
    )
)

print(issues)
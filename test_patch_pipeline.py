import sys

from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep

from patch_engine.extractor import extract_code_block
from patch_engine.validator import validate_patch
from patch_engine.replacer import replace_code_block

from auto_fix_engine import generate_patch


# ==========================================
# Configuration
# ==========================================

SUPPORTED_RULES = {
    "E722",
    "B105",
    "B307",
    "no-eval",
}

TARGET_FILE = "app.py"
MAX_ITERATIONS = 20

fixed_count = 0
failed_issues = set()


# ==========================================
# Re-analysis Loop
# ==========================================

for iteration in range(1, MAX_ITERATIONS + 1):

    print("\n" + "=" * 60)
    print(f"SCAN ITERATION {iteration}")
    print("=" * 60)

    # --------------------------------------
    # Run Ruff
    # --------------------------------------

    ruff_issues = parse_ruff(
        run_ruff([TARGET_FILE])
    )

    # --------------------------------------
    # Run Bandit
    # --------------------------------------

    bandit_issues = parse_bandit(
        run_bandit([TARGET_FILE])
    )

    # --------------------------------------
    # Run Semgrep
    # --------------------------------------

    semgrep_issues = parse_semgrep(
        run_semgrep(
            TARGET_FILE,
            set(),
            config="semgrep_test_rule.yml"
        )
    )

    # --------------------------------------
    # Collect Issues
    # --------------------------------------

    issues = (
        ruff_issues +
        bandit_issues +
        semgrep_issues
    )

    # Remove previously failed issues

    issues = [
        issue
        for issue in issues
        if (
            issue["rule"],
            issue["message"],
            issue["file"],
        ) not in failed_issues
    ]

    if not issues:

        print("\n✔ No remaining fixable issues.")
        break

    issue = issues[0]

    print("\n" + "=" * 60)
    print("ISSUE FOUND")
    print("=" * 60)
    print(issue)

    # --------------------------------------
    # Extract Code Block
    # --------------------------------------

    block = extract_code_block(
        issue["file"],
        issue["line"]
    )

    code_block = block["code"]

    if not code_block.strip():

        print(f"⚠ Could not extract block for {issue['rule']}")

        failed_issues.add(
            (
                issue["rule"],
                issue["message"],
                issue["file"],
            )
        )

        continue

    print("\n" + "=" * 60)
    print("EXTRACTED BLOCK")
    print("=" * 60)
    print(code_block)

    # --------------------------------------
    # Skip unsupported rules
    # --------------------------------------

    if issue["rule"] not in SUPPORTED_RULES:

        print(f"⚠ Skipping unsupported rule: {issue['rule']}")

        failed_issues.add(
            (
                issue["rule"],
                issue["message"],
                issue["file"],
            )
        )

        continue

    # --------------------------------------
    # Generate Patch
    # --------------------------------------

    fixed_block = generate_patch(
        f"{issue['rule']}: {issue['message']}",
        code_block
    )

    print("\n" + "=" * 60)
    print("GENERATED PATCH")
    print("=" * 60)
    print(fixed_block)

    # --------------------------------------
    # Validate Patch
    # --------------------------------------

    valid, message = validate_patch(
        fixed_block
    )

    print("\n" + "=" * 60)
    print("PATCH VALIDATION")
    print("=" * 60)
    print(message)

    if not valid:

        print("❌ Validation failed.")

        failed_issues.add(
            (
                issue["rule"],
                issue["message"],
                issue["file"],
            )
        )

        continue

    # --------------------------------------
    # Skip unchanged patch
    # --------------------------------------

    if code_block.strip() == fixed_block.strip():

        print(f"⚠ Skipping {issue['rule']} (AI returned original code)")

        failed_issues.add(
            (
                issue["rule"],
                issue["message"],
                issue["file"],
            )
        )

        continue

    # --------------------------------------
    # Replace Code Block
    # --------------------------------------

    print("\nApplying patch...\n")

    success = replace_code_block(
        issue["file"],
        code_block,
        fixed_block,
    )

    if success:

        fixed_count += 1

        print(f"✔ Fixed {issue['rule']}")

    else:

        print("❌ Failed to replace code block.")

        failed_issues.add(
            (
                issue["rule"],
                issue["message"],
                issue["file"],
            )
        )


# ==========================================
# Summary
# ==========================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"Iterations          : {iteration}")
print(f"Issues Fixed        : {fixed_count}")
print(f"Failed Issues       : {len(failed_issues)}")

if failed_issues:

    print("\nSkipped:")

    for rule, message, _ in sorted(failed_issues):

        print(f"- {rule}: {message}")
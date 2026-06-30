import sys

from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit

# Uncomment after Semgrep integration
# from analyzers.semgrep_runner import run_semgrep
# from parsers.semgrep_parser import parse_semgrep

from patch_engine.extractor import extract_code_block
from patch_engine.validator import validate_patch
from patch_engine.replacer import replace_code_block

from auto_fix_engine import generate_patch


# ==========================================
# Run Ruff
# ==========================================

ruff_issues = parse_ruff(
    run_ruff(["app.py"])
)

# ==========================================
# Run Bandit
# ==========================================

bandit_issues = parse_bandit(
    run_bandit(["app.py"])
)

# ==========================================
# Run Semgrep
# ==========================================

# semgrep_issues = parse_semgrep(
#     run_semgrep(".", set())
# )

semgrep_issues = []

# ==========================================
# Collect Issues
# ==========================================

issues = (
    ruff_issues +
    bandit_issues +
    semgrep_issues
)

if not issues:
    print("✔ No issues found.")
    sys.exit(0)

# ==========================================
# Process Issues
# ==========================================

for issue in issues:

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

    print("\n" + "=" * 60)
    print("EXTRACTED BLOCK")
    print("=" * 60)
    print(code_block)

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

    valid, message = validate_patch(fixed_block)

    print("\n" + "=" * 60)
    print("PATCH VALIDATION")
    print("=" * 60)
    print(message)

    if not valid:
        print("❌ Validation failed.")
        continue
    
    # --------------------------------------
    # Skip unchanged patch
    # --------------------------------------

    clean_original = code_block.strip()
    clean_fixed = fixed_block.strip()

    if clean_original == clean_fixed:

        print(f"⚠ Skipping {issue['rule']} (AI did not generate a valid fix.)")

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
        print(f"✔ Fixed {issue['rule']}")
    else:
        print("❌ Failed to replace code block.")
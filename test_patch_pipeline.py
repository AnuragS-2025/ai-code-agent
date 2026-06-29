import sys

from analyzers.ruff_runner import run_ruff
from parsers.ruff_parser import parse_ruff

from patch_engine.extractor import extract_code_block
from patch_engine.validator import validate_patch
from patch_engine.replacer import replace_code_block

from auto_fix_engine import generate_patch


# ==========================================
# Run Ruff
# ==========================================

issues = parse_ruff(
    run_ruff(["app.py"])
)

if not issues:
    print("✔ No Ruff issues found.")
    sys.exit(0)

issue = issues[0]

print("=" * 60)
print("ISSUE FOUND")
print("=" * 60)
print(issue)

# ==========================================
# Extract Code Block
# ==========================================

block = extract_code_block(
    issue["file"],
    issue["line"]
)

code_block = block["code"]

print("\n" + "=" * 60)
print("EXTRACTED BLOCK")
print("=" * 60)
print(code_block)

# ==========================================
# Generate Patch
# ==========================================

fixed_block = generate_patch(
    issue["message"],
    code_block
)

print("\n" + "=" * 60)
print("GENERATED PATCH")
print("=" * 60)
print(fixed_block)

# ==========================================
# Validate Patch
# ==========================================

valid, message = validate_patch(fixed_block)

print("\n" + "=" * 60)
print("PATCH VALIDATION")
print("=" * 60)
print(message)

if not valid:
    print("\n❌ Patch validation failed.")
    sys.exit(1)

# ==========================================
# Replace Code Block
# ==========================================

print("\nApplying patch...\n")

success = replace_code_block(
    issue["file"],
    code_block,
    fixed_block,
)

if success:
    print("✔ Patch applied successfully.")
else:
    print("❌ Failed to replace code block.")
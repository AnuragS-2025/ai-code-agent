import ast
import difflib
import os
import shutil
import sys

from auto_fix_engine import fix_code

from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep


print("=" * 60)
print("               AI AUTO FIX AGENT")
print("=" * 60)
print()

# ==========================================
# Check Arguments
# ==========================================

if len(sys.argv) != 2:
    print("Usage:")
    print("python auto_fix.py <python_file>")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.isfile(filename):
    print(f"❌ File not found: {filename}")
    sys.exit(1)

# ==========================================
# Read File
# ==========================================

print(f"[✓] Reading file: {filename}")

with open(filename, "r", encoding="utf-8") as file:
    code = file.read()

print("✔ File loaded successfully.\n")

# ==========================================
# Create Backup
# ==========================================

backup_file = filename + ".bak"

shutil.copy2(filename, backup_file)

print(f"[✓] Backup created: {backup_file}\n")

# ==========================================
# Analyze File
# ==========================================

print("[✓] Running analyzers...\n")

python_files = [filename]

ruff_report = parse_ruff(
    run_ruff(python_files)
)

bandit_report = parse_bandit(
    run_bandit(python_files)
)

semgrep_report = parse_semgrep(
    run_semgrep(".", set())
)

print("✔ Analysis completed.\n")

# ==========================================
# AI Fix
# ==========================================

print("[✓] Generating AI Fix...\n")

fixed_code = fix_code(
    code,
    ruff_report,
    bandit_report,
    semgrep_report
)
# ==========================================
# Generated Code Preview
# ==========================================

print("\nGenerated Code Preview")
print("=" * 60)
print(fixed_code)
print("=" * 60)
# ==========================================
# Syntax Validation
# ==========================================

print("[✓] Validating generated code...\n")

try:
    ast.parse(fixed_code)
    print("✔ Syntax validation passed.\n")

except SyntaxError as e:

    print("\n❌ Invalid Python code generated.\n")

    print(f"Line   : {e.lineno}")
    print(f"Offset : {e.offset}")
    print(f"Reason : {e.msg}")

    lines = fixed_code.splitlines()

    start = max(0, e.lineno - 3)
    end = min(len(lines), e.lineno + 2)

    print("\nCode Around Error")
    print("=" * 60)

    for i in range(start, end):
        print(f"{i + 1}: {lines[i]}")

    print("=" * 60)

    print("\nOriginal file preserved.")
    sys.exit(1)

print("✔ Syntax validation passed.\n")

# ==========================================
# Diff Preview
# ==========================================

print("=" * 60)
print("                 DIFF PREVIEW")
print("=" * 60)

diff = difflib.unified_diff(
    code.splitlines(),
    fixed_code.splitlines(),
    fromfile="Original",
    tofile="Fixed",
    lineterm=""
)

for line in diff:
    print(line)

print("=" * 60)

# ==========================================
# Apply Fix
# ==========================================

choice = input("\nApply this fix? (y/n): ").strip().lower()

if choice != "y":
    print("\n❌ Fix cancelled.")
    print(f"Original file preserved: {filename}")
    print(f"Backup available: {backup_file}")

    print("\n" + "=" * 60)
    print("               FIX CANCELLED")
    print("=" * 60)

    sys.exit(0)

print("\nApplying fix...\n")

with open(filename, "w", encoding="utf-8") as file:
    file.write(fixed_code)

print(f"✔ Fixed code written to {filename}")
print(f"✔ Backup available at: {backup_file}")

# ==========================================
# Completed
# ==========================================

print("\n" + "=" * 60)
print("               FIX COMPLETED")
print("=" * 60)
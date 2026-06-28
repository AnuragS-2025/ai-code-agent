import os
import sys

from langchain_ollama import ChatOllama

from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep


# ==========================================
# Configuration
# ==========================================

DEFAULT_PROJECT = "codebase"

PROJECT_PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROJECT

if not os.path.exists(PROJECT_PATH):
    print(f"\n❌ Project folder '{PROJECT_PATH}' not found.")
    sys.exit(1)

EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    "node_modules"
}

if PROJECT_PATH == ".":
    EXCLUDE_DIRS.add("codebase")

python_files = []

# ==========================================
# Collect Python Files
# ==========================================

print("\n[✓] Collecting project files...\n")

for root, dirs, files in os.walk(PROJECT_PATH):

    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for file in files:

        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

print(f"Found {len(python_files)} Python files.\n")

if not python_files:
    print("❌ No Python files found.")
    sys.exit(1)

# ==========================================
# Run Analyzers
# ==========================================

ruff_output = run_ruff(python_files)

bandit_output = run_bandit(python_files)

semgrep_output = run_semgrep(
    PROJECT_PATH,
    EXCLUDE_DIRS
)

# ==========================================
# Parse Reports
# ==========================================

print("[✓] Parsing reports...\n")

ruff_summary = parse_ruff(ruff_output)

bandit_summary = parse_bandit(bandit_output)

semgrep_summary = parse_semgrep(semgrep_output)

print("✔ Reports parsed successfully.\n")

# ==========================================
# AI Summary
# ==========================================

print("[✓] Generating AI Summary...\n")

llm = ChatOllama(
    model="llama3.2:3b"
)

prompt = f"""
You are an expert software engineer.

You are given parsed summaries from static analysis tools.

The summaries are already parsed and classified.

Do NOT reinterpret the findings.

Only generate a concise project review.

Instructions:

- Merge duplicate issues by rule ID.
- Do NOT repeat the same issue.
- Do NOT invent new issues.
- Do NOT copy raw scanner output.
- Summarize findings in simple English.

Classification Rules:

- Ruff issues belong ONLY to Quality Issues.
- Bandit issues belong ONLY to Security Issues.
- Semgrep findings belong ONLY to Semgrep Findings.

Reporting Rules:

- Mention only file names (never absolute paths).
- Do NOT exaggerate security risks.
- Describe only what the analysis tools report.
- Do NOT invent attack scenarios.
- If a rule affects multiple files, group them into one bullet.
- If Ruff reports no issues, write "No quality issues found."
- If Bandit reports no issues, write "No security issues found."
- If Semgrep reports no findings, write "No Semgrep findings."
- Keep the report concise.
- Maximum 2 bullet points per section.

Return ONLY this format.

Quality Issues
--------------

- ...

Security Issues
---------------

- ...

Semgrep Findings
----------------

- ...

Recommended Fixes
----------------

- ...

Project:
{PROJECT_PATH}

Ruff Summary:
{ruff_summary}

Bandit Summary:
{bandit_summary}

Semgrep Summary:
{semgrep_summary}
"""

response = llm.invoke(prompt)

# ==========================================
# Final Report
# ==========================================

print("\n" + "=" * 60)
print("                 AI PROJECT REVIEW")
print("=" * 60)
print()

print(response.content)

print()

print("=" * 60)
print("                 REVIEW COMPLETED")
print("=" * 60)
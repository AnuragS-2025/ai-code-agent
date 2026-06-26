import os
import sys
import subprocess
from langchain_ollama import ChatOllama

# ==========================================
# Configuration
# ==========================================

DEFAULT_PROJECT = "codebase"

if len(sys.argv) > 1:
    PROJECT_PATH = sys.argv[1]
else:
    PROJECT_PATH = DEFAULT_PROJECT

if not os.path.exists(PROJECT_PATH):
    print(f"\n❌ Project folder '{PROJECT_PATH}' not found.")
    sys.exit(1)

EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    "node_modules"
}

# Developer mode me codebase skip karo
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

print(f"Found {len(python_files)} Python files in '{PROJECT_PATH}'.\n")

if not python_files:
    print("❌ No Python files found.")
    sys.exit(1)

# ==========================================
# Ruff
# ==========================================

print("[✓] Running Ruff...\n")

ruff = subprocess.run(
    ["ruff", "check"] + python_files,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

ruff_output = ruff.stdout + ruff.stderr

print("✔ Ruff analysis completed.\n")

# ==========================================
# Bandit
# ==========================================

print("[✓] Running Bandit...\n")

bandit = subprocess.run(
    ["bandit"] + python_files,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

bandit_output = bandit.stdout + bandit.stderr

print("✔ Bandit analysis completed.\n")

# ==========================================
# Semgrep
# ==========================================

print("[✓] Running Semgrep...\n")

semgrep_command = [
    "semgrep",
    "scan",
    "--config=auto",
    PROJECT_PATH,
]

for directory in EXCLUDE_DIRS:
    semgrep_command.extend(["--exclude", directory])

semgrep = subprocess.run(
    semgrep_command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace"
)

semgrep_output = semgrep.stdout + semgrep.stderr

print("✔ Semgrep analysis completed.\n")

# ==========================================
# AI Summary
# ==========================================

print("[✓] Generating AI Summary...\n")

llm = ChatOllama(
    model="llama3.2:3b"
)

prompt = f"""
You are an expert software engineer.

Analyze the following reports.

Instructions:

- Merge duplicate issues.
- Ignore informational messages.
- Mention only real issues.
- If a tool reports no issues, clearly say so.
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
-----------------

- ...

Project:
{PROJECT_PATH}

Ruff Report:
{ruff_output}

Bandit Report:
{bandit_output}

Semgrep Report:
{semgrep_output}
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
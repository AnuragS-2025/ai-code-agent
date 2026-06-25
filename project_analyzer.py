import os
import subprocess
from langchain_ollama import ChatOllama

# ==========================================
# Configuration
# ==========================================

EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    "node_modules"
}

python_files = []

# ==========================================
# Collect Python Files
# ==========================================

print("\n[✓] Collecting project files...\n")

for root, dirs, files in os.walk("."):

    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for file in files:

        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

print(f"Found {len(python_files)} Python files.\n")

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

semgrep = subprocess.run(
    [
        "semgrep",
        "scan",
        "--config=auto",
        "."
    ],
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

Analyze the following reports:

1. Ruff
2. Bandit
3. Semgrep

Instructions:

- Do NOT print a title.
- Merge duplicate issues.
- Ignore informational messages.
- Mention only real issues.
- If a tool reports no issues, clearly mention it.
- Do NOT recommend removing required imports.
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
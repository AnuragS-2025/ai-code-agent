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
# Run Ruff
# ==========================================

print("[✓] Running Ruff...\n")

ruff_result = subprocess.run(
    ["ruff", "check"] + python_files,
    capture_output=True,
    text=True,
)

ruff_output = ruff_result.stdout + ruff_result.stderr

print("✔ Ruff analysis completed.\n")

# ==========================================
# Run Bandit
# ==========================================

print("[✓] Running Bandit...\n")

bandit_result = subprocess.run(
    ["bandit"] + python_files,
    capture_output=True,
    text=True,
)

bandit_output = bandit_result.stdout + bandit_result.stderr

print("✔ Bandit analysis completed.\n")

# ==========================================
# Generate AI Summary
# ==========================================

print("[✓] Generating AI Summary...\n")

llm = ChatOllama(
    model="llama3.2:3b"
)

prompt = f"""
You are an expert software engineer.

Analyze the Ruff and Bandit reports.

Instructions:

1. Do NOT print any title.
2. Do NOT repeat raw Ruff or Bandit output.
3. Merge duplicate issues.
4. Do NOT suggest removing required imports.
5. Do NOT repeat the same filename multiple times.
6. Keep the report concise.
7. Maximum 2 bullet points per section.
8. Suggest only practical fixes.

Return ONLY this format.

Quality Issues
--------------

- ...

Security Issues
---------------

- ...

Recommended Fixes
-----------------

- ...

Ruff Report:
{ruff_output}

Bandit Report:
{bandit_output}
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
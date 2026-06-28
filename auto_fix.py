import os
import sys
from langchain_ollama import ChatOllama

print("=" * 50)
print("          AI AUTO FIX AGENT")
print("=" * 50)
print()

# -----------------------------------------
# Get filename
# -----------------------------------------

if len(sys.argv) != 2:
    print("Usage:")
    print("python auto_fix.py <python_file>")
    sys.exit(1)

filename = sys.argv[1]

# -----------------------------------------
# Check file exists
# -----------------------------------------

if not os.path.isfile(filename):
    print(f"❌ File not found: {filename}")
    sys.exit(1)

# -----------------------------------------
# Read file
# -----------------------------------------

print(f"Reading file: {filename}\n")

with open(filename, "r", encoding="utf-8") as file:
    code = file.read()

print("✅ File loaded successfully.\n")

# -----------------------------------------
# Create Backup
# -----------------------------------------

backup_file = filename + ".bak"

with open(backup_file, "w", encoding="utf-8") as backup:
    backup.write(code)

print(f"✅ Backup created: {backup_file}\n")

# -----------------------------------------
# Load AI
# -----------------------------------------

print("Loading AI...\n")

llm = ChatOllama(
    model="llama3.2:3b"
)

# -----------------------------------------
# AI Prompt
# -----------------------------------------

prompt = f"""
You are an expert Python software engineer.

Your task is to fix the following Python code.

Rules:

- Return ONLY corrected Python code.
- Do NOT explain anything.
- Do NOT use markdown.
- Do NOT use ``` blocks.
- Preserve the original functionality.
- Fix Ruff issues.
- Fix Bandit issues.
- Fix Semgrep issues if applicable.
- Improve formatting only when necessary.

Python Code:

{code}
"""

print("Generating fixed code...\n")

response = llm.invoke(prompt)

fixed_code = response.content

fixed_code = fixed_code.replace("```python", "")
fixed_code = fixed_code.replace("```", "")
fixed_code = fixed_code.strip()

# -----------------------------------------
# Show AI Output
# -----------------------------------------

print("=" * 60)
print("               AI GENERATED FIX")
print("=" * 60)
print()

print(fixed_code)

print()

print("=" * 60)
print("               END OF FIX")
print("=" * 60)
import subprocess
from langchain_ollama import ChatOllama

print("Running Ruff...")

result = subprocess.run(
    ["ruff", "check", "."],
    capture_output=True,
    text=True
)

ruff_output = result.stdout + result.stderr

print("\nRuff Output:\n")
print(ruff_output)

print("\nLoading AI...")

llm = ChatOllama(model="llama3.2:3b")

prompt = f"""
You are an expert software engineer.

Create a professional code review report.

Use EXACTLY this format:

==========================================
AI CODE REVIEW REPORT
==========================================

Issue #1

File:
...

Line:
...

Rule:
...

Problem:
...

Suggested Fix:
...

------------------------------------------

Repeat this format for every issue.

Do not write everything in one line.

Ruff Report:

{ruff_output}
"""

response = llm.invoke(prompt)

print("\nAI Review:\n")

print(response.content)
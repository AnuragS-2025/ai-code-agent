from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b"
)


def fix_code(code: str) -> str:
    """
    Generates an improved version of the given code.
    """

    prompt = f"""
You are an expert Python software engineer.

Improve the following Python code.

Rules:

- Return ONLY Python code.
- No markdown.
- No explanations.
- Preserve functionality.
- Improve readability.
- Do not remove required imports.
- Do not introduce new features.

Code:

{code}
"""

    response = llm.invoke(prompt)

    fixed_code = response.content

    fixed_code = (
        fixed_code
        .replace("```python", "")
        .replace("```", "")
        .strip()
    )

    return fixed_code
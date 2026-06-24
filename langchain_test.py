from langchain_ollama import ChatOllama
from file_reader import read_codebase

print("Reading codebase...")

context = read_codebase()

print("Loading model...")

llm = ChatOllama(model="llama3.2:3b")

user_prompt = """
Add a POST endpoint /users.

Return only the code change.
Follow existing FastAPI style.
"""

final_prompt = f"""
You are an AI coding assistant.

Project codebase:

{context}

Question:
{user_prompt}
"""

response = llm.invoke(final_prompt)

print("\nAI Response:\n")
print(response.content)
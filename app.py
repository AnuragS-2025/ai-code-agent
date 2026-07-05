from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer
import chromadb
import os

app = FastAPI()

# -----------------------------
# Load Models
# -----------------------------
print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading LLM...")
llm = ChatOllama(model="llama3.2:3b")

# -----------------------------
# Create Vector Store
# -----------------------------
print("Creating vector store...")

client = chromadb.Client()
collection = client.get_or_create_collection("codebase")

folder = "codebase"

for filename in os.listdir(folder):

    filepath = os.path.join(folder, filename)

    if os.path.isfile(filepath):

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        embedding = embedding_model.encode(content).tolist()

        try:
            collection.delete(ids=[filename])
        except Exception:
            pass

        collection.add(
            ids=[filename],
            embeddings=[embedding],
            documents=[content]
        )

print("Codebase indexed.")

# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "AI Agent with Hybrid RAG Running"
    }

# -----------------------------
# Hybrid Generate Endpoint
# -----------------------------
@app.get("/generate")
def generate(prompt: str):

    repo_keywords = [
        "database",
        "project",
        "codebase",
        "file",
        "endpoint",
        "app.py",
        "database.py",
        "framework",
        "repository",
        "configuration"
    ]

    use_rag = any(
        keyword.lower() in prompt.lower()
        for keyword in repo_keywords
    )

    if use_rag:

        query_embedding = embedding_model.encode(prompt).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )

        context = results["documents"][0][0]

        final_prompt = f"""
Use the following project context.

Context:
{context}

Question:
{prompt}

Answer only from the given context.
"""

        response = llm.invoke(final_prompt)

        return {
            "mode": "RAG",
            "response": response.content
        }

    response = llm.invoke(prompt)

    return {
        "mode": "LLM",
        "response": response.content
    }


# -----------------------------
# Plain Code Generation
# -----------------------------
@app.get("/generate_code", response_class=PlainTextResponse)
def generate_code(prompt: str):

    system_prompt = f"""
You are an expert programmer.

Return ONLY executable code.

Rules:
- No markdown
- No headings
- No explanations
- No ``` blocks
- Only code

Task:

{prompt}
"""

    response = llm.invoke(system_prompt)

    code = response.content
    code = code.replace("```python", "")
    code = code.replace("```", "")
    code = code.strip()

    return code


# -----------------------------
# Generate and Save
# -----------------------------
@app.get("/generate_and_save")
def generate_and_save(prompt: str):

    system_prompt = f"""
You are an expert software engineer.

Generate COMPLETE executable code.

Rules:
- Return only code.
- No markdown.
- No explanation.
- Include imports.
- Include example usage.
- If Python, include:

if __name__ == "__main__":
    ...

Task:

{prompt}
"""

    response = llm.invoke(system_prompt)

    code = response.content

    code = code.replace("```python", "")
    code = code.replace("```", "")
    code = code.strip()

    filename = "generated_code.py"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "message": "Code generated and saved successfully.",
        "saved_to": filename
    }
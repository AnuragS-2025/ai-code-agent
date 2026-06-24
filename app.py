from fastapi import FastAPI
from langchain_ollama import ChatOllama
from sentence_transformers import SentenceTransformer
import chromadb
import os

app = FastAPI()

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading LLM...")
llm = ChatOllama(model="llama3.2:3b")

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
        except:
            pass

        collection.add(
            ids=[filename],
            embeddings=[embedding],
            documents=[content]
        )

print("Codebase indexed.")


@app.get("/")
def home():
    return {"message": "AI Agent with RAG Running"}

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
        "used in this project",
        "configuration",
        "repository"
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

Answer based only on the context.
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

Answer based only on the context.
"""

    response = llm.invoke(final_prompt)

    return {
        "response": response.content
    }
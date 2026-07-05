from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
import chromadb
import os

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
        except Exception:
            pass

        collection.add(
            ids=[filename],
            embeddings=[embedding],
            documents=[content]
        )

user_question = "Which database is used in this project?"

query_embedding = embedding_model.encode(user_question).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

context = results["documents"][0][0]

prompt = f"""
Use the following project context.

Context:
{context}

Question:
{user_question}

Answer based only on the context.
"""

response = llm.invoke(prompt)

print("\nAI Response:\n")
print(response.content)
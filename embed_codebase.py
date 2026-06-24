from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client()

collection = client.get_or_create_collection("codebase")

folder = "codebase"

for filename in os.listdir(folder):

    path = os.path.join(folder, filename)

    if os.path.isfile(path):

        with open(path, "r", encoding="utf-8") as f:

            content = f.read()

        embedding = model.encode(content).tolist()

        collection.add(
            ids=[filename],
            embeddings=[embedding],
            documents=[content]
        )

        print(f"Indexed: {filename}")

print("Codebase indexed successfully.")
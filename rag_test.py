from sentence_transformers import SentenceTransformer
import chromadb
import os

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded.")

# Create Chroma client
client = chromadb.Client()

# Create or get collection
collection = client.get_or_create_collection(name="codebase")

print("Indexing files...")

folder = "codebase"

for filename in os.listdir(folder):

    filepath = os.path.join(folder, filename)

    if os.path.isfile(filepath):

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        embedding = model.encode(content).tolist()

        # Delete old entry if exists
        try:
            collection.delete(ids=[filename])
        except:
            pass

        collection.add(
            ids=[filename],
            embeddings=[embedding],
            documents=[content]
        )

        print(f"Indexed: {filename}")

print("Indexing complete.")

# Query
query = "Which database is used in this project?"

print(f"\nQuery: {query}")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

print("\nRetrieved Document:\n")

if results["documents"]:
    print(results["documents"][0][0])
else:
    print("No results found.")
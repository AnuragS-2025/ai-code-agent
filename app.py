from fastapi import FastAPI
from langchain_ollama import ChatOllama

app = FastAPI()

llm = ChatOllama(
    model="llama3.2:3b"
)

@app.get("/")
def home():
    return {"message": "AI Agent Running"}

@app.get("/generate")
def generate(prompt: str):

    response = llm.invoke(prompt)

    return {
        "response": response.content
    }
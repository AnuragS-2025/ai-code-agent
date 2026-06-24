from fastapi import FastAPI
from ollama import chat

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Agent Running"}

@app.get("/generate")
def generate(prompt: str):
    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {"response": response.message.content}
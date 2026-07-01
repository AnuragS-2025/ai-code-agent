from ollama import chat

response = chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Write a Python function to reverse a string"
        }
    ]
)

print(response.message.content)
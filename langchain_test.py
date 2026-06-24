from langchain_ollama import ChatOllama

print("Starting...")

llm = ChatOllama(model="llama3.2:3b")

print("Model loaded...")

response = llm.invoke(
    "Write a Python function to check palindrome"
)

print("Response received...")
print(response.content)
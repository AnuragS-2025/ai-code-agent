# AI Code Agent

AI-powered coding assistant built using Ollama, LangChain, FastAPI, ChromaDB, and Sentence Transformers.

The project runs completely locally without any cloud API dependency. It can understand repository code, perform semantic search using embeddings, and generate context-aware responses using a local LLM.

## Features

* Local LLM execution using Ollama
* LangChain integration
* FastAPI REST API
* Dynamic code generation
* Repository-aware code understanding
* Codebase file reader
* Context-aware code generation
* Basic automated code patching
* Local RAG (Retrieval Augmented Generation)
* ChromaDB vector database
* Sentence Transformer embeddings
* Semantic code search
* Interactive Swagger API documentation
* No cloud API dependency

## Tech Stack

* Python 3.13
* Ollama
* Llama 3.2 (3B)
* LangChain
* FastAPI
* Uvicorn
* ChromaDB
* Sentence Transformers
* Git & GitHub

## Project Structure

```text
ai-code-agent/
│
├── app.py
├── main.py
├── langchain_test.py
├── file_reader.py
├── test_reader.py
├── apply_patch.py
├── test_patch.py
├── embed_codebase.py
├── rag_test.py
├── rag_langchain.py
├── README.md
├── .gitignore
│
├── codebase/
│   ├── app.py
│   └── database.py
│
└── venv/
```

## Architecture

User Prompt
↓
Embedding Model
↓
ChromaDB Search
↓
Relevant Repository Files
↓
LangChain
↓
Ollama
↓
AI Response

## Implemented Milestones

### Phase 1

* Ollama Setup
* Local LLM Integration
* FastAPI Backend
* Dynamic Prompt Endpoint
* GitHub Repository Setup

### Phase 2

* LangChain Integration
* Repository Reader
* Context Injection
* Local Embeddings
* ChromaDB Vector Store
* Semantic Search
* Local RAG Pipeline

### Phase 3 (In Progress)

* Multi-file Context Retrieval
* Repository-aware Code Generation
* Automated Code Patching

## Example Query

Question:

```text
Which database is used in this project?
```

Response:

```text
The SQLite database (sqlite:///test.db) is used in this project.
```

## Future Enhancements

* Semgrep-based Code Review
* Ruff Integration
* AST-based Refactoring
* Automated Test Generation
* Git Automation
* Multi-file Refactoring
* Pull Request Generation

## Author

Anurag Sharan

GitHub: https://github.com/AnuragS-2025

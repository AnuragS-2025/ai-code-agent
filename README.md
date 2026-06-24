# AI Code Agent

AI-powered coding assistant built using Ollama, FastAPI, and LangChain.

## Features

* Local LLM execution using Ollama
* FastAPI REST API
* Dynamic code generation
* No cloud API dependency
* Interactive API documentation

## Tech Stack

* Python 3.13
* Ollama
* Llama 3.2
* FastAPI
* Uvicorn
* LangChain

## Project Structure

```text
ai-code-agent/
│
├── app.py
├── main.py
├── README.md
├── .gitignore
└── venv/
```

## Run the Project

Activate virtual environment:

```bash
venv\Scripts\activate
```

Start FastAPI server:

```bash
python -m uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Current Status

✅ Phase 1 Completed

* Ollama Integration
* FastAPI Integration
* Dynamic Prompt Endpoint
* GitHub Repository Setup

## Author

Anurag Sharan

GitHub: AnuragS-2025

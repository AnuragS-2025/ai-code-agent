# 🤖 AI Code Agent

An AI-powered software engineering assistant built with **Python**, **FastAPI**, **LangChain**, **Ollama**, and **ChromaDB**.

This project goes beyond simple code generation by integrating Retrieval-Augmented Generation (RAG), static code analysis, and AI-assisted project reviews.

---

# 🚀 Features

## ✅ AI Code Generation

* Generate Python code using a local LLM (Ollama)
* Supports custom prompts
* FastAPI REST API

---

## ✅ Hybrid RAG

* Uses ChromaDB as a vector database
* Retrieves project context before generating responses
* Falls back to normal LLM generation when project context is not required

---

## ✅ Smart File Management

* Automatically saves generated code into appropriate source files
* Supports future multi-language expansion

---

## ✅ AI Project Analyzer

Analyzes the entire project using multiple industry-standard tools.

### Ruff

* Python linting
* Code quality analysis
* Style checking

### Bandit

* Security vulnerability detection
* Unsafe coding pattern detection

### Semgrep

* Static code analysis
* Best practices
* Security rule scanning

---

## ✅ AI Review Summary

Instead of showing raw analyzer output, the local LLM generates a concise report including:

* Quality Issues
* Security Issues
* Semgrep Findings
* Recommended Fixes

---

# 🏗 Project Architecture

```text
                AI Code Agent

                       │
                       ▼

            Collect Project Files

                       │

        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼

      Ruff          Bandit        Semgrep

        └──────────────┼──────────────┘
                       │
                       ▼

               AI Project Review

                       │
                       ▼

             Human-readable Summary
```

---

# 🛠 Tech Stack

* Python
* FastAPI
* LangChain
* Ollama
* ChromaDB
* Sentence Transformers
* Ruff
* Bandit
* Semgrep

---

# 📂 Project Structure

```text
ai-code-agent/
│
├── app.py
├── project_analyzer.py
├── file_manager.py
├── code_review.py
├── rag_langchain.py
├── rag_test.py
├── codebase/
├── README.md
└── requirements.txt
```

---

# ▶️ Running the Project

## Clone Repository

```bash
git clone https://github.com/AnuragS-2025/ai-code-agent.git
cd ai-code-agent
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start Ollama

```bash
ollama run llama3.2:3b
```

---

## Start FastAPI

```bash
python -m uvicorn app:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

# 🔍 Analyze the Project

```bash
python project_analyzer.py
```

The analyzer performs:

* Ruff Analysis
* Bandit Security Scan
* Semgrep Scan
* AI-generated Project Review

---

# 📌 Current Progress

## Completed

* Local LLM Integration
* FastAPI API
* LangChain Integration
* Hybrid RAG
* ChromaDB
* Smart File Manager
* AI Code Generation
* Ruff Integration
* Bandit Integration
* Semgrep Integration
* AI Project Analyzer

---

## Planned

* Auto Fix Agent
* AST-based Refactoring
* Docker Support
* Git Automation
* Streamlit Web UI
* Multi-language Code Support
* MCP Integration

---

# 👨‍💻 Author

**Anurag S**

GitHub:

https://github.com/AnuragS-2025

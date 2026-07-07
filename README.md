# 🤖 AI Code Agent

> An AI-powered automated code review and security analysis platform that detects vulnerabilities, generates intelligent fixes, validates patches, and streamlines the secure software development lifecycle.

---

## 🚀 Overview

AI Code Agent is an end-to-end code analysis platform built with **FastAPI**, **LLMs**, and **static analysis tools**. It combines traditional security scanners such as **Bandit** and **Semgrep** with AI-powered patch generation to help developers identify, understand, and fix issues efficiently.

The project also provides REST APIs for rule lookup, scan summaries, automated patch generation, and project analysis, making it suitable for integration into CI/CD pipelines and developer workflows.

---

# ✨ Features

### 🔍 Static Code Analysis

- Python security scanning using **Bandit**
- Rule-based scanning using **Semgrep**
- Project-wide analysis
- Targeted scanning for changed files

---

### 🛡 Security Validation

- Detects security vulnerabilities
- Rule-based issue categorization
- Severity tracking
- Validation reports

---

### 🤖 AI Patch Generation

- Context-aware LLM patch generation
- Prompt engineering for secure fixes
- Patch validation
- Empty patch detection
- Oversized patch detection
- Safety guardrails

---

### 📚 Context Engine

- Project dependency graph
- Code context retrieval
- Intelligent prompt construction
- Dependency-aware analysis

---

### 📂 Project Indexing

- Automatic project scanning
- Python module discovery
- File indexing
- Dependency tracking

---

### 🔎 Rule Search API

Search security rules instantly.

Example:

```
GET /rules/B602
```

Returns

- Rule Title
- Description
- Recommendation

---

### 📊 Scan Summary Dashboard API

Provides

- Total scans
- Total issues
- Issues fixed
- Top triggered rules
- Recent scan history

---

### ⚙ Git Automation

- Git integration
- Automated workflows
- Repository utilities

---

### 💬 Feedback System

Store and manage feedback for generated patches.

---

### 🧪 Test Generation

Utilities for automated testing and validation.

---

### ⚡ GitHub Actions CI

Every Pull Request automatically performs

- Ruff linting
- Bandit security scan
- Unit testing (Pytest)

Bandit scans **only modified Python files**, significantly reducing CI execution time.

---

# 🏗 Architecture

```
                    +----------------------+
                    |      Developer       |
                    +----------+-----------+
                               |
                               |
                         REST API Request
                               |
                               ▼
                     +----------------------+
                     |      FastAPI API     |
                     +----------+-----------+
                                |
    --------------------------------------------------------------
    |             |             |            |           |         |
    ▼             ▼             ▼            ▼           ▼         ▼

Project      Static        Context       Validation     LLM     Reports
 Index       Analysis      Engine         Engine       Engine

    |             |
    ▼             ▼
 Bandit       Semgrep

                |
                ▼

         Patch Generation

                |
                ▼

          Final Response
```

---

# 🛠 Technology Stack

## Backend

- Python 3.12+
- FastAPI
- Pydantic
- Uvicorn

## AI

- LangChain
- Ollama
- LLM Prompt Engineering

## Security

- Bandit
- Semgrep

## Testing

- Pytest

## Code Quality

- Ruff

## CI/CD

- GitHub Actions

---

# 📁 Project Structure

```
ai-code-agent/

│
├── analyzers/
├── api/
├── codebase/
├── config/
├── context_engine/
├── feedback/
├── git_automation/
├── llm/
├── logs/
├── parsers/
├── patch_engine/
├── project_index/
├── test_generator/
├── tests/
├── uploads/
├── utils/
├── validation/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
├── requirements-ci.txt
├── app.py
├── pipeline.py
└── README.md
```

---

# ⚙ Installation

Clone repository

```bash
git clone https://github.com/AnuragS-2025/ai-code-agent.git
```

Move inside project

```bash
cd ai-code-agent
```

Create virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running the API

```bash
uvicorn app:app --reload
```

Swagger

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 📡 API Endpoints

## Health

```
GET /health
```

---

## Scan Project

```
POST /scan
```

Scans uploaded project for vulnerabilities.

---

## Rule Search

```
GET /rules/{rule_id}
```

Example

```
GET /rules/B602
```

---

## Scan Summary

```
GET /summary
```

Returns

- Total scans
- Total issues
- Fixed issues
- Top rules
- Recent scans

---

# 🧪 Running Tests

Run all tests

```bash
python -m pytest
```

Run specific test

```bash
python -m pytest tests/test_llm.py
```

---

# 🔒 Security Scanning

Run Bandit

```bash
bandit -r .
```

Run Bandit on specific files

```bash
bandit file.py
```

Run Ruff

```bash
ruff check .
```

Run Semgrep

```bash
semgrep --config auto .
```

---

# ⚡ GitHub Actions

The project includes a lightweight CI pipeline.

Every Pull Request automatically runs:

- Ruff Linting
- Bandit Security Scan
- Pytest

Bandit only scans changed Python files for faster execution.

Workflow location

```
.github/workflows/ci.yml
```

---

# 📊 Current Project Status

| Module | Status |
|---------|--------|
| FastAPI Backend | ✅ |
| Bandit Integration | ✅ |
| Semgrep Integration | ✅ |
| AI Patch Generation | ✅ |
| Validation Engine | ✅ |
| Context Engine | ✅ |
| Rule Search API | ✅ |
| Scan Summary API | ✅ |
| GitHub Actions CI | ✅ |
| React Dashboard | 🚧 |
| Docker Support | 🚧 |
| Authentication | 🚧 |

---

# 🗺 Roadmap

## Completed

- FastAPI Backend
- Bandit Integration
- Semgrep Integration
- Context Engine
- LLM Patch Generation
- Validation Engine
- Rule Search API
- Dashboard API
- GitHub Actions CI

## In Progress

- React Dashboard
- Interactive Scan Reports
- Project Upload UI

## Planned

- Authentication
- Docker Support
- Kubernetes Deployment
- VS Code Extension
- Multi-language Analysis
- AI Chat Assistant
- PDF Report Generation

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Anurag Sharan**

GitHub

https://github.com/AnuragS-2025

---

# ⭐ Support

If you found this project useful,

⭐ Star the repository

🐛 Report issues

💡 Suggest new features

Happy Coding! 🚀
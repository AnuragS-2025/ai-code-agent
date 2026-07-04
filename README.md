# AI Code Agent

A modular Python framework for static code analysis, automated patch generation, and context-aware code fixing. The project combines multiple static analysis tools with an extensible fixing pipeline to identify, prioritize, and automatically resolve common code quality, security, and style issues.

---

# Overview

AI Code Agent is designed as a modular backend system that automates the software maintenance workflow. It performs static analysis, prioritizes detected issues, generates validated code patches, and applies fixes while maintaining a structured execution pipeline.

The architecture emphasizes:

- Modular design
- Extensibility
- Deterministic execution
- Safe patch application
- Context-aware code analysis
- Comprehensive automated testing

---

# Features

## Static Analysis

- Ruff integration
- Bandit integration
- Semgrep integration
- Multi-analyzer aggregation
- Unified issue collection
- Issue prioritization

## Automated Code Fixing

- Plugin-based fixer architecture
- Built-in rule fixers
- AST-based code extraction
- AST-safe code replacement
- Patch validation
- Batch patch scheduling

## Project Intelligence

- Project indexing
- Dependency graph construction
- Cross-file context resolution
- Module relationship analysis
- Symbol discovery

## Execution Pipeline

- Modular pipeline orchestration
- Batch execution
- Context-aware processing
- Automatic rescanning
- Metrics collection
- Structured logging

## Feedback System

- Persistent JSON database
- Success recording
- Failure recording
- Historical execution tracking
- Deterministic serialization

## Testing

- Unit testing using Pytest
- Module-level validation
- Integration verification
- Regression testing

---

# System Architecture

```
                    main.py
                        │
                        ▼
               Pipeline Controller
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
 Static Analysis                Project Index
 Ruff                           Scanner
 Bandit                         Parser
 Semgrep                        Builder
        │                               │
        └───────────────┬───────────────┘
                        ▼
                 Context Engine
                        │
                        ▼
              Issue Prioritization
                        │
                        ▼
               Batch Scheduler
                        │
                        ▼
               Built-in Fixers
                        │
                        ▼
               Patch Generation
                        │
                        ▼
               Patch Validation
                        │
                        ▼
               Patch Application
                        │
                        ▼
               Feedback Database
```

---

# Project Structure

```
ai-code-agent/

├── analyzers/
├── builtin_fixers/
├── config/
├── context_engine/
├── feedback/
├── patch_engine/
├── plugins/
├── project_index/
├── tests/

├── pipeline.py
├── main.py
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/AnuragS-2025/ai-code-agent.git
```

Move into the project directory

```bash
cd ai-code-agent
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Usage

Analyze a single file

```bash
python main.py example.py
```

Analyze multiple files

```bash
python main.py file1.py file2.py
```

---

# Running Tests

Execute the complete test suite

```bash
python -m pytest
```

Execute individual test modules

```bash
python -m pytest tests/test_project_index.py -v
```

```bash
python -m pytest tests/test_context_engine.py -v
```

```bash
python -m pytest tests/test_feedback.py -v
```

---

# Core Components

## Static Analysis

- Ruff
- Bandit
- Semgrep

## Patch Engine

- AST Extraction
- AST Replacement
- Patch Validation

## Project Index

- Filesystem Scanner
- AST Parser
- Project Builder
- Module Metadata

## Context Engine

- Dependency Graph
- Module Relationships
- Import Analysis
- Export Analysis

## Pipeline

- Batch Scheduling
- Issue Prioritization
- Metrics Collection
- Logging

## Feedback

- JSON Database
- History Management
- Serialization
- Execution Records

---

# Processing Workflow

```
Input Source Files
        │
        ▼
Static Analysis
(Ruff • Bandit • Semgrep)
        │
        ▼
Issue Prioritization
        │
        ▼
Batch Scheduler
        │
        ▼
Project Index
        │
        ▼
Context Engine
        │
        ▼
Patch Generation
        │
        ▼
Patch Validation
        │
        ▼
Patch Application
        │
        ▼
Feedback Database
```

---

# Testing

The project includes automated tests covering:

- Project indexing
- Cross-file context engine
- Feedback database
- Serialization
- Pipeline components

Current test status:

```
21 Tests Passing
```

---

# Technology Stack

- Python 3.13+
- Ruff
- Bandit
- Semgrep
- Pytest
- AST
- Dataclasses
- JSON
- Git

---

# Design Principles

The project is built around the following engineering principles:

- Modular architecture
- Separation of concerns
- Immutable data models
- Deterministic execution
- Extensible plugin system
- Read-only analysis layers
- Safe code transformation

---

# Development Progress

## Phase 1

Completed

- Analyzer CLI
- Multi-file Support
- Logging System
- Configuration System

## Phase 2

Completed

- Plugin Architecture
- Rule Dispatch
- Built-in Fixers
- AST Extraction
- AST Replacement
- Patch Engine

## Phase 3

Completed

- Batch Scheduler
- Project Indexing
- Cross-file Context
- Pipeline Integration
- Feedback Database

In Progress

- Automatic Test Generation
- Git Automation

---

# Future Work

Planned improvements include:

- Automatic test generation
- Git workflow automation
- AI-assisted feedback learning
- Performance optimization
- Docker support
- CI/CD pipeline
- Web-based interface

---

# License

This project is intended for educational, research, and software engineering experimentation purposes.

---

# Author

**Anurag Sharan**  
GitHub: https://github.com/AnuragS-2025
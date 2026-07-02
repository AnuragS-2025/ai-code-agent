# AI Code Agent

An AI-assisted Python auto-fixing tool that detects issues using static analyzers and automatically applies built-in or AI-generated fixes through an iterative validation pipeline.

---

## Features

- Ruff integration
- Bandit integration
- Semgrep integration
- Built-in rule fixers
- AI fallback for unsupported rules
- Rule registry architecture
- Block-level and file-level fixer dispatch
- Automatic import management
- Multi-file and directory support
- CLI interface
- Iterative re-analysis pipeline
- Patch validation before applying fixes

---

## Project Structure

```
ai-code-agent/
│
├── analyzers/
│   ├── ruff_runner.py
│   ├── bandit_runner.py
│   └── semgrep_runner.py
│
├── parsers/
│   ├── ruff_parser.py
│   ├── bandit_parser.py
│   └── semgrep_parser.py
│
├── patch_engine/
│   ├── extractor.py
│   ├── replacer.py
│   ├── validator.py
│   ├── rule_fixers.py
│   ├── rule_registry.py
│   ├── import_manager.py
│   └── file_fixers.py
│
├── utils/
│   └── file_discovery.py
│
├── pipeline.py
├── main.py
├── auto_fix_engine.py
└── README.md
```

---

## Pipeline Architecture

```
                  main.py
                     │
                     ▼
         Discover Target Python Files
                     │
                     ▼
               pipeline.py
                     │
                     ▼
      ┌────────────────────────────┐
      │ Run Static Analyzers       │
      │                            │
      │  • Ruff                    │
      │  • Bandit                  │
      │  • Semgrep                 │
      └────────────────────────────┘
                     │
                     ▼
             Parse Analyzer Output
                     │
                     ▼
             Extract Code Block
                     │
                     ▼
              Rule Registry Lookup
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   Built-in Fixer          AI Fixer
          │                     │
          └──────────┬──────────┘
                     ▼
             Validate Generated Patch
                     │
                     ▼
              Rule Dispatch Layer
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     Block Fixer          File Fixer
          │                     │
          ▼                     ▼
    Replace Code        Rewrite File
          │                     │
          └──────────┬──────────┘
                     ▼
            Import Management
                     │
                     ▼
              File Cleanup
                     │
                     ▼
              Re-run Analyzers
                     │
                     ▼
          Repeat Until Clean
```

---

## Supported Fixers

### Ruff

| Rule | Description |
|------|-------------|
| E722 | Bare except |
| F401 | Remove unused imports |
| F811 | Remove duplicate imports |
| E402 | Move imports to top (file-level) |
| W291 | Remove trailing whitespace |
| W293 | Remove whitespace on blank lines |
| E303 | Remove excessive blank lines |

### Bandit

| Rule | Description |
|------|-------------|
| B307 | Replace eval() |
| B105 | Hardcoded password |

### Semgrep

| Rule | Description |
|------|-------------|
| no-eval | Replace eval() |

---

## Usage

Analyze a single file

```bash
python main.py app.py
```

Analyze multiple files

```bash
python main.py app.py utils.py
```

Analyze an entire directory

```bash
python main.py src/
```

Limit maximum iterations

```bash
python main.py src --max-iterations 30
```

Display help

```bash
python main.py --help
```

---

## Current Workflow

1. Discover Python files
2. Run Ruff, Bandit and Semgrep
3. Parse issues
4. Extract affected code block
5. Select built-in fixer or AI fixer
6. Validate generated patch
7. Dispatch to block-level or file-level fixer
8. Update imports
9. Cleanup file
10. Re-run analyzers until no supported issues remain

---

## Current Architecture

- Modular pipeline
- Rule registry
- Built-in fixers
- AI fallback engine
- File-level fixers
- Import manager
- Automatic validation
- Multi-file support
- CLI entrypoint

---

## Roadmap

- AST-based extractor
- AST-aware code replacement
- AST-based validator
- Batch issue fixing
- Rule prioritization
- Additional built-in fixers
- Unit and integration tests
- Configurable analyzer settings
- Plugin architecture for custom fixers

---

## License

This project is intended for educational and research purposes.
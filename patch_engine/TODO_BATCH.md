# TODO: Evolution of the Batch Scheduling System

This document outlines the architectural roadmap and planned pipeline for the `patch_engine` batch scheduling system. It serves as a guide for future contributors as we transition from basic deduplication to a fully automated, AST-aware patch application engine.

## Future Workflow Architecture

The planned execution pipeline processes raw analyzer feedback down to structural source code modifications through the following deterministic stages:

1. **Analyzer Issues**: Static analysis tools identify bugs, security vulnerabilities, or style violations and output raw issues.
2. **Issue Prioritizer**: Ranks issues based on severity, confidence, and target files to establish an optimal processing order.
3. **AST Extractor**: Parses target files into Abstract Syntax Trees (AST) to determine precise code coordinates.
4. **Plugin Fixer**: Executes specific rule plugins against the AST nodes to generate a logical modification payload.
5. **Patch Object Creation**: Instantiates lightweight, immutable `Patch` dataclasses containing exact file paths, rules, physical line coordinates, and replacement strings.
6. **Conflict Detection**: Compares pending `Patch` objects for mathematical range overlaps on identical files using `has_conflict()`.
7. **Batch Scheduler**: Organizes conflict-free patches into optimal execution groups and defers or discards overlapping modifications.
8. **Patch Application**: Writes scheduled changes to the physical disk.
9. **Cleanup**: Disposes of temporary AST structures, caches, and system handles.
10. **Analyzer Rescan**: Triggers a final static analysis pass to verify fix correctness and ensure no secondary issues were introduced.

---

## Architectural Constraints & Technical Justifications

### Why Conflict Detection Requires Prior Patch Creation
Conflict detection is fundamentally dependent on physical source coordinates (`start` and `end` lines or offsets). 
* **The Problem**: Analyzer issues only provide high-level diagnostic metadata and vague "trigger" lines. They lack knowledge of the broader structural context or the exact boundaries of the code that needs replacement.
* **The Solution**: Precise coordinates are only computed during the **AST Extraction** and **Plugin Fixer** phases. Conflict detection cannot evaluate mathematical interval overlaps ($max(start_1, start_2) \le min(end_1, end_2)$) until these coordinates are bound inside a concrete `Patch` object. Therefore, instantiation of the `Patch` data model must strictly precede conflict detection.

### Current Limitation of the BatchScheduler
The temporary implementation of `BatchScheduler` only performs deterministic duplicate filtering based on `(rule, message, file, line)`. 
* **Reason**: AST coordinates are entirely unavailable during the early analyzer stage. Without access to the `AST Extractor` and `Plugin Fixer`, the scheduler cannot reason about structural overlap or arrange non-conflicting batches. It acts purely as a defensive deduplication gate until the upstream AST infrastructure is fully integrated.
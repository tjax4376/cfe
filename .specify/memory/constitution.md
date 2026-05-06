# Aidev Project Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### Library-First
Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries.

### CLI Interface
Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats.

### Test-Driven Development (TDD)
TDD is mandatory. Tests MUST be written, approved, and must fail before implementation begins (Red-Green-Refactor cycle strictly enforced). **NEVER simulate data; all schemas must be explicitly defined.**

### Integration Testing
Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas.

### Observability, Versioning & Simplicity
Text I/O ensures debuggability; Structured logging required. Versioning MUST follow MAJOR.MINOR.PATCH format.

## Development Constraints
All code MUST adhere to the standards defined in `@nasa-coding-stds.md`. Placeholders are strictly forbidden in production code.

## Development Workflow
Code reviews MUST verify compliance with all principles and standards. All changes must be traceable to a defined user story or requirement.

## Governance
All PRs/reviews must verify compliance with this Constitution and `@nasa-coding-stds.md`. Versioning policy is MAJOR.MINOR.PATCH.

**Version**: 1.0.0 | **Ratified**: 2026-04-30 | **Last Amended**: 2026-04-30
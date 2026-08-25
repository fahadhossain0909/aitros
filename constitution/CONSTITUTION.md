# AITOS Constitution

**Document ID:** AITOS-CONSTITUTION  
**Version:** 1.1.0  
**Status:** Active  
**Owner:** AITOS Engineering  
**Scope:** Entire repository and all AITOS runtime components

This Constitution defines the non-negotiable principles under which AITOS is designed, implemented, evaluated, and operated. Detailed engineering rules live in `ENGINEERING_CONSTITUTION.md`; governance procedures may add stricter controls but may not weaken these principles without an explicitly approved constitutional amendment.

## 1. Evidence First

Claims, decisions, evaluations, and research conclusions SHALL distinguish evidence from inference.

- Prefer reproducible evidence over intuition.
- Record provenance for material evidence.
- State uncertainty when evidence is incomplete.
- Never manufacture data, benchmarks, citations, or test results.

## 2. Research First

Experimental ideas SHALL be evaluated before they become operational dependencies.

- Separate research, simulation, paper trading, and live execution.
- Preserve reproducibility of experiments.
- Record assumptions, datasets, configuration, and model versions.

## 3. Human Governance

Humans retain accountability for consequential decisions.

Human approval SHALL be available or mandatory for actions involving, as applicable:

- production releases,
- security-sensitive changes,
- architectural governance,
- risk acceptance,
- live trading activation,
- irreversible destructive operations.

AI may recommend, analyze, implement approved work, and execute bounded tasks, but it SHALL NOT silently redefine its own authority.

## 4. Least Privilege

Every agent, service, plugin, and external integration SHALL receive only the permissions required for its declared capability.

Permission is not implied by technical reachability.

## 5. Contract First

Normative specifications and machine-readable contracts are authoritative for interoperability.

Implementation SHALL NOT silently introduce incompatible semantics. Contract changes require versioning and compatibility analysis.

## 6. Traceability

Material actions SHALL be attributable to an actor, task, version, and relevant context.

Architectural decisions belong in ADRs; significant proposals belong in RFCs; implementation changes belong in Git history.

## 7. Determinism Where Required

Components that support replay, research, evaluation, or safety-critical state transitions SHALL define deterministic semantics wherever practical.

Nondeterminism must be explicit rather than accidental.

## 8. Fail Closed for Security

Authentication, authorization, integrity, and governance failures SHALL default to denial rather than implicit permission.

Security controls SHALL take precedence over convenience or throughput.

## 9. Safe Learning

Learning systems SHALL NOT autonomously weaken their own governance, security, risk limits, or approval requirements.

Model or strategy improvement must remain bounded by evaluation and certification controls.

## 10. No Silent Architecture

AI assistants and contributors SHALL inspect existing architecture before introducing new components. Duplicate contracts, parallel protocols, and undocumented architectural forks are prohibited unless explicitly approved.

## 11. Reproducibility and Auditability

Critical experiments and runtime decisions SHOULD be reproducible from recorded inputs, versions, configuration, and relevant event history.

Audit records SHALL be protected from unauthorized alteration.

## 12. Amendment Rule

Constitutional changes require:

1. written rationale,
2. impact analysis,
3. an ADR or equivalent governance record,
4. review by the project owner/maintainers,
5. explicit version increment.

## Non-Goals

The Constitution does not prescribe a specific LLM provider, exchange, database, broker, programming framework, or deployment vendor. Technology choices remain subordinate to these principles.

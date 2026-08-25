# AITOS AI Context Contract

**Document ID:** AITOS-CONTEXT-AI  
**Version:** 1.1.0  
**Status:** Active  
**Authority:** Project Constitution + applicable specifications/ADRs/RFCs

This document defines how AI coding/research agents must operate inside the AITOS repository. It is an execution contract, not merely advice.

## 1. Context Loading Order

Before making a material change, an AI agent SHALL inspect, in order:

1. `constitution/`
2. `docs/IMPLEMENTATION_ROADMAP.md`
3. applicable component specification/contracts
4. relevant ADRs
5. active RFCs
6. current implementation
7. tests and CI configuration
8. recent Git history when compatibility is relevant

The agent may narrow the search when a task is demonstrably isolated, but it must not assume undocumented architecture.

## 2. Existing-Code-First Rule

The agent SHALL inspect existing files before creating new files.

If an existing component is incomplete, the default action is to improve it rather than create a parallel implementation.

New files are justified only when:

- the architecture explicitly requires a new bounded component,
- separation materially improves maintainability, or
- an approved specification/ADR requires it.

## 3. Authority Hierarchy

When sources conflict, use this order unless an explicit governance record says otherwise:

```text
Constitution
    ↓
Normative Specification / Contract
    ↓
Approved ADR
    ↓
Approved RFC
    ↓
Implementation
    ↓
Examples / Informational Documentation
```

Implementation must be corrected when it violates a higher-authority contract.

## 4. Change Discipline

For every material task, the agent SHALL:

- identify affected components,
- identify dependencies and consumers,
- check compatibility,
- preserve public contracts unless a versioned change is intended,
- update tests with implementation changes,
- update documentation when behavior changes,
- report unresolved blockers instead of hiding them.

## 5. No Unsupported Claims

The agent SHALL NOT claim that a component is:

- production-ready,
- secure,
- certified,
- CI-passing,
- fully implemented,
- exactly-once,
- deterministic,

unless the repository contains evidence supporting that claim.

## 6. Trading Safety

AI agents SHALL treat live trading as a privileged downstream capability.

Research and paper trading may proceed under their own permissions, but live execution requires the applicable risk, governance, authorization, and certification gates.

## 7. Context Integrity

Agents must preserve:

- provenance,
- timestamps where relevant,
- version information,
- task/correlation identifiers,
- security classification,
- source references.

Context must be minimized for relevance without removing information required for correctness or safety.

## 8. Verification Before Completion

An AI agent should finish a change only after checking the strongest applicable evidence:

```text
Format → Lint → Type Check → Unit Tests → Contract Tests → Integration Tests
```

If a check cannot be run, the agent must state that explicitly.

## 9. Human Escalation

Escalate rather than guess when:

- requirements conflict,
- security implications are unclear,
- destructive actions are requested without authorization,
- an architectural decision is ambiguous,
- a production/live-trading boundary is involved,
- test evidence contradicts the intended behavior.

## 10. Documentation and Memory

Implementation and documentation SHALL evolve together. Durable architectural knowledge belongs in repository artifacts, not only in chat history.

AI agents should update the relevant specification, roadmap, ADR, changelog, or component README when a change makes existing documentation inaccurate.

# AITOS

**Adaptive Intelligence Trading & Research Operating System**

> Evidence → Knowledge → Decision → Execution → Learning

AITOS is a specification-first, event-driven operating system for governed multi-agent research, trading intelligence, experimentation, and controlled execution.

## Project Status

**Phase:** Runtime Foundation / Event Bus hardening / Replay Engine foundation  
**Status:** Active development — **not production-certified**

A component is not considered production-ready merely because a specification or prototype exists. AITOS uses the following completion path:

```text
Specification
    ↓
Machine-readable Contract
    ↓
Reference Runtime
    ↓
Tests / Conformance
    ↓
Security + Observability
    ↓
CI Quality Gates
    ↓
Integration
    ↓
Certification
```

## Architectural Principles

- Evidence before inference
- Research before deployment
- Human governance for consequential decisions
- AI/model/provider agnosticism
- Deterministic behavior where reproducibility matters
- Least privilege and explicit trust boundaries
- Auditable state transitions
- Versioned contracts and backward-compatibility discipline
- Existing components are inspected and extended before new duplicates are created

## Runtime Domains

```text
runtime/
├── event_bus/          # event coordination backbone
├── replay_engine/      # deterministic event reconstruction
├── context_engine/     # context selection, validation and budgeting
├── memory_engine/      # persistent/episodic/semantic memory
├── registry/           # agent/model/capability registry
├── governance/         # policy and approval enforcement
├── security/           # identity, authorization and trust boundaries
└── workflow_engine/    # governed workflow orchestration
```

Trading/research services are built on top of these runtime contracts and include liquidity, order flow, paper trading, knowledge graph, model registry, risk, and execution capabilities.

## Repository Map

| Area | Purpose |
|---|---|
| `constitution/` | project and engineering principles |
| `agents/` | agent governance, lifecycle, ACP and capability contracts |
| `context/` | context-engine and AI working-context rules |
| `memory/` | memory architecture and retention rules |
| `governance/` | governance and approval policies |
| `runtime/contracts/` | machine-readable runtime contracts |
| `runtime/event_bus/` | Event Bus reference runtime |
| `runtime/replay_engine/` | Replay Engine reference runtime |
| `docs/` | architecture, roadmap and implementation guidance |
| `adr/` | architecture decision records |
| `rfc/` | proposals requiring architectural review |
| `tests/` | cross-component and conformance tests |

## Engineering Workflow

Before changing a component:

1. Read the applicable specification and contract.
2. Inspect the current implementation and tests.
3. Check ADRs/RFCs and dependency relationships.
4. Make the smallest coherent change that advances the specification.
5. Add or update tests.
6. Run formatting, linting, type checking and tests.
7. Review compatibility, security and observability.
8. Record the change in Git history and update documentation.

## Roadmap

The authoritative execution roadmap is [`docs/IMPLEMENTATION_ROADMAP.md`](docs/IMPLEMENTATION_ROADMAP.md).

The current priority is to harden the Event Bus before making downstream components depend on undocumented behavior, while establishing the deterministic Replay Engine foundation.

## Development

Python support currently targets **Python 3.11+**. Development tooling is defined in `pyproject.toml`.

```bash
python -m pip install -e '.[dev]'
ruff check runtime
mypy runtime
pytest
```

## Safety Notice

AITOS is a research and engineering platform. Nothing in this repository should be interpreted as a guarantee of trading performance. Live execution must remain behind explicit risk, governance, authorization, and paper-trading validation gates.

## License

See [`LICENSE`](LICENSE).

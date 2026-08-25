# Agent Communication Protocol (ACP)

**Document ID:** AITOS-ACP-001  
**Version:** 1.1.0  
**Status:** Active / Normative  
**Owner:** AITOS Engineering  
**Scope:** Agent-to-agent, agent-to-runtime, and governed human-agent communication

## 1. Purpose

ACP defines the canonical communication contract for AITOS agents. It standardizes identity, routing, correlation, delegation, context exchange, memory synchronization, failure handling, security, auditability, and protocol compatibility.

ACP is transport-neutral. An implementation may use the AITOS Event Bus, HTTP, WebSocket, a message broker, or another approved transport, but the logical ACP contract remains unchanged.

## 2. Normative Language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

## 3. Message Envelope

Every ACP message MUST contain:

- `message_id` — globally unique identifier
- `protocol` — protocol name and version
- `message_type`
- `timestamp`
- `sender`
- `receiver` or broadcast scope
- `correlation_id`
- `payload`
- `security`
- `status`

The following SHOULD be supplied when applicable:

- `causation_id`
- `conversation_id`
- `task_id`
- `workflow_id`
- `context_ref`
- `memory_refs`
- `trace`
- `deadline`
- `idempotency_key`
- `capability_requirements`

Unknown top-level fields MUST NOT change the meaning of an existing field. Schema evolution MUST follow the AITOS versioning policy.

## 4. Message Types

The canonical types are:

- `REQUEST`
- `RESPONSE`
- `EVENT`
- `ERROR`
- `BROADCAST`
- `DELEGATION`
- `MEMORY_SYNC`
- `CONTEXT_EXCHANGE`
- `PROPOSAL`
- `APPROVAL_REQUEST`
- `REVIEW`
- `WARNING`

Implementations MAY define domain-specific subtypes under a versioned namespace.

## 5. Identity and Trust

A sender MUST be authenticated before privileged communication is accepted.

A receiver MUST verify:

1. sender identity,
2. protocol compatibility,
3. capability requirements,
4. authorization for the requested operation,
5. message integrity when integrity protection is required.

Trust is not inferred from network location.

## 6. Correlation and Causation

`correlation_id` identifies the logical operation across multiple messages.

`causation_id` identifies the message/event that directly caused the current message.

Delegated work MUST preserve the parent correlation chain.

## 7. Delegation

Delegation MUST include:

- parent task/correlation identifier,
- delegated task identifier,
- required capability,
- permission scope,
- deadline or cancellation policy where applicable,
- expected result contract.

Delegation transfers execution responsibility but never transfers governance accountability.

## 8. Context Exchange

Context exchange MUST be:

- scoped to the task,
- version-aware,
- provenance-preserving,
- authorization-filtered,
- bounded by an explicit context budget where applicable.

Agents MUST NOT receive protected context solely because another agent can access it.

## 9. Memory Synchronization

Memory synchronization MUST identify:

- memory record/version,
- source agent,
- provenance,
- operation (`create`, `update`, `delete`, `merge`),
- conflict/version information,
- authorization context.

Unvalidated or speculative output MUST NOT silently become durable institutional memory.

## 10. Delivery Semantics

ACP transport adapters MUST declare delivery semantics:

- `at_most_once`
- `at_least_once`
- `exactly_once`

Exactly-once processing MUST NOT be claimed unless a durable idempotency mechanism and recovery semantics are actually implemented.

At-least-once delivery requires idempotent consumers or explicit duplicate handling.

## 11. Retry and Failure

Retry is permitted only for classified transient failures.

Retry MUST respect:

- maximum attempts,
- backoff,
- deadline,
- cancellation,
- idempotency requirements.

Permanent authorization, validation, policy, or contract errors MUST NOT be retried automatically.

Failures MUST use the canonical AITOS error taxonomy when an error contract is available.

## 12. Human Approval

Human approval MUST be supported for governance-defined operations, including security-sensitive changes, production releases, risk acceptance, and live-trading activation.

An agent MUST NOT represent a recommendation as an approval.

## 13. Audit Requirements

Privileged or material ACP messages MUST produce an auditable record containing, at minimum:

- message ID,
- timestamp,
- sender and receiver,
- correlation/task ID,
- operation,
- authorization result,
- outcome,
- relevant version references.

Audit records MUST be protected against unauthorized modification.

## 14. Security Requirements

ACP implementations MUST enforce:

- authentication,
- authorization,
- least privilege,
- input/schema validation,
- secret isolation,
- sensitive-data minimization,
- replay protection where required,
- integrity protection where required.

Security failures MUST fail closed.

## 15. Protocol Negotiation

Peers MUST negotiate or otherwise establish a mutually supported ACP version before using version-sensitive features.

A receiver MUST reject unsupported mandatory features rather than silently approximating them.

Backward-compatible additions SHOULD be made within the same major protocol version. Breaking changes require a major version increment and migration strategy.

## 16. Lifecycle

```text
CREATE
  ↓
VALIDATE
  ↓
AUTHORIZE
  ↓
ROUTE
  ↓
DELIVER
  ↓
PROCESS
  ↓
ACK / RESPOND
  ↓
AUDIT
```

Failed messages enter the applicable error/retry/DLQ path according to runtime policy.

## 17. Compliance Checklist

Before accepting a privileged message, the runtime MUST verify:

- protocol supported,
- sender authenticated,
- receiver/capability valid,
- authorization granted,
- schema valid,
- correlation valid,
- context access allowed,
- delivery semantics supported,
- idempotency requirements satisfied,
- audit path available.

## 18. Cross References

- `runtime/contracts/event_contract.json`
- `ERROR_CODES.md`
- `VERSIONING.md`
- `REGISTRY_SCHEMA.md`
- Agent Lifecycle
- Agent Security Policy
- Agent Capability Model
- Context and Memory specifications

## Change Log

| Version | Date | Description |
|---|---|---|
| 1.1.0 | 2026-08-26 | Converted ACP from descriptive guidance into a normative transport-neutral protocol contract. |
| 1.0.0 | 2026-07-06 | Initial ACP framework. |

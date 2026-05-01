# Paper 1: "Temporal Prompt Injection: Exploiting Multi-Turn Unreliability for Delayed Payload Attacks on LLMs and MLLMs"

**Status**: Direction established — experiment design deferred to next refinement round.

**Foundation papers**: Visual Exclusivity (MM-Plan, Zhang et al. 2026) + LLMs Get Lost in Multi-Turn Conversation (Laban et al. 2025)

**Related infrastructure**: `ipi-arena-bench` (Multi_turn_IPI_Attack) — indirect prompt injection benchmark covering tool/email/MCP injection. Out of scope for this paper but should be cited in related work as covering the complementary agentic injection surface.

**Target venue**: ICML 2026 Workshop on Adversarial Machine Learning (or equivalent)
**Estimated deadline**: ~mid-June 2026
**Timeline from start**: 8 weeks
**Role in arc**: Foundational measurement paper. Establishes the phenomenon that Papers 2 and 3 build on.

---

## Thesis

Malicious payloads injected late in a multi-turn conversation achieve higher attack success rates than the same payload injected early — not simply because of timing, but because **lateness interacts with documented multi-turn failure modes**: the model has accumulated conversational commitments, made premature assumptions, and is less able to recover. This is a qualitatively different vulnerability from single-turn prompt injection.

**Novelty claim**: Existing prompt injection work studies static or single-shot adversarial instructions. We study *temporally staged prompt injection*, where strategic delay exploits multi-turn unreliability, anchoring to prior context, and failure to recover — not merely instruction-following vulnerability.

**One-sentence punchline**: "A late payload doesn't need to overpower the system instruction — it attaches itself to the model's current trajectory."

---

## Grounding in "LLMs Get Lost in Multi-Turn Conversation"

Laban et al. (2025) document a 39% average performance drop in multi-turn underspecified conversations, driven by four specific failure modes:

1. **Premature answer attempts** — models commit to solutions early, making assumptions to fill underspecified gaps
2. **Commitment/answer bloat** — once an answer trajectory is established, models over-rely on it and fail to invalidate prior assumptions; later answers grow longer and more distorted
3. **Loss-of-middle-turns** — models overweight turn 1 (sets the frame) and the most recent turn, underweighting intermediate turns (mirrors the "lost in the middle" long-context phenomenon)
4. **Verbosity compounds assumptions** — longer responses introduce more assumptions that further anchor the trajectory

**For the attacker**, each failure mode is a distinct exploit surface:
- Premature commitment → late payload frames itself as a natural "clarification" the model is already looking for
- Anchoring → model treats the payload as a legitimate refinement of its existing trajectory, not a novel harmful request
- Loss-of-middle-turns → safety-relevant instructions in the middle of the conversation are already underweighted when the payload arrives
- Verbosity → the model's own bloated responses have planted assumptions the attacker can leverage

---

## Threat Model: Four Variants of Temporal Prompt Injection

| Variant | Description | Exploited failure mode |
|---|---|---|
| **Late clarification injection** | Payload framed as "one more requirement" after benign turns | Premature commitment + anchoring |
| **State-poisoning injection** | Early benign turns induce wrong assumptions; late payload completes the malicious trajectory | Commitment bias + answer bloat |
| **Middle-context burial** | Safety-relevant constraint appears in middle turns; payload in the final turn overrides it | Loss-of-middle-turns + recency bias |
| **Tool/retrieval late injection** | Malicious instruction appears in retrieved content or tool output after task is underway | Anchoring + failure to re-evaluate |

**Scope for this paper**: Late clarification injection, State-poisoning injection, and Middle-context burial. These three variants share a common attack surface: the adversarial payload arrives in a **user turn**, with timing controlled by the human attacker.

**Tool/retrieval late injection is out of scope for this paper.** This variant involves indirect injection — the payload is embedded in tool responses, email bodies, or MCP server outputs, not in user turns. The `ipi-arena-bench` benchmark (Multi_turn_IPI_Attack) already covers this surface with 43 behaviors and a production-grade multi-turn runner. Paper 1 should cite it as prior work and explicitly scope out indirect injection: "ipi-arena-bench measures indirect injection via tool responses; we measure direct temporal injection via user turns — a threat surface with no existing benchmark."

---

## Core Direction

Measure ASR as a function of injection position k (the turn at which the harmful payload appears), across both LLMs and MLLMs. Critically: design preambles that induce the documented failure modes (premature commitment, anchoring) rather than using neutral filler turns.

**Primary question**: Does ASR increase with k? Is the increase sharpest *after* the model has produced an intermediate answer attempt (anchoring threshold)?

**Scope**: Both text-only LLMs and MLLMs. The MLLM angle connects to MM-Plan; the LLM angle is where "LLMs Get Lost" is most directly applicable (text-only tasks). See [Paper1_Experiment_Plan.md](Paper1_Experiment_Plan.md) for the full specification.

---

## Key Hypotheses

- **H1**: ASR(k) is higher for late-stage payloads than early-stage payloads when the payload is framed as a natural clarification or missing requirement (not a blunt harmful request).
- **H2 (anchoring)**: The ASR increase is especially pronounced *after* the model has produced at least one intermediate answer attempt — consistent with Laban et al.'s premature commitment finding.
- **H3 (recovery failure)**: Models that have been shown to exhibit higher unreliability in the Laban et al. data (e.g., Llama-3.1-8B, Claude Haiku) show larger timing-based ASR gains than more reliable models (e.g., Gemini 2.5 Pro, GPT-4.1).
- **H4 (modality)**: The timing effect is larger for MLLMs than text-only LLMs, since visual context may accelerate anchoring.

---

## Experiment Plan

See [Paper1_Experiment_Plan.md](Paper1_Experiment_Plan.md) for the full operational specification: exact conditions (C1–C4), preamble templates, injection positions, pilot protocol, measurement protocol, compute budget, ipi-arena-bench gap assessment, and repo search prompt.

---

## Defense Connection (motivates Paper 3)

The "LLMs Get Lost" paper implicitly suggests what the monitor (Paper 3) should track. A sequence-aware monitor should ask at each turn:

| Signal | Suspicious pattern |
|---|---|
| Goal drift | New turn changes the task objective unexpectedly |
| Authority drift | User/tool/document claims new authority mid-conversation |
| Constraint reversal | "Ignore previous constraints," "actually do X instead" |
| Data boundary change | Request shifts to sensitive data, credentials, private content |
| Recency override | Later instruction directly conflicts with earlier safety-relevant constraint |

This is explicitly sequence-aware rather than message-local — directly motivated by the finding that loss-of-middle-turns makes middle-turn safety constraints vulnerable to late-turn overrides.

---

## Key Risk

**Primary risk**: ASR-vs-position curve is flat — no timing effect even with commitment-inducing preambles.
**Mitigation**: Pilot with 50 instances at k=1 (blunt injection) vs. k=5 (post-commitment, framed as clarification). If flat, the interesting finding becomes *why* — which model properties (from Laban et al.) predict robustness to timing attacks.

**Secondary risk**: The "framed as clarification" manipulation confounds timing with framing quality. An attacker who frames the payload better at k=1 might achieve the same ASR as a late injection.
**Mitigation**: Design a matched-framing condition: same clarification framing at k=1 and k=5, holding framing quality constant. This isolates timing from framing.

---

## Writing Outline (Workshop, ~6 pages)

1. Introduction — temporal structure as attack surface; why lateness ≠ simple timing (0.5pp)
2. Background — "LLMs Get Lost" failure modes; single-turn vs. multi-turn prompt injection (0.75pp)
3. Threat model — four variants; focus on late clarification + state-poisoning (0.75pp)
4. Experiments — ASR vs. position, post-commitment condition, cross-model results (2.5pp)
5. Analysis — anchoring threshold, model unreliability correlation, detection rate (0.75pp)
6. Discussion + limitations + defense implications (0.75pp)

---

## Remaining Open Question

`[CONFIRM]` ICML 2026 Workshop on Adversarial Machine Learning deadline — verify exact date before committing to 8-week timeline.

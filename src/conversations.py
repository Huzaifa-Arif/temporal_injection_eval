"""
Position-controlled multi-turn conversation builder for Temporal Prompt Injection experiments.

Conditions from Paper1_Experiment_Plan.md:
  C1 - Late clarification injection: payload framed as "one more requirement"
  C2 - State-poisoning injection:    early turns induce wrong assumptions; late payload completes trajectory
  C3 - Middle-context burial:        safety constraint placed at turn k_mid; payload at final turn
  C4 - Matched-framing control:      same clarification framing at k=1 vs k=5; isolates timing from framing

Preamble templates are loaded from prompts/preambles.json.
Three task domains: chemistry_lab, legal_drafting, medical_consultation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Condition = Literal["C1", "C2", "C3", "C4"]
Template = Literal["chemistry_lab", "legal_drafting", "medical_consultation"]

PROMPTS_PATH = Path(__file__).parent.parent / "prompts" / "preambles.json"


def _load_preambles() -> dict:
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        return json.load(f)


_PREAMBLES: dict | None = None


def _preambles() -> dict:
    global _PREAMBLES
    if _PREAMBLES is None:
        _PREAMBLES = _load_preambles()
    return _PREAMBLES


@dataclass
class ConversationSpec:
    condition: Condition
    template: Template
    injection_turn: int       # 1-indexed over user turns
    conversation_length: int  # total number of user turns (incl. injection turn)
    harmful_instruction: str
    include_system: bool = True


def build_conversation(spec: ConversationSpec) -> list[dict]:
    """
    Return a messages list ready to pass to the victim model.
    The last message is always a user turn containing the harmful payload.
    All prior assistant turns are pre-filled with the benign stub — the victim
    model only ever generates the response to the final user turn.
    """
    if spec.injection_turn < 1 or spec.injection_turn > spec.conversation_length:
        raise ValueError(
            f"injection_turn={spec.injection_turn} must be in [1, {spec.conversation_length}]"
        )

    p = _preambles()
    tmpl = p["templates"][spec.template]
    stub = p["benign_assistant_stub"]

    messages: list[dict] = []

    if spec.include_system:
        messages.append({"role": "system", "content": tmpl["system"]})

    benign_turns: list[str] = tmpl["turns"]

    for t in range(1, spec.conversation_length + 1):
        if t == spec.injection_turn:
            user_content = _payload_turn(spec, t)
        else:
            # Cycle through available benign turns (excluding the last one,
            # which is reserved as the natural lead-in before the injection).
            benign_idx = (t - 1) % max(len(benign_turns) - 1, 1)
            user_content = benign_turns[benign_idx]

        messages.append({"role": "user", "content": user_content})

        # Add pre-filled assistant stub for all turns except the final one.
        # The victim model generates the response to the final user turn only.
        if t < spec.conversation_length:
            messages.append({"role": "assistant", "content": stub})

    return messages


def _payload_turn(spec: ConversationSpec, turn_index: int) -> str:
    """Wrap the harmful instruction according to the condition."""
    p = _preambles()
    instruction = spec.harmful_instruction

    if spec.condition == "C1":
        template = p["late_clarification_wrapper"]
    elif spec.condition == "C2":
        template = p["state_poisoning_wrapper"]
    elif spec.condition == "C3":
        # C3 middle-context burial: payload always at the final turn regardless
        # of injection_turn (which in C3 marks where the safety constraint sits).
        template = p["late_clarification_wrapper"]
    elif spec.condition == "C4":
        # Matched-framing control: same wrapper regardless of position.
        template = p["matched_framing_wrapper"]
    else:
        raise ValueError(f"Unknown condition '{spec.condition}'")

    return template.format(harmful_instruction=instruction)


def build_c3_conversation(
    template: Template,
    safety_constraint: str,
    harmful_instruction: str,
    conversation_length: int,
    safety_turn: int,
    include_system: bool = True,
) -> list[dict]:
    """
    C3 middle-context burial variant.
    Places a safety-relevant constraint at safety_turn; harmful payload at final turn.
    """
    p = _preambles()
    tmpl = p["templates"][template]
    stub = p["benign_assistant_stub"]
    benign_turns: list[str] = tmpl["turns"]

    messages: list[dict] = []
    if include_system:
        messages.append({"role": "system", "content": tmpl["system"]})

    for t in range(1, conversation_length + 1):
        if t == safety_turn:
            user_content = safety_constraint
        elif t == conversation_length:
            user_content = p["late_clarification_wrapper"].format(
                harmful_instruction=harmful_instruction
            )
        else:
            benign_idx = (t - 1) % max(len(benign_turns) - 1, 1)
            user_content = benign_turns[benign_idx]

        messages.append({"role": "user", "content": user_content})
        if t < conversation_length:
            messages.append({"role": "assistant", "content": stub})

    return messages


INJECTION_POSITIONS = list(range(1, 7))   # k ∈ {1, 2, 3, 4, 5, 6}
TEMPLATES: list[Template] = ["chemistry_lab", "legal_drafting", "medical_consultation"]
CONDITIONS: list[Condition] = ["C1", "C2", "C3", "C4"]

"""Claude decides buy/sell/hold from a market summary. Output is schema-constrained JSON."""
import json

import anthropic

MODEL = "claude-opus-5-5"

SYSTEM = (
    "You are a cautious quantitative trading analyst for a single crypto asset. "
    "Given market indicators and the current portfolio, decide buy, sell, or hold. "
    "Prefer hold when the evidence is mixed. Base the decision only on the data given; "
    "do not claim certainty. Confidence is your calibrated probability (0-1) that the action is correct."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["buy", "sell", "hold"]},
        "confidence": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["action", "confidence", "reasoning"],
    "additionalProperties": False,
}


def decide(client: anthropic.Anthropic, market: dict, portfolio: dict) -> dict:
    resp = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": json.dumps({"market": market, "portfolio": portfolio})}],
    )
    if resp.stop_reason == "refusal":
        return {"action": "hold", "confidence": 0.0, "reasoning": "model refused"}
    text = next(b.text for b in resp.content if b.type == "text")
    d = json.loads(text)
    d["confidence"] = max(0.0, min(1.0, float(d["confidence"])))
    return d

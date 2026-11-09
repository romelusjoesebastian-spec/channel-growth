"""Memecoin agent: scan DexScreener for fresh pairs, hard-filter rugs/illiquid junk, let Claude pick,
trade a multi-token PAPER book with slippage. No live mode: see README for why."""
import argparse
import json
import random
import time
from dataclasses import dataclass, field

import anthropic
import requests

MODEL = "claude-opus-5-5"
API = "https://api.dexscreener.com"


@dataclass
class Filters:
    min_liquidity_usd: float = 25_000
    min_volume_24h_usd: float = 50_000
    min_age_hours: float = 6          # avoid first-minutes sniping zone
    max_age_hours: float = 24 * 14
    min_txns_1h: int = 30
    max_buy_sell_skew: float = 5.0    # lopsided flow = bot/wash trading signal
    max_1h_pump_pct: float = 150      # don't chase vertical candles


def fetch_pairs(chain: str = "solana", query: str = "meme") -> list[dict]:
    r = requests.get(f"{API}/latest/dex/search", params={"q": query}, timeout=15)
    r.raise_for_status()
    return [p for p in r.json().get("pairs", []) if p.get("chainId") == chain]


def synthetic_pairs(n: int = 12, seed: int = 0) -> list[dict]:
    rng, now = random.Random(seed), time.time() * 1000
    return [{
        "chainId": "solana", "pairAddress": f"pair{i}",
        "baseToken": {"address": f"tok{i}", "symbol": f"MEME{i}"},
        "priceUsd": str(rng.uniform(0.00001, 0.05)),
        "liquidity": {"usd": rng.uniform(1_000, 400_000)},
        "volume": {"h24": rng.uniform(5_000, 2_000_000)},
        "priceChange": {"h1": rng.uniform(-30, 200), "h24": rng.uniform(-60, 500)},
        "txns": {"h1": {"buys": rng.randint(1, 300), "sells": rng.randint(1, 300)}},
        "pairCreatedAt": now - rng.uniform(0.5, 24 * 20) * 3600_000,
    } for i in range(n)]


def age_hours(p: dict) -> float:
    return (time.time() * 1000 - p.get("pairCreatedAt", 0)) / 3600_000


def passes(p: dict, f: Filters) -> bool:
    try:
        tx = p["txns"]["h1"]
        buys, sells = tx["buys"], tx["sells"]
        skew = max(buys, 1) / max(sells, 1)
        return (
            float(p["priceUsd"]) > 0
            and p["liquidity"]["usd"] >= f.min_liquidity_usd
            and p["volume"]["h24"] >= f.min_volume_24h_usd
            and f.min_age_hours <= age_hours(p) <= f.max_age_hours
            and buys + sells >= f.min_txns_1h
            and 1 / f.max_buy_sell_skew <= skew <= f.max_buy_sell_skew
            and p["priceChange"]["h1"] <= f.max_1h_pump_pct
        )
    except (KeyError, TypeError, ValueError):
        return False


def digest(p: dict) -> dict:
    return {
        "id": p["baseToken"]["address"], "symbol": p["baseToken"]["symbol"],
        "price": float(p["priceUsd"]), "liquidity_usd": round(p["liquidity"]["usd"]),
        "volume_24h": round(p["volume"]["h24"]), "age_hours": round(age_hours(p), 1),
        "change_1h_pct": p["priceChange"]["h1"], "change_24h_pct": p["priceChange"]["h24"],
        "buys_1h": p["txns"]["h1"]["buys"], "sells_1h": p["txns"]["h1"]["sells"],
    }


SCHEMA = {
    "type": "object",
    "properties": {"picks": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "string"}, "confidence": {"type": "number"}, "reasoning": {"type": "string"},
    }, "required": ["id", "confidence", "reasoning"], "additionalProperties": False}}},
    "required": ["picks"], "additionalProperties": False,
}
SYSTEM = (
    "You screen memecoins that already passed hard liquidity/age/flow filters. Memecoins are extremely "
    "high-risk and most go to zero. Pick at most 2 tokens only if momentum looks organic (balanced "
    "buys/sells, healthy liquidity relative to volume, not a vertical pump). Returning no picks is normal "
    "and good. Use only the data provided; confidence is your calibrated probability the trade profits."
)


def choose(client, candidates: list[dict], held: list[str]) -> list[dict]:
    r = client.beta.messages.create(
        model=MODEL, max_tokens=4000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": json.dumps({"candidates": candidates, "already_held": held})}],
    )
    if r.stop_reason == "refusal":
        return []
    picks = json.loads(next(b.text for b in r.content if b.type == "text"))["picks"]
    valid = {c["id"] for c in candidates}
    return [x for x in picks if x["id"] in valid and x["id"] not in held][:2]


@dataclass
class MemeBook:
    """Paper book. Slippage + fee are harsh on purpose: meme DEX fills are worse than CEX."""
    cash: float = 1_000.0
    pos: dict = field(default_factory=dict)  # id -> {qty, entry, symbol}
    slippage: float = 0.03
    fee: float = 0.01
    max_pos_pct: float = 0.10     # per-token cap on equity
    max_positions: int = 5
    take_profit: float = 0.50
    stop_loss: float = 0.20
    max_hold_hours: float = 24

    def equity(self, prices: dict) -> float:
        return self.cash + sum(p["qty"] * prices.get(i, 0) for i, p in self.pos.items())

    def buy(self, tid, symbol, price, equity, confidence):
        usd = min(equity * self.max_pos_pct * confidence, self.cash)
        if tid in self.pos or len(self.pos) >= self.max_positions or usd < 5:
            return None
        self.cash -= usd
        self.pos[tid] = {"qty": usd * (1 - self.fee) / (price * (1 + self.slippage)),
                         "entry": price, "symbol": symbol, "t": time.time()}
        return {"buy": symbol, "usd": round(usd, 2)}

    def sell(self, tid, price, why):
        p = self.pos.pop(tid)
        proceeds = p["qty"] * price * (1 - self.slippage) * (1 - self.fee)
        self.cash += proceeds
        return {"sell": p["symbol"], "why": why, "pnl_usd": round(proceeds - p["qty"] * p["entry"], 2)}

    def manage(self, prices: dict) -> list[dict]:
        out = []
        for tid in list(self.pos):
            p, px = self.pos[tid], prices.get(tid)
            if px is None:  # pair vanished/delisted: assume rug, mark dead
                out.append(self.sell(tid, 0.0, "pair_missing"))
                continue
            ret = px / p["entry"] - 1
            if ret >= self.take_profit:
                out.append(self.sell(tid, px, "take_profit"))
            elif ret <= -self.stop_loss:
                out.append(self.sell(tid, px, "stop_loss"))
            elif (time.time() - p["t"]) / 3600 > self.max_hold_hours:
                out.append(self.sell(tid, px, "time_exit"))
        return out


def run(a):
    client = None if a.stub else anthropic.Anthropic()
    book, f = MemeBook(), Filters()
    start = book.cash
    for i in range(a.cycles):
        pairs = synthetic_pairs(seed=i) if a.offline else fetch_pairs(a.chain)
        prices = {p["baseToken"]["address"]: float(p["priceUsd"]) for p in pairs if p.get("priceUsd")}
        for e in book.manage(prices):
            print(json.dumps(e))
        eq = book.equity(prices)
        if eq < start * 0.7:
            print("KILL SWITCH: -30% drawdown, stopping.")
            break
        cands = [digest(p) for p in pairs if passes(p, f)][:15]
        picks = [] if a.stub or not cands else choose(client, cands, list(book.pos))
        by_id = {c["id"]: c for c in cands}
        for pk in picks:
            if pk["confidence"] >= 0.65:
                c = by_id[pk["id"]]
                fill = book.buy(c["id"], c["symbol"], c["price"], eq, pk["confidence"])
                if fill:
                    print(json.dumps({**fill, "reasoning": pk["reasoning"]}))
        print(json.dumps({"cycle": i, "candidates": len(cands), "equity": round(book.equity(prices), 2)}))
        if i < a.cycles - 1:
            time.sleep(a.interval)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chain", default="solana")
    p.add_argument("--cycles", type=int, default=1)
    p.add_argument("--interval", type=int, default=900)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--stub", action="store_true", help="skip Claude (smoke test)")
    run(p.parse_args())


if __name__ == "__main__":
    main()

"""Market data: public Coinbase candles, plus a synthetic generator for offline runs."""
import math
import random
import time
from dataclasses import dataclass

import requests


@dataclass
class Candle:
    ts: int
    low: float
    high: float
    open: float
    close: float
    volume: float


def fetch_candles(product: str = "BTC-USD", granularity: int = 3600, limit: int = 100) -> list[Candle]:
    """Oldest-first candles from Coinbase's public (keyless) endpoint."""
    r = requests.get(
        f"https://api.exchange.coinbase.com/products/{product}/candles",
        params={"granularity": granularity}, timeout=15,
    )
    r.raise_for_status()
    rows = sorted(r.json(), key=lambda x: x[0])[-limit:]
    return [Candle(*row) for row in rows]


def synthetic_candles(n: int = 100, start: float = 60000.0, seed: int | None = None) -> list[Candle]:
    rng = random.Random(seed)
    price, out, t = start, [], int(time.time()) - n * 3600
    for i in range(n):
        o = price
        price *= 1 + rng.gauss(0.0003, 0.008) + 0.002 * math.sin(i / 8)
        out.append(Candle(t + i * 3600, min(o, price) * 0.998, max(o, price) * 1.002, o, price, rng.uniform(10, 100)))
    return out


def summarize(candles: list[Candle]) -> dict:
    closes = [c.close for c in candles]
    def sma(n): return sum(closes[-n:]) / min(n, len(closes))
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(max(1, len(closes) - 14), len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(max(1, len(closes) - 14), len(closes))]
    ag, al = sum(gains) / max(len(gains), 1), sum(losses) / max(len(losses), 1)
    rsi = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return {
        "last_price": closes[-1], "sma_10": round(sma(10), 2), "sma_30": round(sma(30), 2),
        "rsi_14": round(rsi, 1),
        "change_24_candles_pct": round((closes[-1] / closes[max(-25, -len(closes))] - 1) * 100, 2),
        "recent_closes": [round(c, 2) for c in closes[-12:]],
    }

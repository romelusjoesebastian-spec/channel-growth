"""CLI: python -m trader.main --mode {signals,paper,live} [--offline]"""
import argparse
import json
import time

import anthropic

from . import brain, data
from .brokers import LiveBroker, PaperBroker
from .risk import RiskLimits, killed, size_order


def run(args):
    lim = RiskLimits()
    client = anthropic.Anthropic()
    symbol = args.product.replace("-", "/")
    broker = None
    if args.mode == "paper":
        broker = PaperBroker()
    elif args.mode == "live":
        broker = LiveBroker(args.exchange, symbol)
    start_equity = None
    entry = None

    for i in range(args.cycles):
        candles = data.synthetic_candles(seed=i) if args.offline else data.fetch_candles(args.product)
        market = data.summarize(candles)
        price = market["last_price"]
        portfolio = {}
        if broker:
            eq = broker.equity(price)
            start_equity = start_equity or eq
            portfolio = {"equity": round(eq, 2), "position_usd": round(broker.position_value(price), 2)}
            if killed(eq, start_equity, lim):
                print("KILL SWITCH: max drawdown hit, stopping.")
                break
            if entry and broker.position_value(price) > 0 and price < entry * (1 - lim.stop_loss_pct):
                print(f"STOP LOSS at {price}")
                broker.sell(broker.position_value(price), price)
                entry = None
                continue

        d = brain.decide(client, market, portfolio) if not args.offline_stub else \
            {"action": "hold", "confidence": 0.0, "reasoning": "stub"}
        line = {"cycle": i, "price": price, **d}

        if broker:
            usd = size_order(d["action"], d["confidence"], portfolio["equity"], portfolio["position_usd"], lim)
            fill = None
            if usd > 0:
                fill = broker.buy(usd, price) if d["action"] == "buy" else broker.sell(usd, price)
                if fill and d["action"] == "buy":
                    entry = price
            line["fill"] = fill
        print(json.dumps(line))
        if i < args.cycles - 1:
            time.sleep(args.interval)

    if broker and start_equity:
        print(f"Start equity {start_equity:.2f} -> {broker.equity(price):.2f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["signals", "paper", "live"], default="paper")
    p.add_argument("--product", default="BTC-USD")
    p.add_argument("--exchange", default="coinbase")
    p.add_argument("--cycles", type=int, default=1)
    p.add_argument("--interval", type=int, default=3600, help="seconds between cycles")
    p.add_argument("--offline", action="store_true", help="synthetic data instead of Coinbase")
    p.add_argument("--offline-stub", action="store_true", help="skip the Claude call (smoke test)")
    run(p.parse_args())


if __name__ == "__main__":
    main()

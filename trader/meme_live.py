"""LIVE Solana memecoin trader via Jupiter. REAL MONEY. UNTESTED against live APIs.

Defaults to dry-run (quotes only, nothing signed). Real swaps need ALL of:
  --execute, TRADER_LIVE_CONFIRM=I_ACCEPT_REAL_LOSSES, SOLANA_PRIVATE_KEY (base58, a *burner* wallet).
Safety: sell-route round-trip check before every buy (catches many honeypots), tiny size caps,
exposure cap, daily-loss kill switch, exits priced from the real sell quote.
"""
import argparse
import base64
import json
import os
import time
from pathlib import Path

import anthropic
import requests

from .meme import Filters, choose, digest, fetch_pairs, passes

SOL = "So11111111111111111111111111111111111111112"
JUP = "https://lite-api.jup.ag/swap/v1"
LAMPORTS = 1_000_000_000
STATE = Path("live_state.json")


class Cfg:
    buy_sol = 0.02            # per trade
    max_exposure_sol = 0.10   # total cost basis open at once
    max_positions = 3
    slippage_bps = 300
    max_roundtrip_loss = 0.15  # buy->sell quote loss above this = reject (honeypot/thin exit)
    take_profit = 0.50
    stop_loss = 0.20
    max_hold_hours = 12
    daily_loss_sol = 0.05     # realized loss that halts trading
    min_confidence = 0.7


def quote(inp: str, out: str, amount: int, bps: int) -> dict | None:
    try:
        r = requests.get(f"{JUP}/quote", params={"inputMint": inp, "outputMint": out,
                                                 "amount": amount, "slippageBps": bps}, timeout=15)
        return r.json() if r.ok and r.json().get("outAmount") else None
    except requests.RequestException:
        return None


def roundtrip_ok(mint: str, sol_amount: int, bps: int, max_loss: float) -> tuple[bool, str]:
    """Quote SOL->token, then token->SOL for the same tokens. Big loss or no route = reject."""
    buy = quote(SOL, mint, sol_amount, bps)
    if not buy:
        return False, "no buy route"
    sell = quote(mint, SOL, int(buy["outAmount"]), bps)
    if not sell:
        return False, "no sell route (possible honeypot)"
    loss = 1 - int(sell["outAmount"]) / sol_amount
    return (loss <= max_loss), f"roundtrip loss {loss:.1%}"


def exit_reason(value_sol: float, cost_sol: float, age_h: float, c=Cfg) -> str | None:
    ret = value_sol / cost_sol - 1
    if ret >= c.take_profit:
        return "take_profit"
    if ret <= -c.stop_loss:
        return "stop_loss"
    if age_h > c.max_hold_hours:
        return "time_exit"
    return None


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {"pos": {}, "realized_sol": 0.0, "day": ""}


def save_state(s):
    STATE.write_text(json.dumps(s, indent=1))


class Wallet:
    def __init__(self, rpc: str):
        from solders.keypair import Keypair
        self.kp = Keypair.from_base58_string(os.environ["SOLANA_PRIVATE_KEY"])
        self.pub, self.rpc = str(self.kp.pubkey()), rpc

    def _rpc(self, method, params):
        r = requests.post(self.rpc, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
        r.raise_for_status()
        j = r.json()
        if "error" in j:
            raise RuntimeError(j["error"])
        return j["result"]

    def sol_balance(self) -> float:
        return self._rpc("getBalance", [self.pub])["value"] / LAMPORTS

    def swap(self, q: dict) -> str:
        from solders.transaction import VersionedTransaction
        r = requests.post(f"{JUP}/swap", json={"quoteResponse": q, "userPublicKey": self.pub,
                                                "dynamicComputeUnitLimit": True}, timeout=20)
        r.raise_for_status()
        tx = VersionedTransaction.from_bytes(base64.b64decode(r.json()["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [self.kp])
        return self._rpc("sendTransaction", [base64.b64encode(bytes(signed)).decode(),
                                              {"encoding": "base64", "maxRetries": 3}])


def run(a):
    live = a.execute
    if live and os.environ.get("TRADER_LIVE_CONFIRM") != "I_ACCEPT_REAL_LOSSES":
        raise SystemExit("Set TRADER_LIVE_CONFIRM=I_ACCEPT_REAL_LOSSES to send real transactions.")
    wallet = Wallet(a.rpc) if live else None
    client, f, c, st = anthropic.Anthropic(), Filters(), Cfg, load_state()
    today = time.strftime("%Y-%m-%d")
    if st["day"] != today:
        st["day"], st["realized_sol"] = today, 0.0

    for i in range(a.cycles):
        # 1) manage open positions using the REAL sell quote (what we could actually get out)
        for mint, p in list(st["pos"].items()):
            q = quote(mint, SOL, p["qty"], c.slippage_bps)
            value = int(q["outAmount"]) / LAMPORTS if q else 0.0
            why = exit_reason(value, p["cost_sol"], (time.time() - p["t"]) / 3600) if q else "no_exit_route"
            if why and (q or why == "no_exit_route"):
                if q and live:
                    print("SELL", p["symbol"], why, wallet.swap(q))
                else:
                    print("DRY SELL" if q else "ALERT: cannot sell", p["symbol"], why)
                if q:
                    st["realized_sol"] += value - p["cost_sol"]
                    del st["pos"][mint]
        if st["realized_sol"] <= -c.daily_loss_sol:
            print("KILL SWITCH: daily loss limit hit.")
            save_state(st)
            break

        # 2) find and vet new entries
        exposure = sum(p["cost_sol"] for p in st["pos"].values())
        if len(st["pos"]) < c.max_positions and exposure + c.buy_sol <= c.max_exposure_sol:
            cands = [digest(p) for p in fetch_pairs(a.chain) if passes(p, f)][:15]
            for pk in (choose(client, cands, list(st["pos"])) if cands else []):
                if pk["confidence"] < c.min_confidence:
                    continue
                amt = int(c.buy_sol * LAMPORTS)
                ok, note = roundtrip_ok(pk["id"], amt, c.slippage_bps, c.max_roundtrip_loss)
                sym = next(x["symbol"] for x in cands if x["id"] == pk["id"])
                print("CANDIDATE", sym, pk["confidence"], note, "-", pk["reasoning"])
                if not ok:
                    continue
                q = quote(SOL, pk["id"], amt, c.slippage_bps)
                if live and q:
                    if wallet.sol_balance() < c.buy_sol + 0.01:
                        print("Insufficient SOL balance.")
                        break
                    print("BUY", sym, wallet.swap(q))
                else:
                    print("DRY BUY", sym)
                if q:
                    st["pos"][pk["id"]] = {"symbol": sym, "qty": int(q["outAmount"]),
                                           "cost_sol": c.buy_sol, "t": time.time()}
                break  # at most one new entry per cycle
        save_state(st)
        if i < a.cycles - 1:
            time.sleep(a.interval)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chain", default="solana")
    p.add_argument("--cycles", type=int, default=1)
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--rpc", default="https://api.mainnet-beta.solana.com")
    p.add_argument("--execute", action="store_true", help="actually send transactions (default: dry-run)")
    run(p.parse_args())


if __name__ == "__main__":
    main()

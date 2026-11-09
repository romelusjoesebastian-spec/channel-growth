# channel-growth

## Trading agent (`trader/`)

Claude reads market indicators and decides buy / sell / hold. Hard risk limits in code
(`trader/risk.py`) size or veto every order, and there is a drawdown kill switch and stop loss.

Three modes:

| Mode | What happens |
|---|---|
| `signals` | Prints decisions with reasoning. No orders. |
| `paper` (default) | Simulated $10k portfolio with fees. No real money. |
| `live` | Real market orders via ccxt. Needs `EXCHANGE_API_KEY`, `EXCHANGE_API_SECRET` and `TRADER_LIVE_CONFIRM=I_ACCEPT_REAL_LOSSES`. |

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
python -m trader.main --mode paper --cycles 24 --interval 3600
python -m trader.main --mode signals
pytest
```

Use `--offline` for synthetic data. **Run paper mode for weeks before even considering live.**
This is not financial advice; LLM trading decisions have no proven edge and live mode can lose
real money. Use an exchange key with trade permission only (no withdrawals) and a small balance.

### Memecoins (`trader/meme.py`)

```bash
python -m trader.meme --chain solana --cycles 24 --interval 900
```

Scans DexScreener (keyless) for pairs, drops likely rugs with hard filters (liquidity, volume,
age window, transaction count, buy/sell skew, no chasing vertical pumps), then Claude picks at most 2.
A paper book applies 3% slippage + 1% fee, 10% per-token cap, 50% take-profit, 20% stop-loss,
24h time exit, and a -30% kill switch. **Paper only, deliberately**: live memecoin trading needs
wallet keys and DEX swaps, which means honeypot tokens, MEV and drained wallets. Filters here cannot
detect honeypots or holder concentration, so a paper win does not mean a live win.

### LIVE memecoin trading (`trader/meme_live.py`) - real money

Solana swaps via Jupiter. **Untested against live APIs** (the dev sandbox had no network). Defaults to dry-run.

1. Make a **new burner wallet** (Phantom -> add account). Fund it with ~0.2 SOL you can afford to lose. Never use your main wallet.
2. Export that burner's private key (base58) and set:
```bash
export ANTHROPIC_API_KEY=...
export SOLANA_PRIVATE_KEY=burner_wallet_base58_key
export TRADER_LIVE_CONFIRM=I_ACCEPT_REAL_LOSSES
```
3. Dry-run first (quotes only, nothing is sent): `python -m trader.meme_live --cycles 3 --interval 60`
4. Real trades: add `--execute`. Limits live in `Cfg`: 0.02 SOL per buy, 0.10 SOL max open, 3 positions, daily loss stop 0.05 SOL.

Every buy is preceded by a round-trip quote (buy then sell back); no sell route or >15% loss is rejected.
This catches many honeypots, not all. Memecoins mostly go to zero; expect to lose the money.

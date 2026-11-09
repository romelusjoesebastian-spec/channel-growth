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

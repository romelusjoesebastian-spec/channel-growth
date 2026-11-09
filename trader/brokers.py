"""Brokers. PaperBroker simulates fills; LiveBroker places real orders and is heavily gated."""
import os
from dataclasses import dataclass, field

LIVE_CONFIRM_ENV = "TRADER_LIVE_CONFIRM"
LIVE_CONFIRM_VALUE = "I_ACCEPT_REAL_LOSSES"
FEE = 0.001  # 0.1% per fill


@dataclass
class PaperBroker:
    cash: float = 10_000.0
    qty: float = 0.0
    trades: list = field(default_factory=list)

    def equity(self, price: float) -> float:
        return self.cash + self.qty * price

    def position_value(self, price: float) -> float:
        return self.qty * price

    def buy(self, usd: float, price: float) -> dict | None:
        usd = min(usd, self.cash)
        if usd < 1:
            return None
        q = usd * (1 - FEE) / price
        self.cash -= usd
        self.qty += q
        return self._log("buy", q, price)

    def sell(self, usd: float, price: float) -> dict | None:
        q = min(usd / price, self.qty)
        if q * price < 1:
            return None
        self.qty -= q
        self.cash += q * price * (1 - FEE)
        return self._log("sell", q, price)

    def _log(self, side, q, price):
        t = {"side": side, "qty": q, "price": price}
        self.trades.append(t)
        return t


class LiveBroker:
    """Real orders via ccxt (market orders). Requires explicit confirmation env var."""

    def __init__(self, exchange_id: str, symbol: str):
        if os.environ.get(LIVE_CONFIRM_ENV) != LIVE_CONFIRM_VALUE:
            raise SystemExit(f"Refusing live mode: set {LIVE_CONFIRM_ENV}={LIVE_CONFIRM_VALUE} to confirm.")
        import ccxt  # lazy: only needed for live
        self.symbol = symbol
        self.ex = getattr(ccxt, exchange_id)({
            "apiKey": os.environ["EXCHANGE_API_KEY"], "secret": os.environ["EXCHANGE_API_SECRET"],
        })
        self.base = symbol.split("/")[0]
        self.quote = symbol.split("/")[1]

    def _bal(self, cur):
        return float(self.ex.fetch_balance()["free"].get(cur, 0) or 0)

    def position_value(self, price):
        return self._bal(self.base) * price

    def equity(self, price):
        return self._bal(self.quote) + self._bal(self.base) * price

    def buy(self, usd, price):
        usd = min(usd, self._bal(self.quote))
        if usd < 5:
            return None
        o = self.ex.create_market_buy_order(self.symbol, usd / price)
        return {"side": "buy", "order": o.get("id"), "price": price}

    def sell(self, usd, price):
        q = min(usd / price, self._bal(self.base))
        if q * price < 5:
            return None
        o = self.ex.create_market_sell_order(self.symbol, q)
        return {"side": "sell", "order": o.get("id"), "price": price}

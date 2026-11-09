"""Hard risk limits enforced in code. The model proposes; this module disposes."""
from dataclasses import dataclass


@dataclass
class RiskLimits:
    max_position_pct: float = 0.25    # max share of equity held in the asset
    max_trade_pct: float = 0.10       # max single trade as share of equity
    min_confidence: float = 0.6       # ignore low-confidence calls
    max_drawdown_pct: float = 0.10    # kill switch: stop trading below this drawdown from start
    stop_loss_pct: float = 0.05       # exit if price falls this far below avg entry


def size_order(action: str, confidence: float, equity: float, position_value: float, lim: RiskLimits) -> float:
    """Return the USD notional allowed for this action (0 = do nothing)."""
    if action == "hold" or confidence < lim.min_confidence:
        return 0.0
    trade = equity * lim.max_trade_pct * min(confidence, 1.0)
    if action == "buy":
        room = equity * lim.max_position_pct - position_value
        return max(0.0, min(trade, room))
    if action == "sell":
        return max(0.0, min(trade, position_value))
    return 0.0


def killed(equity: float, start_equity: float, lim: RiskLimits) -> bool:
    return equity < start_equity * (1 - lim.max_drawdown_pct)

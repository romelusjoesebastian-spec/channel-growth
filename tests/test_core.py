import pytest
from trader.brokers import LiveBroker, PaperBroker
from trader.risk import RiskLimits, killed, size_order

L = RiskLimits()

def test_hold_and_low_confidence_do_nothing():
    assert size_order("hold", 0.9, 10000, 0, L) == 0
    assert size_order("buy", 0.3, 10000, 0, L) == 0

def test_position_cap():
    assert size_order("buy", 1.0, 10000, 2500, L) == 0
    assert size_order("buy", 1.0, 10000, 0, L) == pytest.approx(1000)

def test_cannot_sell_more_than_held():
    assert size_order("sell", 1.0, 10000, 300, L) == 300

def test_kill_switch():
    assert killed(8900, 10000, L) and not killed(9500, 10000, L)

def test_paper_roundtrip_loses_only_fees():
    b = PaperBroker()
    b.buy(1000, 100); b.sell(b.position_value(100), 100)
    assert 9995 < b.equity(100) < 10000

def test_live_refuses_without_confirmation(monkeypatch):
    monkeypatch.delenv("TRADER_LIVE_CONFIRM", raising=False)
    with pytest.raises(SystemExit):
        LiveBroker("coinbase", "BTC/USD")

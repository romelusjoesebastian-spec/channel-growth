import time
from trader.meme import Filters, MemeBook, passes, synthetic_pairs

def good():
    return {"priceUsd": "0.01", "liquidity": {"usd": 100_000}, "volume": {"h24": 200_000},
            "priceChange": {"h1": 10, "h24": 20}, "txns": {"h1": {"buys": 60, "sells": 50}},
            "pairCreatedAt": (time.time() - 48 * 3600) * 1000}

def test_filter_accepts_good_and_rejects_rugs():
    f = Filters()
    assert passes(good(), f)
    for mut in [lambda p: p["liquidity"].update(usd=1000), lambda p: p.update(pairCreatedAt=time.time() * 1000),
                lambda p: p["txns"]["h1"].update(sells=1, buys=100), lambda p: p["priceChange"].update(h1=900)]:
        p = good(); mut(p); assert not passes(p, f)
    assert not passes({}, f)

def test_book_stop_loss_take_profit_and_missing_pair():
    b = MemeBook()
    b.buy("a", "A", 1.0, 1000, 1.0); b.buy("b", "B", 1.0, 1000, 1.0); b.buy("c", "C", 1.0, 1000, 1.0)
    out = b.manage({"a": 0.7, "b": 1.6})  # c missing
    why = {o["sell"]: o["why"] for o in out}
    assert why == {"A": "stop_loss", "B": "take_profit", "C": "pair_missing"}
    assert not b.pos

def test_position_cap_and_synthetic():
    b = MemeBook()
    assert b.buy("a", "A", 1.0, 1000, 1.0)["usd"] == 100
    assert b.buy("a", "A", 1.0, 1000, 1.0) is None
    assert len(synthetic_pairs()) == 12

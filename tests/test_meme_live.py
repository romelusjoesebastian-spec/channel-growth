from trader import meme_live as m

def test_exit_reasons():
    assert m.exit_reason(0.04, 0.02, 1) == "take_profit"
    assert m.exit_reason(0.012, 0.02, 1) == "stop_loss"
    assert m.exit_reason(0.02, 0.02, 20) == "time_exit"
    assert m.exit_reason(0.021, 0.02, 1) is None

def test_roundtrip(monkeypatch):
    def fake(inp, out, amt, bps):
        if inp == m.SOL: return {"outAmount": "1000"}
        return {"outAmount": str(int(amt_sol * 0.9))} if sell_ok else None
    monkeypatch.setattr(m, "quote", fake)
    global amt_sol, sell_ok
    amt_sol, sell_ok = 1000, True
    assert m.roundtrip_ok("x", 1000, 300, 0.15)[0]
    assert not m.roundtrip_ok("x", 1000, 300, 0.05)[0]      # 10% loss > 5% cap
    sell_ok = False
    ok, why = m.roundtrip_ok("x", 1000, 300, 0.15)
    assert not ok and "honeypot" in why

"""Offline tests for the trading analyst (no API key needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading_analyst import sma, rsi, draft_signal, build_ai_prompt


def test_sma_basic():
    assert sma([1, 2, 3, 4, 5], 3) == 4.0


def test_sma_not_enough_data():
    assert sma([1, 2], 5) is None


def test_rsi_bounds():
    prices = [100 + i for i in range(30)]  # steady climb
    value = rsi(prices)
    assert 0 <= value <= 100
    assert value > 70  # strong uptrend -> high RSI


def test_rsi_downtrend_low():
    prices = [100 - i for i in range(30)]  # steady fall
    assert rsi(prices) < 30


def test_draft_signal_structure():
    prices = [100 + i * 0.5 for i in range(30)]
    s = draft_signal("TEST", prices)
    assert s["symbol"] == "TEST"
    assert s["action"] in ("HOLD", "CONSIDER_BUY", "CONSIDER_REDUCE")
    assert "not financial advice" in s["note"].lower()
    assert len(s["reasons"]) > 0


def test_ai_prompt_mentions_review():
    prompt = build_ai_prompt([draft_signal("T", [100 + i for i in range(30)])])
    assert "human decides" in prompt
    assert "Not financial advice" in prompt


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print(f"PASS {name}")
    print("All tests passed.")

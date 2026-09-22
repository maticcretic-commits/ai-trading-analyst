#!/usr/bin/env python3
"""
AI Trading Analyst — portfolio practice project.

Analyzes a stock portfolio and drafts trade instructions.
Works in two modes:
  * Rule-based (default, no API key): computes SMA/RSI indicators and
    generates draft signals from transparent rules.
  * Claude-assisted (--ai): sends the indicators to the Anthropic API
    for a written analysis. The model only *drafts* — every instruction
    is labeled for human review, never auto-executed.

Paper-trading / education only. NOT financial advice, and this starter
never places real orders.

Usage:
    python trading_analyst.py data/sample_portfolio.json
    python trading_analyst.py data/sample_portfolio.json --ai   # needs ANTHROPIC_API_KEY
    python tests/test_analyst.py
"""

import argparse
import json
import os
import sys
from pathlib import Path

# TODO(learn): add MACD and Bollinger Bands, then compare signal quality
# on the sample data before/after.


def sma(prices, window):
    """Simple moving average of the last `window` prices."""
    if len(prices) < window or window <= 0:
        return None
    return sum(prices[-window:]) / window


def rsi(prices, window=14):
    """Relative Strength Index (0-100). >70 often 'overbought', <30 'oversold'."""
    if len(prices) < window + 1:
        return None
    gains, losses = [], []
    for i in range(1, window + 1):
        change = prices[-i] - prices[-i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def draft_signal(symbol, prices):
    """Transparent rule-based draft signal. Returns dict, never trades."""
    price = prices[-1]
    sma20 = sma(prices, 20)
    rsi14 = rsi(prices, 14)
    reasons = []
    action = "HOLD"
    if sma20 is not None and price > sma20:
        reasons.append(f"price {price:.2f} above 20-day SMA {sma20:.2f} (uptrend)")
    elif sma20 is not None:
        reasons.append(f"price {price:.2f} below 20-day SMA {sma20:.2f} (downtrend)")
    if rsi14 is not None:
        reasons.append(f"RSI(14) = {rsi14:.1f}")
        if rsi14 < 30 and sma20 is not None and price > sma20:
            action = "CONSIDER_BUY"
            reasons.append("oversold in an uptrend")
        elif rsi14 > 70:
            action = "CONSIDER_REDUCE"
            reasons.append("overbought")
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "action": action,
        "reasons": reasons,
        "note": "DRAFT for human review only — not financial advice.",
    }


def build_ai_prompt(signals):
    lines = ["You are a careful trading assistant. Draft only — the human decides.",
             "Portfolio signals (rule-based indicators):"]
    for s in signals:
        lines.append(f"- {s['symbol']} @ {s['price']}: {s['action']} "
                     f"({'; '.join(s['reasons'])})")
    lines.append("Write a short analysis: trend read, risks, and what to double-check "
                 "before acting. End with: 'Not financial advice.'")
    return "\n".join(lines)


def analyze_with_claude(prompt):
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic  (or run without --ai)")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("Set ANTHROPIC_API_KEY (see .env.example) or run without --ai.")
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Draft AI-assisted trade analysis")
    parser.add_argument("portfolio", help="JSON file: {\"SYMBOL\": [prices...]}")
    parser.add_argument("--ai", action="store_true",
                        help="also ask Claude for a written analysis")
    args = parser.parse_args()

    prices_by_symbol = json.loads(Path(args.portfolio).read_text())
    signals = [draft_signal(sym, prices)
               for sym, prices in prices_by_symbol.items()]

    print(json.dumps(signals, indent=2))

    if args.ai:
        print("\n--- Claude analysis ---\n")
        print(analyze_with_claude(build_ai_prompt(signals)))


if __name__ == "__main__":
    main()

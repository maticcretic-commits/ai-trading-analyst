# AI Trading Analyst

A portfolio practice project: a **Claude-assisted trade analysis bot** starter —
the pattern behind "$2,500 fixed" Interactive-Brokers + Claude integration gigs.

> Paper-trading / education only. **Not financial advice.** This starter never
> places real orders — it only *drafts* analysis for human review.

## What it does

1. Loads price history per symbol from a JSON portfolio file.
2. Computes **SMA(20)** and **RSI(14)** indicators (pure Python, no deps).
3. Drafts transparent rule-based signals (`HOLD` / `CONSIDER_BUY` / `CONSIDER_REDUCE`)
   with human-readable reasons.
4. Optionally (`--ai`) sends the signals to Claude for a written analysis.
   The model drafts; the human decides.

## Setup

```bash
pip install -r requirements.txt   # only needed for --ai mode
cp .env.example .env              # add ANTHROPIC_API_KEY for --ai mode
```

## Usage

```bash
# Rule-based draft signals (no API key needed)
python trading_analyst.py data/sample_portfolio.json

# Plus Claude's written analysis
python trading_analyst.py data/sample_portfolio.json --ai

# Tests (no API key needed)
python tests/test_analyst.py
```

## What I'd build next (learning roadmap)

- [ ] Live market-data adapter (broker API) behind a clean interface
- [ ] Backtest the rules on historical data before trusting them
- [ ] Position-sizing and stop-loss helpers
- [ ] MCP-style tool calling instead of a single prompt

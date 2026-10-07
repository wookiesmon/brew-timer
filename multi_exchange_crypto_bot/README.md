# multi_exchange_crypto_bot

A rule-based crypto trade **planner** with paper trading, walk-forward backtesting and
**gated** live execution on two strictly separated venues:

| Module | Venue | Instrument | What you hold |
|---|---|---|---|
| `coinbase_adapter.py` | Coinbase Advanced Trade | **Spot only** | The actual asset |
| `hyperliquid_adapter.py` | Hyperliquid | **Perpetual futures**, isolated margin, 1x by default | A derivatives position |

> **Not financial advice.** Every level this tool prints is an automated scenario
> computed from historical candles with fixed rules. It does not predict prices,
> does not guarantee fills, and cannot prevent losses. Paper-trade first.

---

## 1. Setup

Requires Python 3.11.

**Linux / macOS**
```bash
cd multi_exchange_crypto_bot
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell)**
```powershell
cd multi_exchange_crypto_bot
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1      # cmd.exe: .venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

Run the tests:
```bash
python -m pytest
```

SDK versions used and verified while writing this project:
`coinbase-advanced-py==1.8.4`, `hyperliquid-python-sdk==0.24.0` (pinned in
`requirements.txt`). On every `--live` start the bot re-checks that each SDK method and
parameter it calls still exists (`verify_sdk()`) and refuses live trading if not.

## 2. Commands

Run from inside `multi_exchange_crypto_bot/`:

```bash
python -m main --venue coinbase    --product GTC-USD --analyze      # analysis + plan, never trades
python -m main --venue coinbase    --product BTC-USD --paper        # paper trading on live data
python -m main --venue hyperliquid --product BTC     --analyze
python -m main --venue hyperliquid --product BTC     --paper
python -m main --venue coinbase    --product GTC-USD --backtest     # walk-forward replay
python -m main --venue coinbase    --product GTC-USD --status
python -m main --venue hyperliquid --product BTC     --status
python -m main --venue coinbase    --product GTC-USD --cancel-open
python -m main --venue hyperliquid --product BTC     --cancel-open
python -m main --venue coinbase    --product GTC-USD --reset-paper
python -m main --venue hyperliquid --product BTC     --reset-paper
python -m main --venue coinbase                      --screen       # rank tradable coins by CoinGecko liquidity
python -m main --venue coinbase    --product GTC-USD --check        # pre-flight report, never trades
python -m main --venue coinbase    --product GTC-USD --preview      # Coinbase validates the orders, places none
python -m main --venue coinbase    --product GTC-USD --live         # only after every gate below
python -m main --venue coinbase    --product GTC-USD --clear-halt   # after reviewing a daily-loss halt
```

Useful options: `--ask` (prompt for equity / allocation / max loss / risk %),
`--equity`, `--max-allocation`, `--max-loss`, `--risk-pct`, `--once` (single step),
`--max-runs N` (paper/live: after a run closes, wait for the next allowed setup and
trade it, up to N runs; default 1), `--candles N` (backtest length), `--log-level DEBUG`.
Set `LOG_FILE=bot.log` to keep an audit log (secrets are redacted).

`--cancel-open` cancels **every** open order on that product, including orders you
placed by hand and the protective stop. It asks you to type `CANCEL` first (`--yes` skips this).

Exit codes: `0` ok, `1` error, `2` market unavailable, `3` kill switch, `4` halted,
`5` refused (risk rule or live gate).

`--analyze`, `--paper` and `--backtest` use public market data and need no API keys.

## 3. Strategy rules (transparent, no black box)

Indicators from at least 100 (target 300) **closed** candles at `CANDLE_INTERVAL`
(the still-forming candle is dropped): ATR(14), EMA(20), EMA(50), RSI(14), rolling
volatility, average volume and recent/average volume ratio, fractal swing highs/lows,
consolidation range, and ATR bands. Nearby levels are clustered into support and
resistance zones. A 0/1 rule score is printed for information only.

| Item | Rule |
|---|---|
| Entry 1 / 2 / 3 | price − 0.5 / 1.0 / 1.5 ATR, GTC limit buys, quantity split 40 / 35 / 25 % |
| Stop trigger | lowest entry − 0.5 ATR |
| Stop-limit price | trigger − max(`STOP_BUFFER_PCT` % of trigger, 0.25 ATR) |
| R | weighted average entry − stop trigger |
| TP1 / TP2 | average entry + 1R / + 2R |
| TP3 | nearest resistance zone above TP2, else + 3R (never below TP2) |
| No plan | price > EMA(20) + 2 ATR ("Market is extended; no automatic market entry will be created."), illiquid volume, entries ≤ 0, exchange minimums not met |

All prices and sizes are `Decimal` and are **rounded down** to exchange precision.

### Position sizing

```
max allocation  = min(MAX_ALLOCATION_PCT % of equity, --max-allocation, MAX_POSITION_NOTIONAL_USD)
max loss budget = min(MAX_PLANNED_LOSS_PCT % of equity, --max-loss, --risk-pct % of equity)

allocation size = max allocation / average entry
risk size       = max loss budget / worst-case loss per unit
worst-case loss per unit = (avg entry − stop-limit) + fees on both legs + slippage
final size      = min(risk size, allocation size), split 40/35/25 and floored
```

The risk size deliberately uses the worst case (stop-limit fill + fees + slippage)
rather than just `avg entry − stop trigger`. That size is never larger than the
textbook formula, and it keeps the printed worst-case loss within your budget.

## 3b. CoinGecko checks (optional)
CoinGecko is a market-data aggregator, **not** an exchange: it never places, sizes or
prices orders. Entries, stops and fills always use the exchange's own data. It adds two
things:

- **`--screen`**: lists coins tradable on the venue, ranked by 24h volume across all
  exchanges, with market cap, 24h change and (on Coinbase) Coinbase's own 24h volume.
  Coins below `COINGECKO_MIN_VOLUME_USD` are dropped. It's a liquidity filter, not a
  recommendation.
- **Pre-trade check** (`COINGECKO_ENABLED=true`): before any new plan in `--analyze`,
  `--paper`, `--preview` and `--live`, the plan is refused if any of these fail:
  - The venue price differs from CoinGecko's cross-exchange price by more than
    `COINGECKO_MAX_PRICE_DEVIATION_PCT` (default 2%). That usually means a stale feed or
    a broken market. The comparison is skipped when CoinGecko's own price is over 15
    minutes old.
  - The coin's 24h volume across all exchanges is below `COINGECKO_MIN_VOLUME_USD`
    (default $1M).
  - Coinbase only: Coinbase's own 24h volume is below `COINGECKO_MIN_VENUE_VOLUME_USD`
    (default $250k), or the planned position exceeds `COINGECKO_MAX_VOLUME_SHARE_PCT`
    (default 1%) of it. Thin books are where stop-limits slip or fail to fill.

  If CoinGecko can't be reached while the check is enabled, new plans are refused (it
  fails closed). Runs already open keep being managed. `--check` shows the result.

Setup: create a free **Demo** API key at coingecko.com/en/api and set `COINGECKO_API_KEY`
(`COINGECKO_PLAN=pro` for a paid key). Many coins share a ticker symbol, so pin the ones
you trade, e.g. `COINGECKO_COIN_IDS=GTC=gitcoin`. Responses are cached (prices 5 min,
exchange volume 1 h, symbol lookups 24 h) to stay inside the Demo plan's monthly call cap.
Coinbase's CoinGecko exchange id is `gdax` (`COINGECKO_COINBASE_EXCHANGE_ID`). For
Hyperliquid perps, only the price and total-volume checks apply: CoinGecko's price is
spot, so a small perp basis is normal.

## 4. Live trading

### Going live, step by step
Each step must pass before the next one:

1. **Paper.** Run `--analyze`, then `--backtest`, then `--paper --max-runs 5` for at
   least a few days on the product you plan to trade. Read `--status` and the log.
2. **Pre-flight.** Add your keys to `.env` (see section 5) and run `--check`. Every
   line must be `PASS`. It verifies the SDK, the market, the candle history, your key's
   permissions (a Coinbase key that can **transfer** is refused, and so is a Hyperliquid
   **main-wallet** key), your balance, and shows each live gate.
3. **Rehearse the orders.**
   - Coinbase: `--preview` sends the planned entries to Coinbase's order-preview
     endpoint. Coinbase checks precision, minimums, balance and fees, and places nothing.
   - Hyperliquid: set `HYPERLIQUID_TESTNET=true`, fund a testnet account, create a
     testnet API wallet, and run `--live --once` against testnet first.
4. **Small live run.** Set the live flag and `DRY_RUN=false`. Use a tiny
   `ACCOUNT_EQUITY_USD` (or `--max-allocation 25`), then run `--live --once`. Check the
   orders in the exchange UI and in `--status`.
5. **Supervised live.** Run `--live` (optionally `--max-runs N`) under `tmux`/`screen`
   or a service manager, with `LOG_FILE` set. Keep watching it.

### Gates (all required, otherwise nothing is submitted)
1. `COINBASE_LIVE_TRADING=true` or `HYPERLIQUID_LIVE_TRADING=true` for that venue.
2. `DRY_RUN=false`.
3. No `STOP` file and no unresolved daily-loss halt.
4. SDK method check passes, and the credentials cannot move funds out (a Coinbase key
   without Transfer permission; a Hyperliquid API wallet rather than the main wallet key).
5. Market verified tradable with complete precision/minimum metadata.
6. Account balance retrieved and sufficient for the planned entries.
7. The plan passes every risk rule.
8. You type exactly `CONFIRM_LIVE` at the prompt (and `CONFIRM_LEVERAGE` if Hyperliquid leverage > 1).

### Order lifecycle
- Entries: three GTC limit buys, each submitted at most once.
- Exits are placed **only for confirmed filled quantity**, and resized as partial fills arrive:
  - **Coinbase spot:** resting sell orders put a hold on the base balance, so a stop
    and take-profits cannot both cover the full position. The stop-limit covers
    everything. When price reaches a TP level, the bot shrinks the stop, then places
    that TP. The bot never places sells for more than the available base balance.
    Spot has no reduce-only flag: sells are bounded by the balance.
  - **Hyperliquid:** take-profits and the stop are **reduce-only**, so they rest
    together and can never increase or flip the position. The stop is a trigger order
    with `isMarket=false` (a real stop-limit), `tpsl="sl"`.
- If price is already at or below the stop trigger when the stop is due (e.g. the entries
  filled during a fast drop), a stop order cannot be placed below the market. The bot
  places what a triggered stop-limit becomes: a limit sell at the stop-limit price.
- If the exchange rejects the protective stop 3 times, the bot cancels entries and TPs,
  halts, and asks for manual attention instead of looping.
- Once price reaches TP1 after a fill, or any exit fills, remaining entries are cancelled.
  Unfilled entries are also cancelled after `ENTRY_TTL_HOURS`.

### Restarts and duplicates
Every order row is written to SQLite (`PENDING_SUBMIT`) **before** the API call.
Client order IDs are deterministic per run/leg/version and UNIQUE in the database.
A leg is never re-sent while a non-terminal row exists. If an API call fails in a way
that hides the outcome (e.g. a timeout), the order is marked `SUBMIT_UNKNOWN` and looked
up by client ID on the next step instead of being resent. On restart, the active run is
loaded and reconciled with the exchange before anything new is placed. Order creation
is never retried automatically. Reads and cancels use bounded exponential backoff, and
any API error starts a cooldown (`API_ERROR_COOLDOWN_SECONDS`) with no new orders.
If a whole polling step fails (network outage, exchange 5xx), the loop logs it and
retries on the next poll. Orders already resting on the exchange, including the stop,
keep working. After 10 consecutive failed steps the bot exits and says so.

### Kill switch and limits
- **`STOP` file** in the working directory: every bot-managed order is cancelled and
  the process exits. **This includes the protective stop, so any open position is then
  unprotected.** Close or protect it manually.
- **Daily loss** (`MAX_DAILY_LOSS_USD`, realized today + unrealized loss): entries and
  take-profits are cancelled, the protective stop is **kept**, and the bot halts. It
  will not restart until you run `--clear-halt`.
- `MAX_OPEN_ORDERS` counts bot orders plus any orders you placed manually on the
  product (those are never touched).
- `MAX_POSITION_NOTIONAL_USD` caps exposure regardless of leverage.

### Live-trading checklist
- [ ] Ran `--analyze` and read every warning.
- [ ] Paper-traded the same product with `--paper` and reviewed `--status`.
- [ ] Ran `--backtest` and understood that past simulated results are not predictive.
- [ ] `--check` shows no FAIL lines; Coinbase `--preview` (or Hyperliquid testnet) succeeded.
- [ ] API key has trade permissions only, with **no withdraw/transfer**, and is IP-allowlisted.
- [ ] Equity, allocation, loss budget and `MAX_DAILY_LOSS_USD` are amounts you can afford to lose.
- [ ] Hyperliquid: leverage is 1x, and you understand funding and liquidation.
- [ ] You know how to use `STOP`, `--cancel-open` and the exchange UI to exit manually.
- [ ] You will monitor the bot. It is an automation tool, not a substitute for supervision.

## 5. API keys and security
- Secrets come only from environment variables or `.env`. `.env` is git-ignored.
  Secrets are held as pydantic `SecretStr`, and a log filter redacts them if one ever
  reaches a log line. The bot never logs auth headers or signing payloads.
- **Coinbase:** create a CDP API key (ECDSA/ES256) with **View** and **Trade**
  permissions only. **Never enable Transfer/withdraw.** Restrict it to your IP address.
  Store the PEM key on one line with `\n` escapes.
- **Hyperliquid:** generate an **API wallet** (Hyperliquid app → More → API). Put its
  private key in `HYPERLIQUID_PRIVATE_KEY` and your main account address in
  `HYPERLIQUID_ACCOUNT_ADDRESS`. API wallets can trade but **cannot withdraw**. Never
  use your main wallet's private key. Try `HYPERLIQUID_TESTNET=true` first.
- Never commit `.env`, database files or logs containing account data.

## 6. Paper-trading walkthrough
1. `python -m main --venue coinbase --product BTC-USD --analyze`: read the plan.
2. `python -m main --venue coinbase --product BTC-USD --paper`: creates a paper run
   in `trading_bot.paper.sqlite3` (paper state is a **separate file** from live state),
   then polls every `POLL_SECONDS`. As candles close, the simulator matches orders and
   prints `[SIMULATED FILL]` lines. Stop it with Ctrl-C, and run the same command again
   to resume the run without duplicating anything.
3. `python -m main --venue coinbase --product BTC-USD --status`: shows orders, fills,
   position and realized P/L.
4. `python -m main --venue coinbase --product BTC-USD --reset-paper`: clears it.

Simulator fill model (conservative): limit buys fill only if price trades *below*
the limit; limit sells only if price trades *above* it. A stop-limit that gaps through
its limit stays unfilled. Fills are capped at `SIM_VOLUME_PARTICIPATION_PCT` of candle
volume, which produces partial fills. No look-ahead: orders only match candles that
open after they were placed. Funding and liquidation are **not** simulated.

## 7. Risks you must understand
- **Stop-limit non-execution.** A stop-limit becomes a limit order at the stop-limit
  price once triggered. If the market gaps below that price, or liquidity disappears
  (common in small caps such as GTC), it **may never fill** while losses grow. The bot
  shows the trigger and the limit separately for this reason.
- **Coinbase spot vs Hyperliquid perpetuals.** Spot means you own the asset, your loss
  is limited to what you paid, and there is no liquidation. A perpetual is a derivatives
  contract: it pays or charges **funding** (typically hourly on Hyperliquid), it can be
  **liquidated**, and its stops trigger on the **mark price** (an oracle-based index),
  not the last trade. Coinbase stops trigger on the last trade price.
- **Liquidation.** At 1x isolated margin, liquidation is near zero price. With
  leverage the bot estimates a conservative liquidation price and refuses plans where
  it is at or above the stop-limit. Once a position exists, it checks the exchange's own
  figure. Margin is not exposure: 100 USDC margin at 3x controls 300 USDC notional.
- **Slippage and partial fills.** Thin books move against you. Orders may fill partly
  or not at all, and fees are deducted from results.
- **Exchange outages / API changes.** Venues halt, rate-limit, delist and change APIs.
  The bot fails closed (no new orders) on errors, but orders already resting on the
  exchange keep working while the bot is down.
- **Market availability.** The bot never assumes a symbol exists. For example, if GTC
  is not listed as a Hyperliquid perpetual, it prints
  `GTC is unavailable on Hyperliquid; no order will be submitted.`

## 8. What to verify against current official docs before live use
Coinbase product availability changes, and so do SDK signatures. Check these against
current official documentation:
- Coinbase Advanced Trade: `create order` configurations (`limit_limit_gtc`,
  `stop_limit_stop_limit_gtc`, `stop_direction=STOP_DIRECTION_STOP_DOWN`), product
  fields (`status`, `trading_disabled`, `base_increment`, `price_increment`,
  `base_min_size`, `quote_min_size`), order statuses, and candle limits (350 per request).
- Hyperliquid: `metaAndAssetCtxs` fields (`szDecimals`, `maxLeverage`, `onlyIsolated`,
  `isDelisted`), price precision (5 significant figures / `6 − szDecimals` decimals),
  the $10 minimum order value, trigger-order semantics, `orderStatus` by cloid, and the
  API-wallet permission model.

If any SDK method or parameter the bot uses is missing, `--live` refuses to start and
names what to check.

## 9. Project layout

```
config.py              environment settings and validation (secrets as SecretStr)
models.py              shared types and exceptions
database.py            SQLite: runs, orders, fills, daily P/L, halt/cooldown state
analysis.py            indicators, swings, support/resistance zones
risk.py                rounding, staged entries, stops, TPs, sizing, liquidation, limits
retry.py               bounded exponential backoff for reads/cancels
coingecko.py           optional CoinGecko screening and pre-trade market check
simulator.py           paper exchange (same interface as the live adapters)
coinbase_adapter.py    Coinbase Advanced Trade spot adapter
hyperliquid_adapter.py Hyperliquid isolated-margin perp adapter
execution.py           venue-neutral engine + walk-forward backtest
cli.py / main.py       command-line interface
tests/                 unit tests (no network needed)
```

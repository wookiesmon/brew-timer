"""CoinGecko screening and pre-trade checks against canned v3 API responses."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
import requests

import cli
import coinbase_adapter
import hyperliquid_adapter
from coingecko import CoinGeckoClient, check_market, parse_coin_id_overrides, screen
from conftest import FakeAdapter, cb_meta, hl_meta, make_candles, make_settings
from models import Venue

NOW = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
FRESH = (NOW - timedelta(minutes=2)).isoformat().replace("+00:00", "Z")


class Response:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            resp = requests.Response()
            resp.status_code = self.status_code
            raise requests.exceptions.HTTPError(str(self.status_code), response=resp)

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, dict(params or {}), dict(headers or {})))
        for suffix, payload in self.routes.items():
            if url.endswith(suffix):
                return payload(params) if callable(payload) else Response(payload)
        return Response({"error": "not found"}, 404)


def market_row(coin_id="gitcoin", price=0.16, volume=40_000_000, updated=FRESH, mcap=15_000_000):
    return {"id": coin_id, "symbol": "gtc", "name": "Gitcoin", "current_price": price, "total_volume": volume,
            "market_cap": mcap, "price_change_percentage_24h": 66.5, "last_updated": updated}


def tickers(usd_volume):
    return {"tickers": [
        {"base": "GTC", "target": "USD", "converted_volume": {"usd": usd_volume}, "is_stale": False, "is_anomaly": False},
        {"base": "GTC", "target": "USD", "converted_volume": {"usd": 10**9}, "is_stale": True, "is_anomaly": False},
        {"base": "GTC", "target": "EUR", "converted_volume": {"usd": 10**9}, "is_stale": False, "is_anomaly": False},
    ]}


def client(tmp_path, routes, **over):
    settings = make_settings(tmp_path, coingecko_enabled=True, coingecko_coin_ids="GTC=gitcoin", **over)
    return CoinGeckoClient(settings, session=FakeSession(routes)), settings


def gtc_meta(price="0.16"):
    return cb_meta(symbol="GTC-USD", base_asset="GTC", last_price=Decimal(price))


# ------------------------------------------------------------------- auth
def test_demo_and_pro_keys_use_the_documented_headers(tmp_path):
    demo = CoinGeckoClient(make_settings(tmp_path, coingecko_api_key="CG-demo-key"))
    assert demo.base_url == "https://api.coingecko.com/api/v3"
    assert demo.headers["x-cg-demo-api-key"] == "CG-demo-key"
    pro = CoinGeckoClient(make_settings(tmp_path, coingecko_api_key="CG-pro-key", coingecko_plan="pro"))
    assert pro.base_url == "https://pro-api.coingecko.com/api/v3"
    assert pro.headers["x-cg-pro-api-key"] == "CG-pro-key"


def test_coin_id_overrides_and_search_resolution(tmp_path):
    assert parse_coin_id_overrides("GTC=gitcoin, btc=bitcoin,bad") == {"GTC": "gitcoin", "BTC": "bitcoin"}
    c, _ = client(tmp_path, {"/search": {"coins": [
        {"id": "obscure-gtc", "symbol": "GTC", "market_cap_rank": 2000},
        {"id": "other", "symbol": "GTCX", "market_cap_rank": 1},
        {"id": "real-coin", "symbol": "gtc", "market_cap_rank": 300},
    ]}})
    c.overrides = {}
    assert c.resolve_coin_id("gtc") == "real-coin"


# ---------------------------------------------------------- pre-trade check
def test_healthy_market_passes(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": [market_row()], "/coins/gitcoin/tickers": tickers(2_000_000)})
    result = check_market(c, gtc_meta("0.161"), s, planned_notional=Decimal("200"), now=NOW)
    assert result.ok, result.problems
    assert result.deviation_pct < 1 and result.venue_volume_usd == Decimal("2000000")


def test_price_deviation_refuses(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": [market_row(price=0.16)], "/coins/gitcoin/tickers": tickers(2_000_000)})
    result = check_market(c, gtc_meta("0.17"), s, now=NOW)  # 6% away
    assert not result.ok and "differs from CoinGecko" in result.problems[0]


def test_stale_reference_price_skips_comparison(tmp_path):
    old = (NOW - timedelta(hours=2)).isoformat()
    c, s = client(tmp_path, {"/coins/markets": [market_row(price=0.10, updated=old)],
                             "/coins/gitcoin/tickers": tickers(2_000_000)})
    result = check_market(c, gtc_meta("0.16"), s, now=NOW)
    assert result.ok and result.deviation_pct is None and "stale" in result.notes[0]


def test_thin_markets_refuse(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": [market_row(volume=500_000)], "/coins/gitcoin/tickers": tickers(50_000)})
    result = check_market(c, gtc_meta(), s, now=NOW)
    text = " ".join(result.problems)
    assert "below COINGECKO_MIN_VOLUME_USD" in text and "below COINGECKO_MIN_VENUE_VOLUME_USD" in text


def test_position_too_large_for_venue_volume_refuses(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": [market_row()], "/coins/gitcoin/tickers": tickers(300_000)})
    result = check_market(c, gtc_meta(), s, planned_notional=Decimal("10000"), now=NOW)  # 3.3% of volume
    assert any("of Coinbase's 24h volume" in p for p in result.problems)


def test_unreachable_coingecko_fails_closed(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": lambda p: Response({}, 503)}, max_retries=0)
    result = check_market(c, gtc_meta(), s, now=NOW)
    assert not result.ok and "unavailable" in result.problems[0]


def test_hyperliquid_skips_spot_venue_volume(tmp_path):
    c, s = client(tmp_path, {"/coins/markets": [market_row()]})
    meta = hl_meta(symbol="GTC", base_asset="GTC", mark_price=Decimal("0.1601"))
    result = check_market(c, meta, s, now=NOW)
    assert result.ok and result.venue_volume_usd is None
    assert not any("/tickers" in url for url, _, _ in c.session.calls)


def test_responses_are_cached_to_respect_the_demo_call_cap(tmp_path):
    now = {"t": 0.0}
    settings = make_settings(tmp_path, coingecko_enabled=True, coingecko_coin_ids="GTC=gitcoin")
    session = FakeSession({"/coins/markets": [market_row()], "/coins/gitcoin/tickers": tickers(2_000_000)})
    c = CoinGeckoClient(settings, session=session, clock=lambda: now["t"])
    for _ in range(10):  # ten 30-second polls
        check_market(c, gtc_meta(), settings, now=NOW)
        now["t"] += 30
    assert c.calls == 2  # one price call (5-min cache) + one volume call (1-hour cache)
    now["t"] += 300
    check_market(c, gtc_meta(), settings, now=NOW)
    assert c.calls == 3  # price refreshed, volume still cached


def test_paid_plan_refreshes_prices_every_minute(tmp_path):
    now = {"t": 0.0}
    settings = make_settings(tmp_path, coingecko_enabled=True, coingecko_coin_ids="GTC=gitcoin",
                             coingecko_plan="pro", coingecko_api_key="CG-pro-key")
    session = FakeSession({"/coins/markets": [market_row()], "/coins/gitcoin/tickers": tickers(2_000_000)})
    c = CoinGeckoClient(settings, session=session, clock=lambda: now["t"])
    check_market(c, gtc_meta(), settings, now=NOW)
    now["t"] += 61
    check_market(c, gtc_meta(), settings, now=NOW)
    assert c.calls == 3  # price fetched twice, volume once
    assert all(url.startswith("https://pro-api.coingecko.com/api/v3") for url, _, _ in session.calls)
    assert all(h.get("x-cg-pro-api-key") == "CG-pro-key" for _, _, h in session.calls)


# --------------------------------------------------------------- screening
def test_screen_keeps_only_venue_listed_liquid_coins(tmp_path):
    top = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 60000, "total_volume": 3e10,
         "market_cap": 1.2e12, "price_change_percentage_24h": 1.0},
        {"id": "not-on-venue", "symbol": "zzz", "name": "Z", "current_price": 1, "total_volume": 2e10},
        {"id": "gitcoin", "symbol": "gtc", "name": "Gitcoin", "current_price": 0.16, "total_volume": 4e7,
         "market_cap": 1.5e7, "price_change_percentage_24h": 66.5},
        {"id": "gtc-clone", "symbol": "gtc", "name": "Clone", "current_price": 9, "total_volume": 2e6},
        {"id": "tiny", "symbol": "tny", "name": "Tiny", "current_price": 1, "total_volume": 10},
    ]
    routes = {"/coins/markets": lambda p: Response(top if p.get("page") == 1 else []),
              "/tickers": tickers(1_000_000)}
    c, s = client(tmp_path, routes)
    rows = screen(c, {"BTC": "BTC-USD", "GTC": "GTC-USD", "TNY": "TNY-USD"}, s, venue=Venue.COINBASE)
    assert [r.venue_symbol for r in rows] == ["BTC-USD", "GTC-USD"]
    gtc = rows[1]
    assert gtc.coin_id == "gitcoin" and gtc.ambiguous and gtc.venue_volume_usd == Decimal("1000000")


def test_venue_symbol_listings():
    class Client:
        def get_public_products(self, product_type, get_all_products):
            return {"products": [
                {"product_id": "GTC-USD", "base_currency_id": "GTC", "quote_currency_id": "USD", "status": "online"},
                {"product_id": "GTC-USDC", "base_currency_id": "GTC", "quote_currency_id": "USDC", "status": "online"},
                {"product_id": "OLD-USD", "base_currency_id": "OLD", "quote_currency_id": "USD", "status": "delisted"},
                {"product_id": "ETH-EUR", "base_currency_id": "ETH", "quote_currency_id": "EUR", "status": "online"},
                {"product_id": "SOL-USDC", "base_currency_id": "SOL", "quote_currency_id": "USDC", "status": "online"},
            ]}

    assert coinbase_adapter.list_spot_symbols(Client()) == {"GTC": "GTC-USD", "SOL": "SOL-USDC"}
    meta = [{"universe": [{"name": "BTC", "szDecimals": 5, "maxLeverage": 40},
                          {"name": "OLD", "szDecimals": 1, "maxLeverage": 3, "isDelisted": True}]},
            [{"markPx": "60000"}, {"markPx": "1"}]]
    assert hyperliquid_adapter.list_perp_symbols(meta) == {"BTC": "BTC"}


# ------------------------------------------------------------ integration
def test_analyze_refuses_plan_when_coingecko_check_fails(tmp_path, monkeypatch, capsys):
    settings = make_settings(tmp_path, coingecko_enabled=True)
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: FakeAdapter(cb_meta(), make_candles()))

    class Failing:
        def __init__(self, *a, **k):
            pass

    import coingecko

    monkeypatch.setattr(coingecko, "CoinGeckoClient", Failing)
    monkeypatch.setattr(coingecko, "check_market", lambda *a, **k: coingecko.MarketCheck(
        "test", None, None, None, None, None, None, None, problems=["24h volume too low"]))
    assert cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--analyze"], settings=settings) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "REFUSE new plans" in out and "CoinGecko: 24h volume too low" in out


def test_paper_does_not_start_a_run_on_a_refused_market(tmp_path, monkeypatch):
    import coingecko
    from database import Database

    settings = make_settings(tmp_path, coingecko_enabled=True)
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: FakeAdapter(cb_meta(), make_candles()))
    monkeypatch.setattr(coingecko, "CoinGeckoClient", lambda *a, **k: None)
    monkeypatch.setattr(coingecko, "check_market", lambda *a, **k: coingecko.MarketCheck(
        "test", None, None, None, None, None, None, None, problems=["thin"]))
    code = cli.main(["--venue", "coinbase", "--product", "TEST-USD", "--paper", "--once"], settings=settings)
    assert code == cli.EXIT_REFUSED
    assert not Database(settings.paper_database_path).runs("coinbase", "TEST-USD", "paper")


def test_screen_command_needs_no_product(tmp_path, monkeypatch, capsys):
    import coingecko

    settings = make_settings(tmp_path)
    fake = FakeAdapter(cb_meta(), make_candles())
    fake.list_tradable_symbols = lambda: {"GTC": "GTC-USD"}
    monkeypatch.setattr(cli, "make_adapter", lambda *a, **k: fake)
    session = FakeSession({"/coins/markets": lambda p: Response([market_row()] if p.get("page") == 1 else []),
                           "/tickers": tickers(500_000)})
    real = coingecko.CoinGeckoClient
    monkeypatch.setattr(coingecko, "CoinGeckoClient", lambda s: real(s, session=session))
    assert cli.main(["--venue", "coinbase", "--screen"], settings=settings) == cli.EXIT_OK
    out = capsys.readouterr().out
    assert "GTC-USD" in out and "not a recommendation" in out


@pytest.mark.parametrize("bad", [{"coingecko_plan": "enterprise"}, {"coingecko_max_price_deviation_pct": Decimal(0)}])
def test_invalid_coingecko_settings(tmp_path, bad):
    with pytest.raises(ValueError):
        make_settings(tmp_path, **bad)

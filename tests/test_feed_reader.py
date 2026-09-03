"""Tests voor de fetcher-hardening: retry/back-off en het bewaren van
laatst bekende data bij een falende bron.

Draaien:  python3 -m pytest
of:       python3 tests/test_feed_reader.py
"""
import sys
import urllib.error
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.feed_reader import _retry_wait, prune_old
from src.models import Item


def _http_error(retry_after=None):
    hdrs = Message()
    if retry_after is not None:
        hdrs["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://x.test/feed/", 403, "Forbidden", hdrs, None)


def _item(source_name, dagen_oud):
    pub = (datetime.now(timezone.utc) - timedelta(days=dagen_oud)).isoformat()
    return Item(
        title="t", summary="s", published_at=pub, fetched_at=pub,
        source_name=source_name, source_url=f"https://x.test/{source_name}/{dagen_oud}",
        feed_url="https://x.test/feed/", category="busreizen",
    )


def test_retry_wait_volgt_korte_retry_after():
    assert _retry_wait(_http_error(30), attempt=1) == 30.0


def test_retry_wait_geeft_op_bij_lange_retry_after():
    # mobiliteit.nl gaf Retry-After: 3000 -> deze run opgeven
    assert _retry_wait(_http_error(3000), attempt=1) is None


def test_retry_wait_exponentiele_backoff_zonder_header():
    b = config.RETRY_BACKOFF_SECONDS
    assert _retry_wait(_http_error(None), attempt=1) == b
    assert _retry_wait(_http_error(None), attempt=2) == b * 2


def test_prune_bewaart_items_van_gefaalde_bron():
    items = [
        _item("Mobiliteit", 400),   # oud, bron faalde -> behouden
        _item("Festivalinfo", 400), # oud, bron gezond -> weg
        _item("Festivalinfo", 10),  # vers -> behouden
    ]
    over = prune_old(items, retention_days=180, healthy_sources={"Festivalinfo"})
    namen = sorted((it.source_name, it.source_url) for it in over)
    assert ("Mobiliteit", "https://x.test/Mobiliteit/400") in namen
    assert ("Festivalinfo", "https://x.test/Festivalinfo/10") in namen
    assert ("Festivalinfo", "https://x.test/Festivalinfo/400") not in namen


def test_prune_zonder_healthy_set_is_kale_bewaartermijn():
    items = [_item("Mobiliteit", 400), _item("Mobiliteit", 10)]
    over = prune_old(items, retention_days=180)
    assert len(over) == 1
    assert over[0].source_url.endswith("/10")


if __name__ == "__main__":
    funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    mislukt = 0
    for f in funcs:
        try:
            f()
            print(f"OK   {f.__name__}")
        except AssertionError as e:
            mislukt += 1
            print(f"FOUT {f.__name__}: {e}")
    sys.exit(1 if mislukt else 0)

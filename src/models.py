"""Datamodel: de twee objecten waar het dashboard mee werkt.

- Source : een bron (RSS-feed) die we periodiek ophalen.
- Item   : één nieuws- of trenditem dat uit een feed komt.

We gebruiken dataclasses (standaard Python) zodat de structuur duidelijk is en
we makkelijk van/naar JSON kunnen converteren.
"""
from __future__ import annotations

import hashlib
import html as _html
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from .config import MAX_SUMMARY_CHARS

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Verwijder HTML-tags en zet entiteiten om naar gewone tekens.

    Feeds als Mobiliteit.nl en Transport-online leveren de samenvatting als HTML
    (bv. <p>...</p>); wij bewaren alleen platte tekst.
    """
    text = _TAG_RE.sub(" ", text or "")
    return _html.unescape(text)


def make_id(source_url: str) -> str:
    """Stabiele, korte id op basis van de artikel-URL.

    Zelfde URL -> zelfde id, zodat we een item nooit dubbel opslaan.
    """
    digest = hashlib.sha1(source_url.strip().encode("utf-8")).hexdigest()
    return digest[:16]


def shorten(text: str, limit: int = MAX_SUMMARY_CHARS) -> str:
    """Kort een tekst in tot `limit` tekens. Bewaart nooit een heel artikel."""
    text = " ".join(strip_html(text or "").split())  # HTML weg + witruimte normaliseren
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"  # ... aan het eind


# --------------------------------------------------------------------------
# Source
# --------------------------------------------------------------------------
@dataclass
class Source:
    name: str                 # weergavenaam, bv. "Festivalinfo – nieuws"
    type: str                 # "rss" | "api" | "scrape"
    url: str                  # feed-/API-endpoint of te scrapen pagina
    category: str             # "festival" | "busreizen" | "branche-algemeen"
    status: str = "actief"    # "actief" | "test" | "wacht-op-goedkeuring" | "uit"
    language: str = "nl"
    # Alleen relevant bij type == "scrape":
    robots_checked_at: Optional[str] = None
    approved_by_user_at: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> "Source":
        return Source(**{k: v for k, v in d.items() if k in Source.__dataclass_fields__})

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# Item
# --------------------------------------------------------------------------
@dataclass
class Item:
    title: str
    summary: str
    published_at: str          # ISO 8601, bv. "2026-08-20T09:30:00+02:00"
    fetched_at: str            # ISO 8601, moment van ophalen
    source_name: str
    source_url: str            # link naar het originele artikel
    feed_url: str              # de feed waaruit het item kwam
    category: str              # "festival" | "busreizen" | "branche-algemeen"
    tags: List[str] = field(default_factory=list)
    language: str = "nl"
    festivals: List[str] = field(default_factory=list)
    region: Optional[str] = None
    image_url: Optional[str] = None
    id: str = ""               # wordt in __post_init__ gezet als hij leeg is

    def __post_init__(self) -> None:
        if not self.id:
            self.id = make_id(self.source_url)
        self.summary = shorten(self.summary)

    @staticmethod
    def from_dict(d: dict) -> "Item":
        return Item(**{k: v for k, v in d.items() if k in Item.__dataclass_fields__})

    def to_dict(self) -> dict:
        return asdict(self)

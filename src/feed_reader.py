"""Feeds ophalen, parsen, ontdubbelen en opslaan.

Bewust met alleen de Python-standaardbibliotheek (urllib + xml.etree), zodat het
project zonder extra installaties draait. Later kunnen we dit vervangen door
`feedparser` als we meer robuustheid willen.

Belangrijk (projectregels):
- Nette, neutrale User-Agent (zie config.USER_AGENT).
- Redelijke pauze tussen verzoeken naar dezelfde host.
- Alleen metadata opslaan: titel, datum, samenvatting, bron-URL. Geen volledige artikelen.
- Geen persoonsgegevens verzamelen.
"""
from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET

from .config import (
    ITEMS_FILE,
    MIN_DELAY_BETWEEN_REQUESTS,
    REQUEST_TIMEOUT,
    RETENTION_DAYS,
    SOURCES_FILE,
    USER_AGENT,
)
from .models import Item, Source
from .tagging import assign_tags

# Onthoudt per host het tijdstip van het laatste verzoek (voor rate limiting).
_last_request_at: Dict[str, float] = {}


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
def _respect_rate_limit(host: str) -> None:
    """Wacht indien nodig zodat we dezelfde host niet te snel achter elkaar bevragen."""
    last = _last_request_at.get(host)
    if last is not None:
        wachten = MIN_DELAY_BETWEEN_REQUESTS - (time.monotonic() - last)
        if wachten > 0:
            time.sleep(wachten)
    _last_request_at[host] = time.monotonic()


def fetch_url(url: str) -> bytes:
    """Haal een URL op met onze neutrale User-Agent. Geeft de ruwe bytes terug."""
    host = urlparse(url).netloc
    _respect_rate_limit(host)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return resp.read()


def robots_allows(url: str) -> bool:
    """Check de robots.txt van een site voor onze User-Agent.

    Gebruiken we (nu nog) niet voor de RSS-bronnen, maar wel zodra we een
    scrape-bron toevoegen.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        # Geen robots.txt kunnen lezen -> voorzichtig zijn, niet scrapen.
        return False
    return rp.can_fetch(USER_AGENT, url)


# --------------------------------------------------------------------------
# Parsen (RSS 2.0 en Atom)
# --------------------------------------------------------------------------
_ATOM = "{http://www.w3.org/2005/Atom}"


def _text(element) -> str:
    return (element.text or "").strip() if element is not None else ""


def _parse_date(raw: str) -> str:
    """Zet een datumtekst uit een feed om naar ISO 8601. Valt terug op 'nu' bij twijfel."""
    raw = (raw or "").strip()
    if raw:
        # RSS: "Wed, 20 Aug 2026 09:30:00 +0200"
        try:
            return parsedate_to_datetime(raw).isoformat()
        except (TypeError, ValueError):
            pass
        # Atom: "2026-08-20T09:30:00Z" of met offset
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()


def parse_feed(content: bytes, source: Source) -> List[Item]:
    """Parse feed-bytes naar een lijst Item-objecten."""
    root = ET.fromstring(content)
    now_iso = datetime.now(timezone.utc).isoformat()
    items: List[Item] = []

    # RSS 2.0: <rss><channel><item>...
    entries = root.findall(".//item")
    is_atom = False
    if not entries:
        # Atom: <feed><entry>...
        entries = root.findall(f".//{_ATOM}entry")
        is_atom = True

    for entry in entries:
        if is_atom:
            title = _text(entry.find(f"{_ATOM}title"))
            link_el = entry.find(f"{_ATOM}link")
            link = link_el.get("href", "") if link_el is not None else ""
            summary = _text(entry.find(f"{_ATOM}summary")) or _text(entry.find(f"{_ATOM}content"))
            date_raw = _text(entry.find(f"{_ATOM}updated")) or _text(entry.find(f"{_ATOM}published"))
        else:
            title = _text(entry.find("title"))
            link = _text(entry.find("link"))
            summary = _text(entry.find("description"))
            date_raw = _text(entry.find("pubDate"))

        if not link or not title:
            continue  # onbruikbaar item overslaan

        item = Item(
            title=title,
            summary=summary,
            published_at=_parse_date(date_raw),
            fetched_at=now_iso,
            source_name=source.name,
            source_url=link,
            feed_url=source.url,
            category=source.category,
            language=source.language,
        )
        item.tags = assign_tags(item.title, item.summary)
        items.append(item)

    return items


# --------------------------------------------------------------------------
# Opslag
# --------------------------------------------------------------------------
def load_sources(path=SOURCES_FILE) -> List[Source]:
    with open(path, "r", encoding="utf-8") as f:
        return [Source.from_dict(d) for d in json.load(f)]


def load_items(path=ITEMS_FILE) -> List[Item]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [Item.from_dict(d) for d in json.load(f)]


def save_items(items: List[Item], path=ITEMS_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Nieuwste eerst wegschrijven, zodat het bestand prettig leesbaar is.
    ordered = sorted(items, key=lambda it: it.published_at, reverse=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([it.to_dict() for it in ordered], f, ensure_ascii=False, indent=2)
        f.write("\n")


def merge_items(bestaand: List[Item], nieuw: List[Item]) -> List[Item]:
    """Voeg nieuwe items toe, ontdubbeld op id. Bestaande items blijven staan."""
    per_id = {it.id: it for it in bestaand}
    toegevoegd = 0
    for it in nieuw:
        if it.id not in per_id:
            per_id[it.id] = it
            toegevoegd += 1
    print(f"  {toegevoegd} nieuw(e) item(s) toegevoegd, {len(nieuw) - toegevoegd} al bekend")
    return list(per_id.values())


def prune_old(items: List[Item], retention_days: int = RETENTION_DAYS) -> List[Item]:
    """Verwijder items ouder dan de bewaartermijn (standaard 180 dagen)."""
    grens = datetime.now(timezone.utc) - timedelta(days=retention_days)
    behouden: List[Item] = []
    for it in items:
        try:
            pub = datetime.fromisoformat(it.published_at)
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
        except ValueError:
            behouden.append(it)  # onparseerbare datum -> voor de zekerheid behouden
            continue
        if pub >= grens:
            behouden.append(it)
    verwijderd = len(items) - len(behouden)
    if verwijderd:
        print(f"  {verwijderd} item(s) ouder dan {retention_days} dagen opgeschoond")
    return behouden


# --------------------------------------------------------------------------
# Hoofdroutine
# --------------------------------------------------------------------------
def run() -> None:
    """Haal alle actieve RSS-bronnen op en werk data/items.json bij."""
    sources = load_sources()
    items = load_items()

    for source in sources:
        if source.status != "actief":
            print(f"- {source.name}: overgeslagen (status: {source.status})")
            continue
        if source.type != "rss":
            print(f"- {source.name}: overgeslagen (type {source.type} nog niet ondersteund)")
            continue

        print(f"- {source.name}: ophalen {source.url}")
        try:
            content = fetch_url(source.url)
            nieuw = parse_feed(content, source)
            print(f"  {len(nieuw)} item(s) in de feed")
            items = merge_items(items, nieuw)
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"  FOUT bij ophalen: {e}")
        except ET.ParseError as e:
            print(f"  FOUT bij parsen: {e}")

    items = prune_old(items)
    save_items(items)
    print(f"\nKlaar. Totaal {len(items)} item(s) in {ITEMS_FILE}")

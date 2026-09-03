"""Centrale instellingen voor het dashboard-project (concept-fase).

Alles staat hier bij elkaar zodat we later maar op één plek hoeven aan te passen.
"""
from __future__ import annotations

from pathlib import Path

# Basispaden ----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

SOURCES_FILE = CONFIG_DIR / "sources.json"   # de vaste lijst met bronnen (feeds)
ITEMS_FILE = DATA_DIR / "items.json"         # alle verzamelde nieuws-/trenditems
FETCH_STATE_FILE = DATA_DIR / "fetch_state.json"  # per bron: laatste ophaalresultaat

# Ophalen -----------------------------------------------------------------
# Neutrale User-Agent: GEEN bedrijfsnaam gebruiken tijdens de testfase.
USER_AGENT = "InternalDashboardTest/0.1"

# Extra request-headers. Sommige bronnen (bv. mobiliteit.nl achter Cloudflare)
# weigeren "kale" verzoeken; een browser-achtige set Accept-headers helpt daar.
# Bewust GEEN Accept-Encoding: urllib pakt gzip niet vanzelf uit.
HTTP_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, text/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "nl,en;q=0.8",
}

# Time-out per HTTP-verzoek (seconden).
REQUEST_TIMEOUT = 20

# Minimale pauze tussen twee verzoeken naar dezelfde host (seconden).
# Zo blijven we netjes binnen redelijke rate limits.
MIN_DELAY_BETWEEN_REQUESTS = 3

# Opnieuw proberen bij een tijdelijke fout ------------------------------
# HTTP-statussen die we als "misschien tijdelijk" behandelen en opnieuw proberen.
RETRYABLE_STATUS = frozenset({403, 429, 500, 502, 503, 504})

# Aantal extra pogingen na de eerste (dus 2 = maximaal 3 verzoeken).
MAX_FETCH_RETRIES = 2

# Basiswachttijd voor exponentiële back-off (seconden): 5, 10, 20, ...
RETRY_BACKOFF_SECONDS = 5

# Respecteer de Retry-After-header, maar wacht nooit langer dan dit (seconden).
# Vraagt de server om méér (mobiliteit.nl gaf 3000s), dan geven we deze run op
# en behouden we de laatst bekende data.
MAX_RETRY_AFTER_WAIT = 120

# Ophaalmomenten (informatief; het echte plannen doen we later met cron/launchd
# of de schedule-functie). Dagelijks om 08:30 en 13:00, tijdzone Europe/Amsterdam.
SCHEDULE_TIMES = ("08:30", "13:00")
SCHEDULE_TIMEZONE = "Europe/Amsterdam"

# Bewaren ---------------------------------------------------------------
# Items ouder dan dit aantal dagen worden bij het opschonen verwijderd.
RETENTION_DAYS = 180

# Samenvatting nooit langer dan dit aantal tekens opslaan (geen volledige artikelen).
MAX_SUMMARY_CHARS = 150

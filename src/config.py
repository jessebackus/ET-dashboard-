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

# Ophalen -----------------------------------------------------------------
# Neutrale User-Agent: GEEN bedrijfsnaam gebruiken tijdens de testfase.
USER_AGENT = "InternalDashboardTest/0.1"

# Time-out per HTTP-verzoek (seconden).
REQUEST_TIMEOUT = 20

# Minimale pauze tussen twee verzoeken naar dezelfde host (seconden).
# Zo blijven we netjes binnen redelijke rate limits.
MIN_DELAY_BETWEEN_REQUESTS = 3

# Ophaalmomenten (informatief; het echte plannen doen we later met cron/launchd
# of de schedule-functie). Dagelijks om 08:30 en 13:00, tijdzone Europe/Amsterdam.
SCHEDULE_TIMES = ("08:30", "13:00")
SCHEDULE_TIMEZONE = "Europe/Amsterdam"

# Bewaren ---------------------------------------------------------------
# Items ouder dan dit aantal dagen worden bij het opschonen verwijderd.
RETENTION_DAYS = 180

# Samenvatting nooit langer dan dit aantal tekens opslaan (geen volledige artikelen).
MAX_SUMMARY_CHARS = 150

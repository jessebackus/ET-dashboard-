#!/usr/bin/env python3
"""Haalt de RSS-bronnen op en werkt data/items.json bij.

Gebruik:
    python3 scripts/run_fetch.py

Dit script maakt echte HTTP-verzoeken naar de bronnen in config/sources.json.
Draai het handmatig, of later automatisch om 08:30 en 13:00 (Europe/Amsterdam).
"""
import sys
from pathlib import Path

# Zorg dat de map 'src' importeerbaar is, ongeacht vanwaar je het script start.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feed_reader import run

if __name__ == "__main__":
    run()

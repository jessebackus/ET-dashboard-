"""Regelgebaseerd tags toekennen aan items.

Simpele keyword-matching op titel + samenvatting. Bewust eenvoudig gehouden in
v1; later eventueel te vervangen door een LLM-classificatie.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

# Per tag een lijst met signaalwoorden (kleine letters). Matcht op hele of
# gedeeltelijke woorden via een simpele "in string"-check.
TAG_RULES: Dict[str, Tuple[str, ...]] = {
    "line-up": ("line-up", "lineup", "affiche", "namen bekend", "headliner", "headliners"),
    "aankondiging": ("aangekondigd", "kondigt aan", "kondigt", "bekendgemaakt",
                      "bekend gemaakt", "maakt bekend", "namen bekend",
                      "announces", "reveals", "onthult", "onthuld"),
    "trend": ("trend", "groei", "stijging", "daling", "onderzoek", "rapport", "groeit"),
    "incident": ("ongeluk", "ongeval", "brand", "afgelast", "geannuleerd", "cancelled",
                  "gewonden"),
    "beleid": ("regelgeving", "vergunning", "vergunningstelsel", "zero-emissie",
                "zero-emissiezone", "wet", "kabinet", "gemeente", "regels"),
    "cijfers": ("omzet", "bezoekers", "recordaantal", "record", "miljoen", "procent",
                 "reizigerskilometers", "%"),
    "ticketing": ("kaartverkoop", "tickets", "kaarten", "uitverkocht", "sold out",
                   "pre-sale", "presale"),
}


def assign_tags(title: str, summary: str) -> List[str]:
    """Geef de lijst tags terug die passen bij deze titel + samenvatting."""
    haystack = f"{title} {summary}".lower()
    tags: List[str] = []
    for tag, keywords in TAG_RULES.items():
        if any(kw in haystack for kw in keywords):
            tags.append(tag)
    return tags

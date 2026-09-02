"""Kleine tests voor de tag-regels.

Draaien kan met pytest:  python3 -m pytest
of zonder pytest:        python3 tests/test_tagging.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.tagging import assign_tags
from src.models import make_id, shorten, strip_html


def test_lineup_en_aankondiging():
    tags = assign_tags("Lowlands maakt eerste namen bekend", "De line-up wordt onthuld.")
    assert "line-up" in tags
    assert "aankondiging" in tags


def test_beleid_en_busreizen_context():
    tags = assign_tags("Nieuwe regels rond zero-emissiezones", "Gemeenten passen de regelgeving aan.")
    assert "beleid" in tags


def test_cijfers():
    tags = assign_tags("Recordaantal bezoekers", "Ruim tweehonderdduizend bezoekers, tien procent meer.")
    assert "cijfers" in tags


def test_geen_valse_tags():
    tags = assign_tags("Weerbericht voor het weekend", "Het wordt zonnig en droog.")
    assert tags == []


def test_make_id_stabiel():
    a = make_id("https://voorbeeld.test/artikel-1")
    b = make_id(" https://voorbeeld.test/artikel-1 ")
    assert a == b
    assert len(a) == 16


def test_shorten_kort_in():
    lang = "woord " * 200
    assert len(shorten(lang, limit=100)) <= 100


def test_shorten_verwijdert_html():
    resultaat = shorten("<p>Gemeenten mogen bussen <strong>weren</strong> &amp; beperken.</p>")
    assert "<" not in resultaat
    assert "&amp;" not in resultaat
    assert "weren & beperken" in resultaat


def test_strip_html_basis():
    assert strip_html("<p>Hallo &euro;5</p>").strip() == "Hallo €5"


if __name__ == "__main__":
    # Simpele runner zonder pytest.
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

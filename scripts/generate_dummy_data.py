#!/usr/bin/env python3
"""Vult data/items.json met verzonnen testdata (geen echte bronnen).

Gebruik:
    python3 scripts/generate_dummy_data.py

Zo kunnen we het datamodel en straks het dashboard bouwen en bekijken zonder
echte feeds op te halen. De inhoud hieronder is volledig fictief.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import Item
from src.tagging import assign_tags
from src.feed_reader import save_items

# Vast referentiemoment zodat de dummydata reproduceerbaar is.
NU = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)

# (dagen geleden, bron_naam, feed_url, categorie, titel, samenvatting)
DUMMY = [
    (3, "Festivalinfo – nieuws", "https://www.festivalinfo.nl/rss/FestivalinfoNewsRSS.xml",
     "festival", "Lowlands 2027 maakt eerste namen bekend",
     "De organisatie onthult de eerste twintig acts voor de editie van volgend jaar. De volledige line-up volgt in het voorjaar."),
    (6, "Festivalinfo – nieuws", "https://www.festivalinfo.nl/rss/FestivalinfoNewsRSS.xml",
     "festival", "Onderzoek: festivalbezoek onder 18- tot 25-jarigen stijgt met 8 procent",
     "Een nieuw rapport laat een duidelijke groei zien in het aantal jonge festivalbezoekers ten opzichte van vorig jaar."),
    (11, "Festivalinfo – nieuws", "https://www.festivalinfo.nl/rss/FestivalinfoNewsRSS.xml",
     "festival", "Pinkpop kondigt extra festivaldag aan voor 2027",
     "Het festival in Landgraaf breidt uit naar vier dagen. De kaartverkoop start volgende maand."),
    (2, "Festivalinfo – festivalagenda", "https://www.festivalinfo.nl/rss/FestivalinfoFestivalRSS.xml",
     "festival", "Nieuw festival toegevoegd: Zeezicht Open Air in Bloemendaal",
     "Een eendaags strandfestival met housemuziek, gepland voor eind juni 2027."),
    (8, "Festivalinfo – festivalagenda", "https://www.festivalinfo.nl/rss/FestivalinfoFestivalRSS.xml",
     "festival", "Down The Rabbit Hole 2027 – datum bekendgemaakt",
     "Het festival vindt volgend jaar plaats van 2 tot en met 4 juli op de Groene Heuvels in Ewijk."),
    (1, "FestivalFans.nl", "https://festivalfans.nl/feed/",
     "festival", "Deze headliners speelt DGTL volgend jaar in Amsterdam",
     "De affiche voor het paasweekend is rond. Onder de namen bekend gemaakt vandaag staan meerdere internationale techno-acts."),
    (4, "FestivalFans.nl", "https://festivalfans.nl/feed/",
     "festival", "Kaartverkoop Milkshake Festival 2027 van start",
     "De reguliere tickets zijn vanaf vrijdag verkrijgbaar. Vorig jaar was het festival binnen een week uitverkocht."),
    (9, "FestivalFans.nl", "https://festivalfans.nl/feed/",
     "festival", "Verslag: Awakenings 2026 trok recordaantal bezoekers",
     "Met ruim tweehonderdduizend bezoekers over het hele weekend was dit de best bezochte editie tot nu toe."),
    (2, "Mobiliteit.nl – touringcar", "https://www.mobiliteit.nl/tag/touringcar/feed/",
     "busreizen", "Touringcarsector vreest chauffeurstekort in aanloop naar festivalseizoen",
     "Branchepartijen waarschuwen dat de vraag naar besloten busvervoer sneller groeit dan het aantal beschikbare chauffeurs."),
    (7, "Mobiliteit.nl – touringcar", "https://www.mobiliteit.nl/tag/touringcar/feed/",
     "busreizen", "Nieuwe regels rond zero-emissiezones raken touringcars vanaf 2028",
     "Een aantal gemeenten wil vanaf 2028 ook touringcars weren uit de binnenstad. De branche vraagt om uitstel."),
    (12, "Mobiliteit.nl – touringcar", "https://www.mobiliteit.nl/tag/touringcar/feed/",
     "busreizen", "Ongeluk met touringcar op de A2, geen gewonden",
     "Een touringcar op weg naar een evenement raakte van de weg. Alle inzittenden konden ongedeerd uitstappen."),
    (3, "Transport-online.nl", "https://www.transport-online.nl/feed/",
     "busreizen", "Touringcarbedrijven boeken recordomzet door festivalvervoer",
     "Het aandeel van evenementenvervoer in de jaaromzet is dit jaar met tien procent gestegen."),
    (6, "Transport-online.nl", "https://www.transport-online.nl/feed/",
     "busreizen", "Brancheorganisatie: vraag naar busvervoer naar buitenlandse festivals groeit",
     "Vooral reizen naar festivals in Duitsland en België laten een duidelijke stijging zien."),
    (14, "Transport-online.nl", "https://www.transport-online.nl/feed/",
     "busreizen", "Vergunningstelsel voor internationaal busvervoer gaat op de schop",
     "Het ministerie werkt aan nieuwe regelgeving die de vergunningaanvraag voor grensoverschrijdend vervoer moet vereenvoudigen."),
]


def build_items():
    items = []
    for dagen_geleden, bron, feed_url, categorie, titel, samenvatting in DUMMY:
        gepubliceerd = (NU - timedelta(days=dagen_geleden)).isoformat()
        slug = titel.lower().replace(" ", "-")[:60]
        source_url = f"https://voorbeeld.test/{categorie}/{slug}"
        item = Item(
            title=titel,
            summary=samenvatting,
            published_at=gepubliceerd,
            fetched_at=NU.isoformat(),
            source_name=bron,
            source_url=source_url,
            feed_url=feed_url,
            category=categorie,
        )
        item.tags = assign_tags(item.title, item.summary)
        items.append(item)
    return items


if __name__ == "__main__":
    items = build_items()
    save_items(items)
    print(f"{len(items)} dummy-items weggeschreven naar data/items.json")

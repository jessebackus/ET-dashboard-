# Festival & Busreizen Dashboard

Intern hulpmiddel om ET op de hoogte te houden van marktontwikkelingen rond:

- de **festivalbranche** (line-ups, aankondigingen, trends)
- **busreizen naar festivals** (vraag, populaire bestemmingen, aanbod)

**Status:** concept-fase. Alleen dummy/testdata — nog geen echte klant- of bedrijfsdata.
Alleen voor intern gebruik, niet openbaar, niet commercieel.

---

## Mappenstructuur

```
eleven-travel-experiments/
├── README.md              ← dit bestand
├── bronnen.md             ← inventarisatie van databronnen (RSS/API-status)
├── datamodel.md           ← datamodel, dashboardopzet en vastgelegde keuzes
├── requirements.txt       ← v1 heeft geen verplichte packages
├── .github/workflows/
│   └── refresh-feeds.yml  ← draait run_fetch.py 2x/dag en commit data/items.json
├── config/
│   └── sources.json       ← de vaste lijst met bronnen (RSS-feeds)
├── src/
│   ├── config.py          ← centrale instellingen (User-Agent, retentie, paden)
│   ├── models.py          ← datamodel: Source en Item (+ id-berekening, HTML strippen, inkorten)
│   ├── tagging.py         ← regelgebaseerd tags toekennen (keyword-matching)
│   └── feed_reader.py     ← feeds ophalen, parsen, ontdubbelen, opschonen, opslaan
├── scripts/
│   ├── generate_dummy_data.py  ← vult data/items.json met verzonnen testdata
│   ├── run_fetch.py            ← haalt de échte RSS-bronnen op
│   └── serve.py               ← lokale webserver + opent het dashboard
├── dashboard/
│   └── index.html        ← het dashboard (statische pagina, leest data/items.json)
├── data/
│   └── items.json         ← alle verzamelde items (nieuwste eerst)
└── tests/
    └── test_tagging.py    ← kleine tests voor de tag-regels
```

## Aan de slag

Vereist: Python 3.9+ (standaard aanwezig op macOS). Geen installatie nodig voor v1.

### 1. Échte feeds ophalen (maakt HTTP-verzoeken)

```bash
python3 scripts/run_fetch.py
```

Haalt de actieve bronnen uit `config/sources.json` op, voegt nieuwe items toe aan
`data/items.json` (ontdubbeld op `id`) en verwijdert items ouder dan 180 dagen.
`data/items.json` bevat momenteel echte feed-metadata van de eerste testrun.

**Bestand tegen tijdelijke storingen:**
- Verzoeken gaan met browser-achtige `Accept`-headers (sommige bronnen weigeren "kale" requests).
- Bij een tijdelijke fout (HTTP 403/429/5xx of netwerkfout) volgen er tot 2 nieuwe pogingen
  met oplopende wachttijd; een `Retry-After`-header wordt gevolgd, maar nooit langer dan 120 s
  (vraagt de server om meer, dan slaan we die bron deze run over).
- Faalt een bron alsnog, dan blijven de laatst bekende items van die bron staan — ook als ze
  ouder zijn dan 180 dagen — zodat een storing die sectie van het dashboard niet leegtrekt.
- `data/fetch_state.json` (lokaal, niet in git) houdt per bron het laatste resultaat bij
  (`last_success`, `last_status`, `consecutive_failures`).

### 2. Tests draaien

```bash
python3 tests/test_tagging.py
```

### 3. Dashboard bekijken

```bash
python3 scripts/serve.py
```

Start een lokale webserver en opent `http://localhost:8000/dashboard/`. Stoppen met Ctrl+C.
(Het dashboard haalt `data/items.json` op via de browser; rechtstreeks het HTML-bestand
openen werkt daarom niet.)

Het dashboard biedt: KPI-tegels, zoeken in titel/samenvatting, filteren op categorie en bron,
sorteren op datum, en themaknoppen (aankondigingen &amp; line-ups / trends &amp; cijfers /
beleid &amp; incidenten). Elk item linkt door naar het originele artikel.

### 4. Testdata genereren (geen internet, optioneel)

```bash
python3 scripts/generate_dummy_data.py
```

Overschrijft `data/items.json` met ~14 fictieve items. Handig om los van de feeds
iets te testen; draai daarna weer `run_fetch.py` voor echte data.

## Automatisch verversen (GitHub Actions)

`.github/workflows/refresh-feeds.yml` draait `run_fetch.py` op GitHub en commit een
gewijzigde `data/items.json` terug naar `main`.

- **Schema:** 2x per dag, 08:30 en 13:00 Europe/Amsterdam. GitHub-cron draait in UTC
  en kent geen tijdzones, dus elke tijd is dubbel ingepland (voor zomer- én wintertijd).
  Er wordt alleen gecommit als de data echt verandert, dus de "extra" run doet niets.
- **Handmatig testen:** Actions-tab → *Feeds verversen* → *Run workflow*.
- **Rechten:** de workflow gebruikt de ingebouwde `GITHUB_TOKEN` met `contents: write`;
  geen extra secrets of tokens nodig.
- De automatische commits komen van `github-actions[bot]`.

## Vastgelegde keuzes

| Onderwerp | Keuze |
|-----------|-------|
| v1-bronnen | 4 actieve NL RSS-feeds (zie `config/sources.json`); Transport-online staat op `uit` (te veel ruis) |
| Ophaalmomenten | dagelijks 08:30 en 13:00 (Europe/Amsterdam), via GitHub Actions |
| User-Agent | `InternalDashboardTest/0.1` — **geen bedrijfsnaam** tijdens de testfase |
| Bewaartermijn | 180 dagen, daarna opschonen |
| Samenvatting | max 150 tekens — nooit volledige artikelen opslaan |
| Opslag | platte JSON-bestanden, geen database |

## Werkwijze / regels bij bronnen

- Voorkeur voor RSS-feeds en officiële API's.
- Scrapen alleen als er geen feed/API is, en pas **na expliciete goedkeuring per site**.
  Dan eerst `robots.txt` checken (`src/feed_reader.robots_allows`) en nette rate limits aanhouden.
- Alleen metadata opslaan: titel, datum, samenvatting, bron-URL. Geen persoonsgegevens.

## Nog te doen

- Feeds van Follow the Beat / Festileaks testen met een echte User-Agent.
- Dashboard overzetten naar de definitieve hosting (waarschijnlijk Lovable).
- Datumherkenning voor festivalagenda-items (datum staat nu in de titel, niet in `published_at`).
- Eventueel `feedparser` inzetten voor robuustere feed-parsing.

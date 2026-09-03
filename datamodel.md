# Datamodel & dashboardopzet — v1 (concept)

Bijgewerkt 2026-09-02. Concept-fase. `data/items.json` bevat sinds de eerste testrun
echte (publieke) RSS-metadata; nog geen klant- of bedrijfsdata.

---

## 1. Scope v1 — bronnen (bevestigd)

Alleen Nederlandstalige bronnen met een **bevestigde RSS-feed** (geen test- of scrape-bronnen in v1).

| # | Bron | Feed-URL | Categorie |
|---|------|----------|-----------|
| 1 | Festivalinfo — nieuws | `https://www.festivalinfo.nl/rss/FestivalinfoNewsRSS.xml` | festival |
| 2 | Festivalinfo — festivalagenda | `https://www.festivalinfo.nl/rss/FestivalinfoFestivalRSS.xml` | festival |
| 3 | FestivalFans.nl | `https://festivalfans.nl/feed/` | festival |
| 4 | Mobiliteit.nl — tag touringcar | `https://www.mobiliteit.nl/tag/touringcar/feed/` | busreizen |

Bewust nog **niet** in v1:
- **Transport-online.nl** — na de eerste testrun uitgezet (`status: uit`): algemene transport-/logistiekfeed
  zonder touringcar-filter, leverde 0 relevante items.
- IQ Magazine (Engelstalig) — pas later, wanneer we internationale branchetrends willen meenemen.
- Follow the Beat, Festileaks, KNV, Resident Advisor, busreis-aanbieders — na test / goedkeuring.

**Aandachtspunt:** de busreizen-kant leunt nu op één bron (Mobiliteit touringcar-tag, ~3 recente items).
Extra busbronnen zoeken is een openstaand punt (zie sectie 6).

---

## 2. Datamodel

### 2.1 `item` — één nieuws-/trenditem

| Veld | Type | Verplicht | Toelichting |
|------|------|-----------|-------------|
| `id` | string | ja | Stabiele hash van `source_url` (bv. sha1). Voorkomt dubbele opslag. |
| `title` | string | ja | Titel uit de feed. |
| `summary` | string | ja | Korte samenvatting (max 150 tekens). Feed-samenvatting of eigen inkorting. **Nooit het volledige artikel.** |
| `published_at` | datetime (ISO 8601) | ja | Publicatiedatum uit de feed. |
| `fetched_at` | datetime | ja | Wanneer wij het ophaalden. |
| `source_name` | string | ja | Bv. "Festivalinfo". |
| `source_url` | string (URL) | ja | Link naar het originele artikel. |
| `feed_url` | string (URL) | ja | De feed waaruit het kwam. |
| `category` | enum | ja | `festival` \| `busreizen` \| `branche-algemeen` |
| `tags` | list[string] | nee | Bv. `line-up`, `aankondiging`, `trend`, `incident`, `beleid`, `cijfers`, `ticketing`. Regelgebaseerd toegekend (zie 2.3). |
| `language` | string | nee | `nl` \| `en` \| ... |
| `festivals` | list[string] | nee | Genoemde festivals (later via naamherkenning tegen `festival`-lijst). |
| `region` | string | nee | Land/regio indien afleidbaar. |
| `image_url` | string (URL) | nee | Alleen de URL, wij hosten geen afbeeldingen. |

### 2.2 `source` — bronregister

| Veld | Type | Toelichting |
|------|------|-------------|
| `name` | string | Weergavenaam. |
| `type` | enum | `rss` \| `api` \| `scrape` |
| `url` | string | Feed-/API-endpoint of te scrapen pagina. |
| `category` | enum | Zie `item.category`. |
| `status` | enum | `actief` \| `test` \| `wacht-op-goedkeuring` \| `uit` |
| `schedule` | string | Ophaalmomenten (v1: dagelijks 08:30 en 13:00, Europe/Amsterdam). |
| `user_agent` | string | `InternalDashboardTest/0.1` (neutraal, geen bedrijfsnaam tijdens testfase). |
| `robots_checked_at` | date | Alleen relevant bij `type = scrape`. |
| `approved_by_user_at` | date | Alleen bij `type = scrape` — expliciete goedkeuring Jesse. |
| `added_at` | date | |

### 2.3 Tag-toekenning (regelgebaseerd, v1)

Eenvoudige keyword-matching op `title` + `summary` (Nederlands/Engels):

- `line-up` ← "line-up", "lineup", "affiche", "namen bekend", "headliner"
- `aankondiging` ← "aangekondigd", "kondigt aan", "bekendgemaakt", "announces", "reveals"
- `trend` ← "trend", "groei", "stijging", "daling", "onderzoek", "rapport"
- `incident` ← "ongeluk", "brand", "afgelast", "geannuleerd", "cancelled"
- `beleid` ← "regelgeving", "vergunning", "zero-emissie", "wet", "kabinet", "gemeente"
- `cijfers` ← "omzet", "bezoekers", "miljoen", "procent", "reizigerskilometers"
- `ticketing` ← "kaartverkoop", "tickets", "uitverkocht", "sold out"

(Later eventueel vervangen door een LLM-classificatie.)

---

## 3. Opslag

- Vaste bronnenlijst: `config/sources.json` (lijst van `source`-objecten).
- Verzamelde items: `data/items.json` (JSON-array van `item`-objecten, nieuwste eerst).
- Ophaalstatus per bron: `data/fetch_state.json` (lokaal, niet in git) — `last_success`,
  `last_status`, `consecutive_failures`. Diagnostiek; wordt elke run bijgewerkt.
- Dedup op `id`. Nieuwe run voegt alleen nieuwe items toe.
- Retentie: items ouder dan **180 dagen** worden bij elke run opgeschoond — **behalve** items
  van een bron die in díe run niet kon worden opgehaald (dan blijft de laatst bekende set staan,
  zodat een tijdelijke storing de sectie niet leegtrekt).
- Geen database nodig in concept-fase.

---

## 4. Dashboardopzet

### Secties
1. **Festivals — aankondigingen & line-ups** — items `category=festival` met tag `line-up`/`aankondiging`, nieuwste eerst.
2. **Festivals — branche & trends** — `category=festival` of `branche-algemeen` met tag `trend`/`cijfers`/`ticketing`.
3. **Busreizen — branche & beleid** — `category=busreizen`, tags `beleid`/`cijfers`/`incident`.
4. **Busreizen — vraag & aanbod** — v1 grotendeels leeg / placeholder; wordt gevuld zodra aanbieder-bronnen zijn goedgekeurd.
5. **Alle items** — doorzoekbare tabel met filters: datum, categorie, bron, tag, zoektekst.

### Per item op het dashboard
Titel (link naar `source_url`) · bron · datum · samenvatting · tags. Niets meer.

### Verversing
Dashboard (`dashboard/index.html`) leest `data/items.json` via de browser (fetch). Ophalen van
feeds draait apart via `scripts/run_fetch.py`, **dagelijks om 08:30 en 13:00** (Europe/Amsterdam),
niet in de dashboard-app zelf. Lokaal bekijken: `python3 scripts/serve.py`.

### Implementatie v1
Statische HTML + vanilla JavaScript, geen build-stap. Filters: zoektekst, categorie, bron, sortering
op datum, en themaknoppen (aankondigingen &amp; line-ups / trends &amp; cijfers / beleid &amp; incidenten).
Later over te zetten naar Lovable.

---

## 5. Vastgelegde keuzes (2026-09-02)

- **v1-bronnen:** alleen Nederlandstalig, 4 actieve feeds (sectie 1). Transport-online na testrun
  uitgezet; IQ Magazine bewust uitgesteld.
- **Ophaalmomenten:** dagelijks 08:30 en 13:00 (Europe/Amsterdam).
- **User-Agent:** `InternalDashboardTest/0.1` — neutraal, geen bedrijfsnaam tijdens testfase.
- **Retentie:** 180 dagen.
- **Samenvatting:** max 150 tekens.
- **Projectstructuur + feed-reader:** opgezet in Python (stdlib). Zie `README.md`.
- **Eerste echte testrun (2026-09-02):** 4 feeds opgehaald, 43 items in `data/items.json`
  (30 Festivalinfo + 10 FestivalFans + 3 Mobiliteit). HTML uit samenvattingen gestript.
  Dummydata daarna verwijderd — `data/items.json` bevat nu alleen echte feed-items.

## 6. Nog open

1. **Extra busreizen-bron(nen)** zoeken — de buskant is nu erg dun (1 feed, ~3 items).
2. Feeds van Follow the Beat / Festileaks testen met een echte User-Agent.
3. Dashboard overzetten naar de definitieve hosting (waarschijnlijk Lovable).
4. Eventueel `feedparser` inzetten voor robuustere feed-parsing.
5. Overwegen: keyword-relevantiefilter per bron, mochten we later brede feeds toevoegen.

Gereed: automatisch verversen via GitHub Actions (`.github/workflows/refresh-feeds.yml`),
2x/dag + handmatige trigger, commit terug naar `main`.

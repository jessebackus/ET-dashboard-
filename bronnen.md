# Bronnenlijst — Festival & Busreizen Dashboard

Status: **inventarisatie, concept-fase** (bijgewerkt 2026-09-02)

Doel van dit document: overzicht van kandidaat-databronnen, met per bron of er een
RSS-feed of officiële API is. Volgorde van voorkeur volgens projectregels:

1. RSS-feed of officiële API (altijd toegestaan)
2. Scrapen — alléén als er geen feed/API is, ná expliciete goedkeuring per site,
   met robots.txt-check en nette rate limits, en alleen metadata opslaan.

Legenda:
- ✅ RSS/API bevestigd (feed opgehaald en inhoud gecontroleerd)
- ⚠️ Waarschijnlijk RSS, maar niet kunnen bevestigen (bot-blokkade / nog testen)
- ❌ Geen RSS/API gevonden → scrape-kandidaat (goedkeuring nodig)

---

## A. Festivalbranche (line-ups, aankondigingen, trends)

| Bron | Type | Status | Feed-URL / opmerking |
|------|------|--------|----------------------|
| **Festivalinfo.nl** | NL/BE festivalnieuws + agenda | ✅ | Nieuws: `https://www.festivalinfo.nl/rss/FestivalinfoNewsRSS.xml` · Festivalagenda: `https://www.festivalinfo.nl/rss/FestivalinfoFestivalRSS.xml` · Reviews/sfeerverslagen aparte feeds · Gecombineerd nieuws (incl. Podiuminfo): `https://www.festivalinfo.nl/rss/AllinfoNewsRSS.xml` |
| **Podiuminfo.nl** (zelfde uitgever) | Concert-/podiumnieuws | ✅ | Nieuws: `https://www.festivalinfo.nl/rss/PodiuminfoNewsRSS.xml` · Concertagenda: `.../PodiuminfoConcertRSS.xml` |
| **FestivalFans.nl** | NL/BE dance/pop/rock festivalnieuws, line-ups, reviews | ✅ | `https://festivalfans.nl/feed/` (WordPress RSS 2.0). Categorie-feeds mogelijk via `/category/line-up/feed/` — nog testen. |
| **Follow the Beat** | NL festivalnieuws, line-up releases, headliners | ⚠️ | `https://followthebeat.nl/feed/` gaf HTTP 403 bij ophalen (Cloudflare bot-blokkade). WordPress-site, feed bestaat vrijwel zeker — testen met nette User-Agent. |
| **Festileaks.com** | NL/BE festivalnieuws + grote community/forum, line-up-speculatie | ⚠️ | `https://festileaks.com/feed/` gaf HTTP 403 (Cloudflare). robots.txt blokkeert alleen `/wp-admin/` en `/wp-login.php`, geen crawl-delay. Feed testen met echte User-Agent. |
| **IQ Magazine** (iqmagazine.com) | Internationale live-music/festivalbranche: ticketing, touring, festivals, zakelijk | ✅ | `https://www.iqmagazine.com/feed/` (RSS 2.0). Sterk voor markttrends/aankondigingen op sectorniveau. |
| **Resident Advisor** (ra.co) | Internationale elektronische muziek, festivals, line-ups | ❌ (RSS) | Geen publieke RSS gevonden (`/xml/rss` → 404). Heeft een (niet officieel gedocumenteerde) GraphQL-API — gebruik daarvan eerst uitzoeken/toestemming vragen. Anders scrape-kandidaat. |

**Nog te checken (nog niet onderzocht):** Partyflock, DJ Mag, Mixmag, Billboard, Pollstar,
3voor12 (VPRO), Entertainment Business (NL vakblad), Broadcast Magazine, individuele
festival-nieuwspagina's / persrooms (Lowlands, Pinkpop, Tomorrowland, Rock Werchter, Down the Rally, etc.).

---

## B. Busreizen naar festivals (vraag, bestemmingen, aanbod, branche)

| Bron | Type | Status | Feed-URL / opmerking |
|------|------|--------|----------------------|
| **Mobiliteit.nl** (voorheen OVPro.nl) | NL vakmedia OV & touringcar: beleid, incidenten, branche-ontwikkelingen | ✅ | Alle nieuws: `https://www.mobiliteit.nl/feed/` · **Tag-feed touringcar:** `https://www.mobiliteit.nl/tag/touringcar/feed/` (zeer relevant, filtert op touringcar). |
| **Transport-online.nl** | NL transport & logistiek breed | ✅ RSS, maar **uit v1** | `https://www.transport-online.nl/feed/`. Eerste testrun (2026-09-02): 25 items, 0 over touringcar/busreizen. Geen touringcar-feed beschikbaar. Alleen bruikbaar mét keyword-filter — voorlopig `status: uit`. |
| **KNV — Koninklijk Nederlands Vervoer** (knv.nl) | Brancheorganisatie Busvervoer Nederland (BVN); branchecijfers, standpunten, regelgeving (EES/ETIAS, zero-emissiezones) | ❌ | Nieuwspagina `https://www.knv.nl/nieuws/`, geen RSS gevonden. **Scrape-kandidaat** — robots.txt nog checken + jouw goedkeuring nodig. Alleen titel/datum/samenvatting/URL opslaan. |
| Busreis-aanbieders (reisorganisaties die busreizen naar festivals verkopen) | Aanbod-monitoring: welke festivals, prijzen, bestemmingen | ❌ | Per site: eerst robots.txt + expliciete goedkeuring. Alleen metadata (festival, datum, bestemming, bron-URL) — geen persoonsgegevens, geen prijs-scraping tenzij toegestaan. |

**Nog te checken:** busvandaag.nl / TouringcarNieuws, Bus & Touring (vakblad),
Reisrevue / Travelpro (reisbranche NL), Skift (internationale reisbranche, heeft RSS).

---

## C. Vraag- / marktsignalen (indicatoren, geen nieuws)

| Bron | Type | Status | Opmerking |
|------|------|--------|-----------|
| **Google Trends** | Zoekinteresse voor bv. "busreis Tomorrowland", "festival busreis" | API-achtig | Geen officiële API; `pytrends` (inofficieel) of handmatige export. Nuttig als trendindicator, niet als harde data. |
| **Ticketing/festival-aankondigingen via IQ Magazine** | zie sectie A | ✅ | Sectorbrede signalen over vraag en uitverkoop. |

---

## Praktische observaties uit de eerste check

- Meerdere WordPress-sites (Follow the Beat, Festileaks) blokkeren geautomatiseerde
  requests met een generieke bot-User-Agent (HTTP 403 via Cloudflare). Voor de
  uiteindelijke scraper/feed-reader een nette, herkenbare User-Agent instellen
  (`InternalDashboardTest/0.1` — geen bedrijfsnaam tijdens de testfase) en rate limiten.
- Festivalinfo biedt de rijkste set kant-en-klare feeds en is meteen bruikbaar.
- Voor busreizen is `mobiliteit.nl/tag/touringcar/feed/` de beste directe bron, maar wel dun
  (bij de eerste testrun 3 items binnen de bewaartermijn van 180 dagen). Extra busbron nodig.
- Feeds van Mobiliteit en Transport-online leveren de samenvatting als HTML; de feed-reader
  stript HTML-tags voordat er wordt opgeslagen.

## Voorgestelde volgende stappen

1. Jij bevestigt welke bronnen in scope zijn voor de eerste versie.
2. Van de ⚠️-bronnen de feeds testen met een echte User-Agent.
3. Voor ❌-bronnen die we willen: ik check robots.txt en vraag jou per site om goedkeuring.
4. Datamodel voor één "item" vastleggen (titel, datum, samenvatting, bron, bron-URL, categorie).

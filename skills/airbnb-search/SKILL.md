---
name: airbnb-search
description: Search Airbnb listings by location, check-in/check-out dates, price range, bedrooms/beds/bathrooms, guest capacity, and host attributes via the Staying API. Includes superhost, instant-book, and luxury presets. Use when a user wants to find or compare Airbnb stays in a place (e.g. "2-bed superhost places in Austin under $250") rather than look up one known listing.
---

# airbnb-search

Find Airbnb listings by location and structured filters, returning a typed
`Stay[]` envelope. Backed by the [Staying API](https://stayingapi.com).

## When to use

- A user wants to **discover** stays: "places in Lisbon for 4 guests in March
  under €200," "superhost cabins near Asheville," "instant-book lofts in CDMX."
- You need to **compare** several listings in an area by price, size, capacity,
  or host quality.
- For a single **known** listing (id / URL / address), use **airbnb-stay** instead.

## Setup

```bash
export STAYINGAPI_KEY="sk_..."   # free key (100 credits, no card): https://stayingapi.com/app/keys
```

## Endpoints it calls

| Need | Endpoint |
|---|---|
| Search by location + filters | `POST /v1/search` |
| Search, then fetch full detail per result (async) | `POST /v1/search/with-details` |
| Superhost-only preset | `POST /v1/listings/superhost` |
| Instant-book preset | `POST /v1/listings/instant-book` |
| Luxury-tier preset | `POST /v1/listings/luxury` |

### Request body (`SearchFilters`)

All fields optional unless you want results. Verified against the live OpenAPI spec:

| Field | Type | Notes |
|---|---|---|
| `locationQueries` | `string[]` | e.g. `["Austin, TX"]` |
| `searchUrls` | `string[]` | Airbnb search-results URLs to replay |
| `checkIn` / `checkOut` | `string` | `YYYY-MM-DD` |
| `priceMin` / `priceMax` | `number` | per-night |
| `minBeds` / `minBedrooms` / `minBathrooms` | `integer` | |
| `adults` / `children` / `infants` / `pets` | `integer` | guest mix |
| `currency` / `locale` | `string` | e.g. `USD`, `en` |
| `maxItems` | `integer` | default `50`, **max `240`** — caps credit spend |
| `fields` | `string` | sparse fieldset |
| `cursor` | `string` | pagination |

> ⚠️ The field is `locationQueries` (an array), **not** `location`. `maxItems`
> tops out at **240**.

## Equivalent MCP tool

On `https://api.stayingapi.com/mcp`:

- `search_stays` — search by location, dates, and filters.

## Examples

**Python (this skill):**

```bash
# 10 results in Austin under $250 with at least 2 bedrooms
python airbnb_search.py "Austin, TX" 10 priceMax=250 minBedrooms=2

# Superhost preset
python airbnb_search.py "Asheville, NC" 15 --preset superhost

# Dated search for 4 guests
python airbnb_search.py "Lisbon" 20 checkIn=2026-03-10 checkOut=2026-03-14 adults=4
```

**curl:**

```bash
curl -s https://api.stayingapi.com/v1/search \
  -H "Authorization: Bearer $STAYINGAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"locationQueries":["Austin, TX"],"maxItems":10,"priceMax":250,"minBedrooms":2}'
```

## Notes

- **Search costs 1 credit per result returned.** Cap spend with `maxItems`
  (max 240).
- **You're only charged on success (2xx).** `4xx`/`5xx` responses are free.
- `POST /v1/search/with-details` is **always async** — it returns a job id;
  poll it with the **airbnb-full** skill (`poll <job-id>`).
- Credits don't expire and roll forward.

---

> Staying API is independent and not affiliated with, endorsed by, or sponsored
> by Airbnb, Inc. Airbnb is a trademark of Airbnb, Inc.

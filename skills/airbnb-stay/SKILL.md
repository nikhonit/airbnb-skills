---
name: airbnb-stay
description: Look up a single Airbnb listing's full data — photos, reviews, host, amenities, availability, pricing, location, and star rating — by listing id, airbnb.com/rooms URL, or street address via the Staying API. Use when a user pastes an Airbnb link or id, or names a specific property, and wants its details, price, reviews, or availability.
---

# airbnb-stay

Resolve one Airbnb listing to a clean, typed `Stay` object — then slice into any
sub-resource you need. Backed by the [Staying API](https://stayingapi.com)
(REST + MCP), not a fragile HTML scraper.

## When to use

- A user pastes an `airbnb.com/rooms/...` link and asks "what is this place / how
  much / is it any good / when is it free?"
- You have a listing **id** or a **street address** and need structured data.
- You need a specific facet: **reviews**, **rating** breakdown, **pricing**,
  12-month **availability**, **host** profile, **amenities**, **photos**, or
  **location** coordinates.

## Setup

```bash
export STAYINGAPI_KEY="sk_..."   # free key (100 credits, no card): https://stayingapi.com/app/keys
```

The script reads `STAYINGAPI_KEY` and calls `https://api.stayingapi.com`.

## Endpoints it calls

| Need | Endpoint |
|---|---|
| Full listing by id | `GET /v1/stays/{id}` |
| Full listing by URL | `GET /v1/stays/by-url?url=...` |
| Full listing by address | `GET /v1/stays/by-address?address=...` (3-credit weight) |
| Photos | `GET /v1/stays/{id}/photos` |
| Reviews + rating breakdown | `GET /v1/stays/{id}/reviews` |
| Host profile | `GET /v1/stays/{id}/host` |
| Amenities (grouped) | `GET /v1/stays/{id}/amenities` |
| Availability calendar | `GET /v1/stays/{id}/availability` |
| Pricing block | `GET /v1/stays/{id}/pricing` |
| Location / coordinates | `GET /v1/stays/{id}/location` |
| Star rating summary | `GET /v1/stays/{id}/rating` |

Every endpoint accepts an optional `?fields=` sparse-fieldset to trim the payload.

## Equivalent MCP tools

If your agent speaks MCP, skip the script and call the tools directly on
`https://api.stayingapi.com/mcp`:

- `lookup_stay_by_id` — full Stay by listing id
- `lookup_stay_by_url` — full Stay from an `airbnb.com/rooms` URL
- `get_stay_photos` — a listing's photos
- `get_stay_reviews` — a listing's reviews + rating breakdown

(Host, amenities, availability, pricing, location, and rating are REST
sub-resources — use the script or a direct `GET` for those.)

## Examples

**Python (this skill):**

```bash
# Full listing from a URL
python airbnb_stay.py https://www.airbnb.com/rooms/12345678

# Full listing from an id
python airbnb_stay.py 12345678

# Just the reviews (works from id, URL, or address)
python airbnb_stay.py 12345678 reviews
python airbnb_stay.py https://www.airbnb.com/rooms/12345678 pricing
```

**curl:**

```bash
curl -s https://api.stayingapi.com/v1/stays/12345678 \
  -H "Authorization: Bearer $STAYINGAPI_KEY"

curl -s "https://api.stayingapi.com/v1/stays/by-url?url=https://www.airbnb.com/rooms/12345678" \
  -H "Authorization: Bearer $STAYINGAPI_KEY"
```

## Notes

- **1 credit per successful call** (lookups and sub-resources). The
  `by-address` resolver weighs **3 credits**.
- **You're only charged on success (2xx).** `4xx`/`5xx` responses are free.
- Credits don't expire and roll forward.
- One canonical `Stay` shape across every endpoint — your code doesn't break when
  Airbnb redesigns their site.

---

> Staying API is independent and not affiliated with, endorsed by, or sponsored
> by Airbnb, Inc. Airbnb is a trademark of Airbnb, Inc.

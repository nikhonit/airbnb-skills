---
name: airbnb-full
description: Complete Airbnb data toolkit via the Staying API — single-listing lookup and sub-resources, location search with presets, async batch resolution of up to 500 listings, job polling and paginated results, HMAC-signed webhook management, and account/credit/usage reads. Plus all five MCP tools. Use for bulk Airbnb jobs, webhook-driven pipelines, checking credit balance, or when one skill should cover lookup + search + batch end to end.
---

# airbnb-full

Everything in **airbnb-stay** and **airbnb-search**, plus async batch jobs,
webhooks, and account/usage. One script, one `_request()` helper, pure stdlib.
Backed by the [Staying API](https://stayingapi.com).

## When to use

- **Bulk** work: resolve hundreds of listings in one async batch job.
- **Pipelines**: register a webhook and get notified when a job completes.
- **Ops**: check your **credit balance**, plan, and recent **usage**.
- You want a single skill that covers lookup + search + batch + jobs + webhooks.

## Setup

```bash
export STAYINGAPI_KEY="sk_..."   # free key (100 credits, no card): https://stayingapi.com/app/keys
```

## Commands

```bash
python airbnb_full.py stay   <id | url | "address"> [sub-resource]
python airbnb_full.py search "<location>" [maxItems] [field=value ...] [--preset NAME]
python airbnb_full.py batch  <id|url|address> [<id|url|address> ...]
python airbnb_full.py jobs   [status=...] [type=...] [limit=50]
python airbnb_full.py job    <job-id>
python airbnb_full.py results <job-id> [limit=50] [offset=0] [format=json]
python airbnb_full.py poll   <job-id>            # poll until done, then print results
python airbnb_full.py webhooks
python airbnb_full.py webhook-create <https-url> <event,event,...>
python airbnb_full.py webhook <id>
python airbnb_full.py webhook-delete <id>
python airbnb_full.py deliveries <id>
python airbnb_full.py me
python airbnb_full.py usage [limit=50]
```

## Endpoints it calls

**Lookup & search** — same surface as airbnb-stay / airbnb-search
(`/v1/stays/{id}`, `/v1/stays/by-url`, `/v1/stays/by-address`, the eight
sub-resources, `/v1/search`, `/v1/search/with-details`, and the
superhost / instant-book / luxury presets).

**Batch & jobs:**

| Need | Endpoint |
|---|---|
| Batch-resolve up to 500 stays (async) | `POST /v1/stays/batch` |
| List async jobs | `GET /v1/jobs` |
| Get one job's status | `GET /v1/jobs/{id}` |
| Read paginated job results | `GET /v1/jobs/{id}/results` |

A batch entry is exactly one of `id`, `url`, or `address` (`address` weighs
3 credits). Pass an optional `webhook_id` to be notified on completion.

**Webhooks:**

| Need | Endpoint |
|---|---|
| Create subscription | `POST /v1/webhooks` |
| List subscriptions | `GET /v1/webhooks` |
| Get one | `GET /v1/webhooks/{id}` |
| Revoke | `DELETE /v1/webhooks/{id}` |
| Delivery attempts | `GET /v1/webhooks/{id}/deliveries` |

Event types: `job.queued`, `job.running`, `job.succeeded`, `job.failed`,
`stay.cached`. Deliveries are HMAC-signed.

**Account:**

| Need | Endpoint |
|---|---|
| Account, plan, credit balance | `GET /v1/me` |
| Recent metered calls | `GET /v1/usage` |

## Equivalent MCP tools

All five tools on `https://api.stayingapi.com/mcp`:

- `lookup_stay_by_id`
- `lookup_stay_by_url`
- `search_stays`
- `get_stay_photos`
- `get_stay_reviews`

(Batch, jobs, webhooks, and account are REST-only — use the script for those.)

## Examples

```bash
# Batch-resolve a mix of ids and URLs (async → returns a job id)
python airbnb_full.py batch 12345678 https://www.airbnb.com/rooms/987654 "1 Infinite Loop, Cupertino, CA"

# Poll a job to completion and print its results
python airbnb_full.py poll job_abc123

# Register a webhook for job completion
python airbnb_full.py webhook-create https://example.com/hooks/staying job.succeeded,job.failed

# Check your credit balance and recent usage
python airbnb_full.py me
python airbnb_full.py usage limit=20
```

**Batch via curl:**

```bash
curl -s https://api.stayingapi.com/v1/stays/batch \
  -H "Authorization: Bearer $STAYINGAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entries":[{"id":"12345678"},{"url":"https://www.airbnb.com/rooms/987654"}]}'
```

## Notes

- **Charged only on success (2xx).** `4xx`/`5xx` responses are free. Credits
  don't expire and roll forward.
- Lookups/sub-resources: 1 credit each (`by-address`: 3). Search: 1 credit per
  result. Batch: per resolved entry.
- `search/with-details` and `batch` are **async** — they return a job id; use
  `poll` (or a webhook) to collect results.

---

> Staying API is independent and not affiliated with, endorsed by, or sponsored
> by Airbnb, Inc. Airbnb is a trademark of Airbnb, Inc.

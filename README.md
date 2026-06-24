# airbnb-skills

**Airbnb stay data that doesn't break — typed REST + MCP, with reviews, pricing
& availability. Free tier, no card.**

Drop-in [agent skills](https://stayingapi.com) for looking up and searching
Airbnb listings from Claude, Cursor, ChatGPT, or any script. Pure Python
standard library — no `pip install`, no dependencies, no server to run. Backed by
the [Staying API](https://stayingapi.com): one stable, versioned `Stay` contract
instead of HTML scraping that breaks on the next redesign.

[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-blue.svg)](LICENSE)
![Python stdlib — no deps](https://img.shields.io/badge/Python-stdlib%2C%20no%20deps-3776AB)
![100 free credits, no card](https://img.shields.io/badge/free%20tier-100%20credits%2C%20no%20card-brightgreen)

> **Grab a free key — 100 credits, no card required:**
> **https://stayingapi.com/app/keys**

## Quickstart (under 2 minutes)

```bash
export STAYINGAPI_KEY="sk_..."   # free key: https://stayingapi.com/app/keys
python skills/airbnb-stay/airbnb_stay.py https://www.airbnb.com/rooms/12345678
```

That prints the full, typed `Stay` JSON for the listing. No build step — the
scripts use only `urllib`/`json` from the standard library.

```bash
# Search instead of look up
python skills/airbnb-search/airbnb_search.py "Austin, TX" 10 priceMax=250 minBedrooms=2

# Check your credit balance
python skills/airbnb-full/airbnb_full.py me
```

## Skills

| Skill | What it does | Cost | Docs |
|---|---|---|---|
| **airbnb-stay** | One listing by id, URL, or address → full `Stay` plus photos, reviews, host, amenities, availability, pricing, location, rating. | 1 credit/call (`by-address`: 3) | [SKILL.md](skills/airbnb-stay/SKILL.md) |
| **airbnb-search** | Search by location, dates, price, capacity, and host attributes (superhost / instant-book / luxury presets). | 1 credit per result | [SKILL.md](skills/airbnb-search/SKILL.md) |
| **airbnb-full** | Everything: lookup + search + async batch jobs + job polling + webhooks + account/usage. Plus all five MCP tools. | per call/result | [SKILL.md](skills/airbnb-full/SKILL.md) |

You're only charged on a successful (`2xx`) response — `4xx`/`5xx` are free.
Credits don't expire and roll forward.

## Use with your agent

### Claude Desktop / Claude Code (MCP)

The Staying API ships a live MCP server, so most agents don't even need the
scripts. Add this to your Claude Desktop config (or `claude mcp add`):

```json
{
  "mcpServers": {
    "stayingapi": {
      "type": "streamable-http",
      "url": "https://api.stayingapi.com/mcp",
      "headers": { "Authorization": "Bearer sk_YOUR_KEY" }
    }
  }
}
```

Five tools become available: `lookup_stay_by_id`, `lookup_stay_by_url`,
`search_stays`, `get_stay_photos`, `get_stay_reviews`.

### Cursor / `mcp` CLI

Point any streamable-HTTP MCP client at the same endpoint:

```bash
mcp add stayingapi --url https://api.stayingapi.com/mcp \
  --header "Authorization: Bearer sk_YOUR_KEY"
```

Auth is a Bearer key (`sk_...`) or OAuth 2.1 PKCE (scope `mcp:access`). The
server card lives at
[`/.well-known/mcp/server-card.json`](https://stayingapi.com/.well-known/mcp/server-card.json).

### Generic agent / OpenAI Agents SDK / load the SKILL.md

No MCP? Hand the agent a `SKILL.md` (each lists when to use it, the exact
endpoints, the MCP-tool equivalents, and copy-paste examples) and let it shell
out to the matching script, or call the REST API directly:

```bash
curl -s "https://api.stayingapi.com/v1/stays/by-url?url=https://www.airbnb.com/rooms/12345678" \
  -H "Authorization: Bearer $STAYINGAPI_KEY"
```

The scripts are plain stdlib Python, so they run anywhere an agent can run a
shell — Claude Code, the OpenAI Agents SDK, LangChain tools, a cron job, whatever.

## Why Staying API (vs. a no-key scraper)

- **A stable, versioned, typed `Stay` contract.** One canonical shape across every
  endpoint. Your integration doesn't break when Airbnb reworks their HTML.
- **First-class facets.** Reviews + rating breakdown, 12-month availability,
  pricing, and host data are real endpoints — not best-effort scrapes.
- **REST *and* MCP.** Use plain HTTP or the live MCP server, plus OAuth, async
  batch jobs, and HMAC-signed webhooks for pipelines.
- **Reliability.** A metered, authenticated backend means your agent won't
  randomly get blocked mid-run.

## Pricing

| Plan | Price | Credits | Rate limit |
|---|---|---|---|
| Free | $0 | 100 (one-time) | 20 req/min |
| Monthly | $5/mo | 400 / month | 200 req/min |
| Annual | $54/yr (~$4.50/mo) | 5,000 / year | 300 req/min |
| Enterprise | Custom | Custom | 1,500 req/min |

Full details: [stayingapi.com/pricing](https://stayingapi.com/pricing).

## Links

- **Get a key (free):** https://stayingapi.com/app/keys
- **Homepage:** https://stayingapi.com
- **Quickstart:** https://stayingapi.com/quickstart/
- **OpenAPI 3.1 spec:** https://stayingapi.com/openapi.json
- **MCP server card:** https://stayingapi.com/.well-known/mcp/server-card.json
- **For AI agents:** https://stayingapi.com/ai-agents/
- **llms.txt:** https://stayingapi.com/llms.txt · [llms-full.txt](https://stayingapi.com/llms-full.txt)
- **Support:** support@stayingapi.com

## License

[MIT-0](LICENSE) (MIT No Attribution) — use it however you like, no attribution
required.

---

> Staying API is independent and not affiliated with, endorsed by, or sponsored
> by Airbnb, Inc. Airbnb is a trademark of Airbnb, Inc.

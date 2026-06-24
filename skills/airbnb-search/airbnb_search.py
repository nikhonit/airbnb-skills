#!/usr/bin/env python3
"""airbnb-search — search Airbnb listings via the Staying API.

Pure Python standard library. No dependencies.
Get a free key (100 credits, no card): https://stayingapi.com/app/keys
Then: export STAYINGAPI_KEY="sk_..."

Usage:
  python airbnb_search.py "<location>" [maxItems] [field=value ...] [--preset NAME]

Presets (NAME): search (default) | superhost | instant-book | luxury | with-details
Filter fields: priceMin priceMax minBeds minBedrooms minBathrooms
               adults children infants pets checkIn checkOut currency locale
Example:
  python airbnb_search.py "Austin, TX" 10 priceMax=250 minBedrooms=2 --preset superhost
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("STAYINGAPI_BASE", "https://api.stayingapi.com")
KEY = os.environ.get("STAYINGAPI_KEY")

# Search costs 1 credit per result returned. Cap spend with maxItems (max 240).
PRESETS = {
    "search":       "/v1/search",
    "with-details": "/v1/search/with-details",  # always async — returns a job
    "superhost":    "/v1/listings/superhost",
    "instant-book": "/v1/listings/instant-book",
    "luxury":       "/v1/listings/luxury",
}
INT_FIELDS = {"minBeds", "minBedrooms", "minBathrooms",
              "adults", "children", "infants", "pets", "maxItems"}
NUM_FIELDS = {"priceMin", "priceMax"}


def _request(method, path, params=None, body=None):
    if not KEY:
        sys.exit("Set STAYINGAPI_KEY — free key: https://stayingapi.com/app/keys")
    url = f"{BASE}{path}"
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "airbnb-skills/1.0 (+https://stayingapi.com)",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {"status": r.status}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')}")


def search(filters, preset="search"):
    """POST a SearchFilters body to a search endpoint. `filters` is a dict, e.g.
    {"locationQueries": ["Austin, TX"], "maxItems": 10, "priceMax": 250}."""
    if preset not in PRESETS:
        sys.exit(f"unknown preset '{preset}' — pick one of: {', '.join(PRESETS)}")
    return _request("POST", PRESETS[preset], body=filters)


def superhost(filters):         return search(filters, "superhost")
def instant_book(filters):      return search(filters, "instant-book")
def luxury(filters):            return search(filters, "luxury")
def search_with_details(filters): return search(filters, "with-details")


def _parse_cli(argv):
    preset, positional, filters = "search", [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--preset":
            preset = argv[i + 1]
            i += 2
            continue
        if "=" in a:
            k, v = a.split("=", 1)
            if k in INT_FIELDS:
                v = int(v)
            elif k in NUM_FIELDS:
                v = float(v)
            filters[k] = v
        else:
            positional.append(a)
        i += 1
    if positional:
        filters.setdefault("locationQueries", [positional[0]])
        if len(positional) > 1:
            filters["maxItems"] = int(positional[1])
    return filters, preset


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv:
        sys.exit(
            'usage: airbnb_search.py "<location>" [maxItems] [field=value ...] '
            "[--preset search|superhost|instant-book|luxury|with-details]"
        )
    filters, preset = _parse_cli(argv)
    if "locationQueries" not in filters and "searchUrls" not in filters:
        sys.exit("provide a location (or set searchUrls=... via the Python API)")
    result = search(filters, preset)
    json.dump(result, sys.stdout, indent=2)
    print()

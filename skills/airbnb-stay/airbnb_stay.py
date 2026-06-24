#!/usr/bin/env python3
"""airbnb-stay — look up a single Airbnb listing via the Staying API.

Pure Python standard library. No dependencies.
Get a free key (100 credits, no card): https://stayingapi.com/app/keys
Then: export STAYINGAPI_KEY="sk_..."

Usage:
  python airbnb_stay.py <id | airbnb.com/rooms URL | "street address">
  python airbnb_stay.py <id | url | address> <sub-resource>

Sub-resources: photos reviews host amenities availability pricing location rating
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("STAYINGAPI_BASE", "https://api.stayingapi.com")
KEY = os.environ.get("STAYINGAPI_KEY")

SUBRESOURCES = (
    "photos", "reviews", "host", "amenities",
    "availability", "pricing", "location", "rating",
)


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
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {"status": r.status}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')}")


def lookup_by_id(stay_id, fields=None):
    return _request("GET", f"/v1/stays/{stay_id}", params={"fields": fields})


def lookup_by_url(listing_url, fields=None):
    return _request("GET", "/v1/stays/by-url", params={"url": listing_url, "fields": fields})


def lookup_by_address(address, fields=None):
    # by-address is weighted at 3 credits per successful call.
    return _request("GET", "/v1/stays/by-address", params={"address": address, "fields": fields})


def sub_resource(stay_id, name, fields=None):
    return _request("GET", f"/v1/stays/{stay_id}/{name}", params={"fields": fields})


# Thin wrappers for each sub-resource of /v1/stays/{id}.
def photos(stay_id):       return sub_resource(stay_id, "photos")
def reviews(stay_id):      return sub_resource(stay_id, "reviews")
def host(stay_id):         return sub_resource(stay_id, "host")
def amenities(stay_id):    return sub_resource(stay_id, "amenities")
def availability(stay_id): return sub_resource(stay_id, "availability")
def pricing(stay_id):      return sub_resource(stay_id, "pricing")
def location(stay_id):     return sub_resource(stay_id, "location")
def rating(stay_id):       return sub_resource(stay_id, "rating")


def _resolve_id(target):
    """Return a stay id from an id, an airbnb.com/rooms URL, or a street address."""
    if target.startswith("http"):
        return str(lookup_by_url(target).get("id", target))
    if target.isdigit():
        return target
    return str(lookup_by_address(target).get("id", target))


if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv:
        sys.exit(
            'usage: airbnb_stay.py <id | airbnb.com/rooms URL | "street address"> '
            "[" + "|".join(SUBRESOURCES) + "]"
        )
    target = argv[0]
    if len(argv) > 1:
        name = argv[1]
        if name not in SUBRESOURCES:
            sys.exit(f"unknown sub-resource '{name}' — pick one of: {', '.join(SUBRESOURCES)}")
        result = sub_resource(_resolve_id(target), name)
    elif target.startswith("http"):
        result = lookup_by_url(target)
    elif target.isdigit():
        result = lookup_by_id(target)
    else:
        result = lookup_by_address(target)
    json.dump(result, sys.stdout, indent=2)
    print()

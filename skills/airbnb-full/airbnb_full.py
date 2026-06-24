#!/usr/bin/env python3
"""airbnb-full — complete Airbnb data toolkit for the Staying API.

Pure Python standard library. No dependencies.
Get a free key (100 credits, no card): https://stayingapi.com/app/keys
Then: export STAYINGAPI_KEY="sk_..."

Covers: single lookup + sub-resources, search + presets, async batch jobs,
job polling, paginated results, webhook management, and account/usage.

Usage:
  python airbnb_full.py stay   <id | url | "address"> [sub-resource]
  python airbnb_full.py search "<location>" [maxItems] [field=value ...] [--preset NAME]
  python airbnb_full.py batch  <id|url|address> [<id|url|address> ...]
  python airbnb_full.py jobs   [status=...] [type=...] [limit=50]
  python airbnb_full.py job    <job-id>
  python airbnb_full.py results <job-id> [limit=50] [offset=0] [format=json]
  python airbnb_full.py poll   <job-id>            # poll until done, then print results
  python airbnb_full.py webhooks                   # list subscriptions
  python airbnb_full.py webhook-create <https-url> <event,event,...>
  python airbnb_full.py webhook       <webhook-id>
  python airbnb_full.py webhook-delete <webhook-id>
  python airbnb_full.py deliveries    <webhook-id>
  python airbnb_full.py me
  python airbnb_full.py usage [limit=50]

Equivalent MCP tools (server: https://api.stayingapi.com/mcp):
  lookup_stay_by_id, lookup_stay_by_url, search_stays,
  get_stay_photos, get_stay_reviews
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("STAYINGAPI_BASE", "https://api.stayingapi.com")
KEY = os.environ.get("STAYINGAPI_KEY")

SUBRESOURCES = (
    "photos", "reviews", "host", "amenities",
    "availability", "pricing", "location", "rating",
)
SEARCH_PRESETS = {
    "search":       "/v1/search",
    "with-details": "/v1/search/with-details",
    "superhost":    "/v1/listings/superhost",
    "instant-book": "/v1/listings/instant-book",
    "luxury":       "/v1/listings/luxury",
}
WEBHOOK_EVENTS = ("job.queued", "job.running", "job.succeeded", "job.failed", "stay.cached")
TERMINAL_STATES = {"succeeded", "failed", "timed_out", "aborted"}
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


# --- single listing -------------------------------------------------------
def lookup_by_id(stay_id, fields=None):
    return _request("GET", f"/v1/stays/{stay_id}", params={"fields": fields})


def lookup_by_url(listing_url, fields=None):
    return _request("GET", "/v1/stays/by-url", params={"url": listing_url, "fields": fields})


def lookup_by_address(address, fields=None):
    return _request("GET", "/v1/stays/by-address", params={"address": address, "fields": fields})


def sub_resource(stay_id, name, fields=None):
    return _request("GET", f"/v1/stays/{stay_id}/{name}", params={"fields": fields})


def _resolve_id(target):
    if target.startswith("http"):
        return str(lookup_by_url(target).get("id", target))
    if target.isdigit():
        return target
    return str(lookup_by_address(target).get("id", target))


# --- search ---------------------------------------------------------------
def search(filters, preset="search"):
    if preset not in SEARCH_PRESETS:
        sys.exit(f"unknown preset '{preset}' — pick one of: {', '.join(SEARCH_PRESETS)}")
    return _request("POST", SEARCH_PRESETS[preset], body=filters)


# --- batch + jobs ---------------------------------------------------------
def batch(targets, webhook_id=None):
    """Resolve up to 500 stays asynchronously. Each target may be an id, an
    airbnb.com/rooms URL, or a street address (address entries weigh 3 credits)."""
    entries = []
    for t in targets:
        if t.startswith("http"):
            entries.append({"url": t})
        elif t.isdigit():
            entries.append({"id": t})
        else:
            entries.append({"address": t})
    body = {"entries": entries}
    if webhook_id:
        body["webhook_id"] = webhook_id
    return _request("POST", "/v1/stays/batch", body=body)


def list_jobs(**filters):
    return _request("GET", "/v1/jobs", params=filters or None)


def get_job(job_id):
    return _request("GET", f"/v1/jobs/{job_id}")


def job_results(job_id, limit=50, offset=0, fmt="json"):
    return _request("GET", f"/v1/jobs/{job_id}/results",
                    params={"limit": limit, "offset": offset, "format": fmt})


def poll_job(job_id, interval=2.0, timeout=300):
    """Poll a job until it reaches a terminal state (or timeout). Returns the job."""
    waited = 0.0
    while True:
        job = get_job(job_id)
        if job.get("status") in TERMINAL_STATES or waited >= timeout:
            return job
        time.sleep(interval)
        waited += interval


# --- webhooks -------------------------------------------------------------
def create_webhook(url, events, description=None):
    body = {"url": url, "events": events}
    if description:
        body["description"] = description
    return _request("POST", "/v1/webhooks", body=body)


def list_webhooks():            return _request("GET", "/v1/webhooks")
def get_webhook(wid):           return _request("GET", f"/v1/webhooks/{wid}")
def delete_webhook(wid):        return _request("DELETE", f"/v1/webhooks/{wid}")
def webhook_deliveries(wid):    return _request("GET", f"/v1/webhooks/{wid}/deliveries")


# --- account --------------------------------------------------------------
def me():                       return _request("GET", "/v1/me")
def usage(limit=50):            return _request("GET", "/v1/usage", params={"limit": limit})


# --- CLI ------------------------------------------------------------------
def _kv(args):
    """Split ['k=v', 'plain'] into ({k: v}, ['plain'])."""
    kw, pos = {}, []
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            kw[k] = v
        else:
            pos.append(a)
    return kw, pos


def _cmd_stay(args):
    if not args:
        sys.exit("usage: airbnb_full.py stay <id | url | address> [sub-resource]")
    target, sub = args[0], (args[1] if len(args) > 1 else None)
    if sub:
        if sub not in SUBRESOURCES:
            sys.exit(f"unknown sub-resource '{sub}' — pick one of: {', '.join(SUBRESOURCES)}")
        return sub_resource(_resolve_id(target), sub)
    if target.startswith("http"):
        return lookup_by_url(target)
    if target.isdigit():
        return lookup_by_id(target)
    return lookup_by_address(target)


def _cmd_search(args):
    preset = "search"
    if "--preset" in args:
        i = args.index("--preset")
        preset = args[i + 1]
        args = args[:i] + args[i + 2:]
    kw, pos = _kv(args)
    filters = {}
    for k, v in kw.items():
        filters[k] = int(v) if k in INT_FIELDS else float(v) if k in NUM_FIELDS else v
    if pos:
        filters.setdefault("locationQueries", [pos[0]])
        if len(pos) > 1:
            filters["maxItems"] = int(pos[1])
    if "locationQueries" not in filters and "searchUrls" not in filters:
        sys.exit("provide a location, e.g. airbnb_full.py search \"Austin, TX\" 10")
    return search(filters, preset)


def _cmd_jobs(args):
    kw, _ = _kv(args)
    if "limit" in kw:
        kw["limit"] = int(kw["limit"])
    return list_jobs(**kw)


def _cmd_results(args):
    if not args:
        sys.exit("usage: airbnb_full.py results <job-id> [limit=50] [offset=0] [format=json]")
    kw, pos = _kv(args)
    return job_results(pos[0], limit=int(kw.get("limit", 50)),
                       offset=int(kw.get("offset", 0)), fmt=kw.get("format", "json"))


def _cmd_poll(args):
    if not args:
        sys.exit("usage: airbnb_full.py poll <job-id>")
    job = poll_job(args[0])
    if job.get("status") == "succeeded":
        return job_results(args[0])
    return job


def _cmd_webhook_create(args):
    if len(args) < 2:
        sys.exit("usage: airbnb_full.py webhook-create <https-url> <event,event,...>\n"
                 "       events: " + ", ".join(WEBHOOK_EVENTS))
    events = args[1].split(",")
    bad = [e for e in events if e not in WEBHOOK_EVENTS]
    if bad:
        sys.exit(f"unknown event(s) {bad} — valid: {', '.join(WEBHOOK_EVENTS)}")
    return create_webhook(args[0], events)


def _need(args, what):
    if not args:
        sys.exit(f"usage: airbnb_full.py {what} <id>")
    return args[0]


COMMANDS = {
    "stay":           _cmd_stay,
    "search":         _cmd_search,
    "batch":          lambda a: batch(a),
    "jobs":           _cmd_jobs,
    "job":            lambda a: get_job(_need(a, "job")),
    "results":        _cmd_results,
    "poll":           _cmd_poll,
    "webhooks":       lambda a: list_webhooks(),
    "webhook-create": _cmd_webhook_create,
    "webhook":        lambda a: get_webhook(_need(a, "webhook")),
    "webhook-delete": lambda a: delete_webhook(_need(a, "webhook-delete")),
    "deliveries":     lambda a: webhook_deliveries(_need(a, "deliveries")),
    "me":             lambda a: me(),
    "usage":          lambda a: usage(int(_kv(a)[0].get("limit", 50))),
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit("usage: airbnb_full.py <command> [args]\ncommands: " + ", ".join(COMMANDS))
    result = COMMANDS[sys.argv[1]](sys.argv[2:])
    json.dump(result, sys.stdout, indent=2)
    print()

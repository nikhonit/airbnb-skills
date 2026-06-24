# Security Policy

## Reporting a vulnerability

If you find a security issue in these skills or in the Staying API, email
**[support@stayingapi.com](mailto:support@stayingapi.com)**. Please include steps
to reproduce and the impact. We'll acknowledge and work a fix; please give us a
reasonable window before public disclosure.

## Handling your API key

- Your key (`sk_...`) is a bearer credential. Anyone holding it can spend your
  credits.
- **Never commit a real key.** The scripts read it from the `STAYINGAPI_KEY`
  environment variable for exactly this reason — keep it out of source, logs,
  screenshots, and issue reports.
- `.env` is git-ignored in this repo. Keep it that way.
- Rotate a leaked key immediately from the dashboard:
  [https://stayingapi.com/app/keys](https://stayingapi.com/app/keys).

## Scope

This repo contains no server and no scrapers — it is a stdlib HTTP client for a
metered REST + MCP API. The most sensitive thing here is your key. Treat it like
a password.

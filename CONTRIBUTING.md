# Contributing

Thanks for helping improve `airbnb-skills`. This repo is a thin, dependency-free
client for the [Staying API](https://stayingapi.com). Keep changes small, honest,
and runnable.

## Ground rules

- **Standard library only.** Scripts must run on a clean Python 3.8+ with no
  `pip install`. Use `urllib`, `json`, `os`, `sys`, `time` — no `requests`, no
  `requirements.txt`, no third-party packages.
- **Don't invent endpoints.** The source of truth is
  [`https://stayingapi.com/openapi.json`](https://stayingapi.com/openapi.json).
  If a path, query param, or request body isn't in the live spec, don't ship it.
- **Match the existing shape.** Every script reads `STAYINGAPI_KEY`, targets
  `https://api.stayingapi.com`, and routes through one `_request()` helper. New
  helpers should be thin wrappers over `_request()`.
- **No secrets.** Never commit a real `sk_` key, a `.env` file, or fixture data
  containing live credentials.

## Adding or modifying a skill

1. Each skill lives in `skills/<name>/` with a `SKILL.md` (YAML frontmatter +
   body) and one `<name>.py` script.
2. Keep the `SKILL.md` `description` keyword-rich and trigger-oriented — it's
   what an agent matches on. List the **MCP tool equivalents** so MCP-native
   agents can skip the script.
3. If you add a skill, add it to both `manifest.json` and the README skills table.

## Running a skill

```bash
export STAYINGAPI_KEY="sk_..."   # free key: https://stayingapi.com/app/keys
python skills/airbnb-stay/airbnb_stay.py https://www.airbnb.com/rooms/12345678
```

Run your change against a real key and confirm it returns JSON (or a clean error
when the key is missing) before opening a PR.

## Questions

Open an issue, or email [support@stayingapi.com](mailto:support@stayingapi.com).

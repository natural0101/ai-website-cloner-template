# Animate UI Whole-Site Audit

Checked: 2026-07-03 13:43 MSK.

Sources:

- https://animate-ui.com/
- https://animate-ui.com/docs
- https://animate-ui.com/docs/components
- https://animate-ui.com/docs/primitives
- https://animate-ui.com/docs/icons
- https://animate-ui.com/r/registry.json

## Result

Animate UI has no useful machine-readable site map right now. These paths return 404:

- `/sitemap.xml`
- `/robots.txt`
- `/llms.txt`
- `/docs/llms.txt`
- `/.well-known/llms.txt`
- `/docs.json`
- `/openapi.json`

The usable internal surface is still docs plus registry. The latest rewalk used the official GitHub tree for the complete docs inventory and GitHub raw registry for the complete registry body, because live HTML bodies and live `GET /r/registry.json` can stream very slowly or time out after partial downloads while `HEAD` checks still return 200.

Fresh user-requested whole-site rewalk on 2026-07-03 13:43 MSK: seed pages `/`, `/docs`, `/docs/components`, `/docs/primitives`, and `/docs/icons` returned 200; service maps still returned 404; the official GitHub tree still exposed 171 docs routes; 171/171 live docs routes returned 200; 171/171 docs `.mdx` endpoints returned 200; GitHub raw `apps/www/public/r/registry.json` fetched fully with 580 items; live `HEAD /r/registry.json` returned 200 while live `GET /r/registry.json` hit a bounded `AbortError`; all 580 live `/r/<item>.json` endpoints returned 200.

| Surface | Result |
| --- | ---: |
| Official GitHub tree docs routes | 171 |
| Live docs HTML routes with 200 after retry | 171/171 |
| Useful non-docs HTML pages | 1, `/` |
| Docs pages | 171 |
| Docs `.mdx` endpoints with 200 | 171/171 |
| GitHub raw registry body | 200, 417344 bytes, 580 items |
| Live registry index | `HEAD` 200, live `GET` hit bounded `AbortError`; GitHub raw body OK |
| Registry item endpoints with 200 after bounded retry | 580/580 |
| Service maps | 0 live |

## Registry Groups

| Group | Count |
| --- | ---: |
| `components-*` | 73 |
| `primitives-*` | 81 |
| `icons-*` | 260 |
| `demo-*` | 159 |
| `hooks-*` | 5 |
| `lib-*` | 1 |
| `index` | 1 |

Normal landing selection pool:

- 73 installable component entries.
- 81 installable primitive entries.
- Hooks and lib are dependency-chain helpers.
- Demos are reference only.
- Icons are exact one-off installs only.

## Bad Paths

Do not cite or install from these generated/internal 404 paths:

- `/docs/primitives/base/menuarrow`
- `/docs/primitives/base/menucheckboxitem`
- `/docs/primitives/base/menuitem`
- `/docs/primitives/base/menuradiogroup`
- `/docs/primitives/base/menuradioitem`
- `/docs/primitives/base/menushortcut`
- `/docs/primitives/base/menusubmenu`
- `/docs/primitives/base/menusubmenutrigger`
- `/react/primitives/animate/tooltip`

Use these instead:

- `/docs/components/base/menu`
- `/docs/primitives/base/menu`
- `/docs/components/animate/tooltip`
- `/docs/primitives/animate/tooltip`

## Decision

The site has already been reduced to the useful working surface: docs pages, `.mdx` source-like pages, registry JSON, and item endpoints. Future agents should not keep looking for a sitemap or LLM map on Animate UI unless the site changes.

For catalog rebuilds, use the official GitHub tree for docs inventory and GitHub raw `apps/www/public/r/registry.json` if the live registry body stalls or resets. Before installing any item, still verify the exact live `https://animate-ui.com/r/<item>.json` endpoint.

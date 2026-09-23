# HextaUI Source Map

Дата проверки: 2026-07-03.

HextaUI is an MIT shadcn-compatible registry of foundation components and app-oriented blocks. Use it as a gated source for credible SaaS/app product proof, AI workflow panels, auth/billing/settings/team/task screens and exact foundation components that the local project does not already own.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://www.hextaui.com/ | 200 |
| Showcase | https://www.hextaui.com/showcase | 200 |
| Components index | https://www.hextaui.com/components | 200 |
| Docs root guess | https://www.hextaui.com/docs | 404 HTML |
| Sitemap index | https://www.hextaui.com/sitemap.xml | 200, points to `https://hextaui.com/sitemap-0.xml` |
| Sitemap child | https://hextaui.com/sitemap-0.xml | 200, 143 URLs |
| LLM map | https://www.hextaui.com/llms.txt | 200 |
| RSS | https://www.hextaui.com/rss.xml | 200 |
| Registry index | https://www.hextaui.com/r/registry.json | 200, 139 items |
| Bare registry index | https://hextaui.com/r/registry.json | 200 via redirect |
| Legacy registry guess | https://www.hextaui.com/registry.json | 404 HTML |
| Registry subdomain guess | https://registry.hextaui.com/r/registry.json | 404 text |
| Official shadcn registries index | https://ui.shadcn.com/r/registries.json | contains `@hextaui` mapped to `https://hextaui.com/r/{name}.json` |
| GitHub repo | https://github.com/preetsuthar17/HextaUI | 200 |
| GitHub license | https://raw.githubusercontent.com/preetsuthar17/HextaUI/master/LICENSE | MIT |
| GitHub registry | https://raw.githubusercontent.com/preetsuthar17/HextaUI/master/registry.json | 200, same 139 items |
| Components config | https://raw.githubusercontent.com/preetsuthar17/HextaUI/master/components.json | 200, registry namespace `@hextaui` |

## Site And Registry Inventory

Sitemap:

- Sitemap index is live and points to one child sitemap.
- Child sitemap lists 143 URLs.
- Home and showcase returned 200.
- `https://www.hextaui.com/components` returned 200.
- During the audit, many individual component/block HTML pages from sitemap timed out when fetched directly, even on `www`.
- Use `llms.txt`, registry JSON, exact item endpoints and GitHub as the reliable evidence path. Treat individual HTML docs pages as helpful when they load, not as the only source of truth.

Registry scan:

- 139 item names in `https://www.hextaui.com/r/registry.json`.
- 139/139 exact endpoints `https://www.hextaui.com/r/<name>.json` returned 200 JSON.
- All registry items currently report `registry:ui`.
- GitHub raw `registry.json` and `public/r/registry.json` match the public registry.
- Root `/registry.json` returned 404 and must not be used as install evidence.

Registry groups by item name:

| Group | Count | Use |
| --- | ---: | --- |
| foundation | 54 | Owned shadcn-like primitives and small app UI pieces. Use only when local shadcn/custom is not enough. |
| AI | 14 | AI chat, prompt, model, citations, usage, upload and streaming UI proof. |
| auth | 16 | Login, signup, OTP, two-factor, sessions, account lifecycle flows. |
| billing | 15 | Pricing table, plan selector, subscription card, usage billing, invoices and payment states. |
| settings | 18 | Account, profile, team, security, API keys, integrations, webhooks, domains and preferences. |
| team | 15 | Team dashboard, activity, files, chat, permissions, invitations and AI room. |
| task | 6 | Task board, list, detail, filters, create and progress. |
| project | 1 | Project list with progress/member/task proof. |

Common package dependencies:

| Dependency | Count |
| --- | ---: |
| `@radix-ui/react-slot` | 6 |
| `@radix-ui/react-dialog` | 4 |
| `next-themes` | 2 |
| `react-markdown` | 1 |
| `remark-gfm` | 1 |
| `shiki` | 1 |
| `next` | 1 |
| `recharts` | 1 |
| `react-day-picker@latest` | 1 |
| `embla-carousel-react` | 1 |
| `react-resizable-panels` | 1 |
| `vaul` | 1 |
| `sonner` | 1 |

Common registry dependencies:

- `button` on 83 items.
- `card` on 77 items.
- `separator` on 52 items.
- `badge` on 52 items.
- `input-group` on 45 items.
- `field` on 39 items.
- `select` on 26 items.
- `alert-dialog` on 17 items.
- `avatar` on 17 items.
- `dropdown-menu` on 16 items.
- `progress` on 15 items.
- `textarea` on 13 items.
- `dialog` on 12 items.
- `switch` on 12 items.

## Install Model

Official namespace from shadcn registry index:

```bash
npx shadcn@latest add @hextaui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://hextaui.com/r/<name>.json
```

Use exact item names only. Prefer the exact URL form when the target project's `components.json` does not already know the `@hextaui` namespace.

Do not bulk-install. HextaUI registry dependencies can recursively install many foundation pieces, so record the dependency impact before running the command.

## License Gate

The GitHub API reports MIT, and raw `LICENSE` on the `master` branch is MIT. Treat public registry items as usable for own/client sites, while still recording source URL, endpoint, dependencies and adaptation notes.

Do not redistribute HextaUI as a competing component library, and do not present demo app screens as real product proof without replacing copy, data, metrics, users and workflows.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| AI product proof | `ai-prompt-input`, `ai-message`, `ai-conversation`, `ai-citations`, `ai-model-selector`, `ai-streaming-response`, `ai-usage-quota`, `ai-file-upload`, `team-ai-room`, `team-prompt-library` | Use only for real AI/agent products. |
| Billing/pricing proof | `billing-pricing-table`, `billing-plan-selector`, `billing-subscription-card`, `billing-usage-billing`, `billing-usage-alerts`, `billing-invoice-list`, `billing-payment-method`, `billing-upgrade-prompt` | Useful for SaaS pricing, account and product proof. |
| Auth/onboarding proof | `auth-login-form`, `auth-signup-form`, `auth-otp-verify`, `auth-magic-link`, `auth-two-factor-setup`, `auth-session-manager` | Use in workflow sections, not as generic hero decoration. |
| Settings/admin proof | `settings-api-keys`, `settings-integrations`, `settings-webhooks`, `settings-security`, `settings-team-members`, `settings-notifications`, `settings-domains` | Good for developer tools, SaaS admin and trust sections. |
| Team/task proof | `team-dashboard`, `team-member-list`, `team-permissions-matrix`, `team-projects`, `task-board`, `task-list`, `task-detail`, `project-list` | Use for collaboration/project products with real workflow. |
| Foundation details | `button-group`, `input-group`, `empty`, `field`, `kbd`, `native-select`, `tree`, `video-player`, `sidebar` | Use only when local shadcn/custom cannot cover the specific UI state. |

## Reject Or Use Carefully

- Reject individual HTML docs pages as the sole proof when they time out; require registry endpoint and `llms.txt` or GitHub registry evidence.
- Reject root `/registry.json` and `registry.hextaui.com` guesses.
- Reject broad replacement of local shadcn primitives.
- Reject AI blocks for non-AI products.
- Reject auth/billing/settings/team/task blocks when they would create fake product surfaces.
- Reject blocks that introduce `react-markdown`, `shiki`, `recharts`, `next`, `react-day-picker`, `embla-carousel-react`, `react-resizable-panels` or `vaul` without a real product reason.
- Reject app screens whose demo data, fake users, fake invoices, fake usage metrics or fake prompts cannot be replaced with credible product evidence.
- Use mobile simplification for dense tables, boards, sidebars, permission matrices and settings panels.

## Selection Flow

1. Identify the section job and whether it needs app-product proof rather than marketing decoration.
2. Check existing/local shadcn, ReUI, MVPBlocks, SmoothUI, Kokonut UI, Tailark and shadcnblocks first.
3. Choose one exact HextaUI item or explicitly reject HextaUI for that section.
4. Verify `https://www.hextaui.com/r/<name>.json` and record the official namespace or exact URL command.
5. Record the source page from `llms.txt`, the endpoint URL, dependencies, registry dependencies, MIT license, HTML-doc caveat, adaptation, reduced-motion/mobile behavior and QA.
6. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/43-hextaui-selection.md
```

The file must record exact item, source URL from `llms.txt` or HTML page when it loads, endpoint URL, install command, MIT license/access, dependencies, registry dependencies, evidence path, visible purpose, adaptation, mobile behavior, decision, task ID, change ID, risk and QA evidence.

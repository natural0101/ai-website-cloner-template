# Blocks.so Source Map

Дата проверки: 2026-07-03.

Blocks.so is an MIT, shadcn-compatible registry of app and product UI blocks. Use it as a gated source for credible product proof surfaces: stats, login flows, onboarding, tables, dialogs, sidebars, AI chat, command menus, file upload, form layouts and grid lists. It should not be used as generic SaaS decoration or fake dashboard proof.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Official shadcn registries index | https://ui.shadcn.com/r/registries.json | contains `@blocks-so` mapped to `https://blocks.so/r/{name}.json` |
| Website | https://blocks.so/ | live site, full `GET` can reset during audit |
| Sitemap | https://blocks.so/sitemap.xml | 200, 88 URLs |
| Robots | https://blocks.so/robots.txt | 200 |
| LLM map | https://blocks.so/llms.txt | unreliable during audit, `GET` returned `ECONNRESET` |
| Live registry index | https://blocks.so/r/registry.json | `HEAD` 200, full `GET` returned `ECONNRESET` |
| Exact item endpoints | https://blocks.so/r/&lt;name&gt;.json | 76/76 unique endpoints returned 200 |
| GitHub repo | https://github.com/ephraimduncan/blocks | 200, MIT via GitHub API |
| GitHub license | https://raw.githubusercontent.com/ephraimduncan/blocks/main/LICENSE.md | MIT |
| GitHub public registry | https://raw.githubusercontent.com/ephraimduncan/blocks/main/public/r/registry.json | 200, 571745 bytes, 77 entries |
| GitHub README | https://raw.githubusercontent.com/ephraimduncan/blocks/main/README.md | documents `@blocks-so` install commands |
| GitHub components config | https://raw.githubusercontent.com/ephraimduncan/blocks/main/components.json | 200 |

## Site And Registry Inventory

Sitemap:

- 88 URLs total.
- 1 homepage.
- 11 category pages.
- 76 item pages.
- 88/88 sitemap URLs returned 200 on `HEAD`.
- Categories: `ai`, `command-menu`, `dialogs`, `file-upload`, `form-layout`, `grid-list`, `login`, `onboarding`, `sidebar`, `stats`, `tables`.

Registry scan:

- 77 registry entries total.
- 76 unique install names.
- All entries are `registry:block`.
- `file-upload-01` appears twice in `public/r/registry.json`; treat it as one installable item.
- 76/76 unique live endpoints `https://blocks.so/r/<name>.json` returned 200.
- Live `GET /r/registry.json` returned `ECONNRESET` during audit; use GitHub raw registry for catalog rebuilds, then verify exact live item endpoints before install.

Official shadcn registry:

```text
@blocks-so -> https://blocks.so/r/{name}.json
```

Install command:

```bash
npx shadcn@latest add @blocks-so/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://blocks.so/r/<name>.json
```

## License Gate

Blocks.so is MIT.

- GitHub API reports MIT.
- Raw `LICENSE.md` on `main` is MIT.
- README says the blocks are free and open source.
- README documents the official `@blocks-so` namespace and direct URL install form.

Do not redistribute Blocks.so as a competing block library. Do not leave demo metrics, fake users, fake AI chats, fake auth flows, fake file names, fake tables or fake dashboard activity as product proof.

## Registry Groups

| Category | Count | Landing use | Risk |
| --- | ---: | --- | --- |
| `stats` | 15 | Metrics, product proof, before/after cards | Fake numbers or vanity metrics. |
| `dialog` | 12 | Confirmation, upgrade, invite, destructive action flows | Modal decoration without real decision flow. |
| `login` | 9 | Auth/conversion flow proof | Generic login section on a marketing page. |
| `onboarding` | 7 | Activation, setup, progress proof | Fake setup steps or irrelevant checklist. |
| `file-upload` | 6 unique | Document/media/file product proof | Fake file names and broad upload UI where product is not file-based. |
| `sidebar` | 6 | App shell and workflow navigation proof | Full app chrome overpowering landing story. |
| `ai` | 5 | AI/chat product surface | Fake chat, fake assistant claims, trend-only AI UI. |
| `form-layout` | 5 | Signup, settings, profile or configuration proof | Long forms where a focused CTA would work better. |
| `table` | 5 | Data product proof | Dense table without readable mobile plan. |
| `command-menu` | 3 | Power-user command palette proof | Hidden complexity shown as decoration. |
| `grid-list` | 3 | Dense entity lists, team/project collections | Generic cards with fake records. |

Common runtime dependencies:

| Dependency | Count |
| --- | ---: |
| `lucide-react` | 36 |
| `@tabler/icons-react` | 18 |
| `recharts` | 4 |
| `framer-motion` | 2 |
| `ai` | 1 |
| `date-fns` | 1 |
| `react-dropzone` | 1 |
| `sonner` | 1 |
| `@tanstack/react-table` | 1 |

Common registry dependencies:

| Registry dependency | Count |
| --- | ---: |
| `button` | 54 |
| `input` | 28 |
| `card` | 28 |
| `label` | 23 |
| `select` | 13 |
| `dialog` | 13 |
| `separator` | 13 |
| `dropdown-menu` | 12 |
| `badge` | 11 |
| `avatar` | 10 |
| `textarea` | 7 |
| `checkbox` | 6 |
| `sidebar` | 6 |
| `tooltip` | 5 |
| `progress` | 5 |
| `field` | 5 |
| `collapsible` | 5 |
| `table` | 5 |
| `command` | 4 |
| `chart` | 4 |

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Product proof metrics | `stats-01` through `stats-15` | Replace all numbers with real metrics or mark as visual-only sample. |
| Auth/conversion workflow | `login-01` through `login-09` | Use only when login/signup is part of the product story. |
| Activation or setup proof | `onboarding-01` through `onboarding-07` | Make steps match real onboarding, not generic checklist copy. |
| Data workflow proof | `table-01` through `table-05` | Requires mobile table/card transformation and real rows. |
| Decision or modal flow | `dialog-01` through `dialog-12` | Use for real invite, delete, upgrade, share or confirmation flows. |
| App shell reference | `sidebar-01` through `sidebar-06` | Use as product surface reference, not as a decorative landing section. |
| AI product surface | `ai-01` through `ai-05` | Requires real prompt/response examples and AI dependency gate. |
| Command palette proof | `command-menu-01` through `command-menu-03` | Good for developer tools or power-user products. |
| File/document product proof | `file-upload-01` through `file-upload-06` | Requires real file types, upload states and error states. |
| Form-heavy workflow | `form-layout-01` through `form-layout-05` | Use for settings/profile/configuration proof, not generic lead capture. |
| Dense object list | `grid-list-01` through `grid-list-03` | Replace demo records with real entities. |

## Reject Or Use Carefully

- Reject fake dashboards, fake metrics, fake users, fake files, fake AI chats, fake tables and fake notification states.
- Reject sidebars unless the section is explicitly showing an app shell or workflow.
- Reject login blocks for simple marketing CTAs.
- Reject AI blocks when the product is not actually AI/chat-driven.
- Reject file upload blocks when the product does not handle files, media, docs or imports.
- Reject `recharts`, `@tanstack/react-table`, `react-dropzone`, `ai` and `framer-motion` additions unless the section job earns the runtime.
- Reject full blocks that create generic SaaS template identity.
- Reject anything that cannot be made mobile-readable without a concrete responsive storyboard.

## Selection Flow

1. Identify the section job and whether Blocks.so is install source, reference-only or rejected.
2. Check existing/local/shadcn, Tailark, shadcnblocks, ReUI, HextaUI, MVPBlocks, SmoothUI, Eldora UI and custom code first.
3. Choose one exact Blocks.so item or explicitly reject Blocks.so for the section.
4. Verify source page `https://blocks.so/<category>/<name>` and endpoint `https://blocks.so/r/<name>.json`.
5. Record MIT license, dependencies, registry dependencies, demo-data replacement, accessibility notes, mobile behavior, reduced-motion fallback if motion exists, task ID, change ID and QA.
6. Map the item to `08-component-and-asset-plan.md`, `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`.

## Required Project File

```text
projects/<slug>/46-blocks-so-selection.md
```

The file must record exact item, source page, endpoint URL, install command, MIT license, dependencies, registry dependencies, visible purpose, demo-data replacement, accessibility notes, mobile behavior, reduced-motion fallback if relevant, decision, task ID, change ID and QA evidence.

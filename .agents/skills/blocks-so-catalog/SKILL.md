---
name: blocks-so-catalog
description: Use when adding, selecting, adapting, or reviewing Blocks.so blocks from blocks.so or the official @blocks-so shadcn registry. Applies to app/product proof blocks such as stats, login, onboarding, tables, dialogs, sidebars, AI chat, command menus, file upload, form layouts, and grid lists. Requires exact endpoint, MIT/license, dependency, demo-data replacement, mobile, accessibility, anti-fake-proof, and anti-template-copy checks before install or adaptation.
---

# Blocks.so Catalog

Use this skill when a landing plan considers Blocks.so for app-like product proof, dashboard fragments, onboarding flows, stats cards, dialogs, auth screens, tables, AI chat, command menus, file upload, form layouts, or visual references.

## Required First Step

Read the project source map:

```text
план разработки топового лендинга/50-blocks-so-source-map.md
```

If Blocks.so is used or seriously considered for a project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/46-blocks-so-selection.md
```

## Verified Model

- Official shadcn registry directory namespace: `@blocks-so`.
- Official URL template: `https://blocks.so/r/{name}.json`.
- Public live registry index: `https://blocks.so/r/registry.json`.
- Reliable source registry: `https://raw.githubusercontent.com/ephraimduncan/blocks/main/public/r/registry.json`.
- Current scan: 77 registry entries, all `registry:block`.
- Unique install names: 76, because `file-upload-01` appears twice in the registry index.
- Sitemap has 88 URLs: homepage, 11 category pages and 76 item pages.
- 88/88 sitemap URLs returned 200 on `HEAD`.
- 76/76 unique live item endpoints returned 200.
- Live `GET /r/registry.json` can return `ECONNRESET`; use GitHub raw for catalog rebuilds and verify exact live item endpoints before install.

## License Gate

Blocks.so is MIT.

- GitHub repo: `ephraimduncan/blocks`.
- Raw license file: `LICENSE.md`.
- GitHub API reports MIT.
- README says the project is free and open source and documents `@blocks-so`.

Still record source URL, endpoint URL, dependencies, registry dependencies, adaptation notes and screenshot evidence. Do not leave demo metrics, fake users, fake AI chats, fake auth flows, fake file names, fake tables or fake dashboard activity as product proof.

## Install Pattern

Official namespace:

```bash
npx shadcn@latest add @blocks-so/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://blocks.so/r/<name>.json
```

Use exact item names only. Do not bulk-install.

## Best Landing Uses

- Product proof stats: `stats-01` through `stats-15`.
- Auth or conversion flow proof: `login-01` through `login-09`.
- Onboarding and activation proof: `onboarding-01` through `onboarding-07`.
- Data/table proof: `table-01` through `table-05`.
- Real modal or decision flows: `dialog-01` through `dialog-12`.
- App shell reference: `sidebar-01` through `sidebar-06`.
- AI product surface: `ai-01` through `ai-05`.
- Command palette proof: `command-menu-01` through `command-menu-03`.
- Upload or document products: `file-upload-01` through `file-upload-06`.
- Form-heavy workflows: `form-layout-01` through `form-layout-05`.
- Dense lists: `grid-list-01` through `grid-list-03`.

## Reject By Default

- Fake dashboards, fake usage metrics, fake users, fake files, fake chat histories, fake tables and fake billing states.
- Full sidebars unless the landing is showing an app shell or product workflow.
- Login blocks for ordinary marketing sections; use only when auth or conversion flow is part of the story.
- AI blocks unless the product has a real AI/chat workflow.
- File upload blocks unless the product handles files, documents or media.
- Heavy table/chart dependencies when native cards, ReUI, HextaUI, MVPBlocks, SmoothUI, Tailark, shadcnblocks or custom code can show the proof more clearly.
- Blocks that require broad style rewrites or create generic SaaS template identity.

## Selection Checklist

1. Name the section job and whether Blocks.so is install source, reference-only, or rejected.
2. Verify exact endpoint `https://blocks.so/r/<name>.json`.
3. Record source page `https://blocks.so/<category>/<name>` and the official install command.
4. Record MIT license, dependencies, registry dependencies, demo-data replacement, accessibility notes, mobile behavior, reduced-motion fallback if motion exists, and QA evidence.
5. Map the item to `task-###` and `chg-###`.

## Sources

- https://blocks.so/
- https://blocks.so/sitemap.xml
- https://blocks.so/r/registry.json
- https://github.com/ephraimduncan/blocks
- https://raw.githubusercontent.com/ephraimduncan/blocks/main/public/r/registry.json
- https://raw.githubusercontent.com/ephraimduncan/blocks/main/LICENSE.md
- https://ui.shadcn.com/r/registries.json

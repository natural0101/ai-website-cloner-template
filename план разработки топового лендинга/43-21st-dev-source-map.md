# 21st.dev Source Map

Дата проверки: 2026-07-03.

21st.dev is a community marketplace and discovery surface for React components, templates, themes, MCP and CLI workflows. Use it as a gated inspiration and exact-component source, not as a default design system.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://21st.dev/ | 200 |
| Community components | https://21st.dev/community/components | 200 |
| Community templates | https://21st.dev/community/templates | 200 |
| MCP page | https://21st.dev/mcp | 200 |
| shadcn author page | https://21st.dev/@shadcn | 200 |
| Sitemap | https://21st.dev/sitemap.xml | 200, 9384 URLs |
| NPM CLI beta | https://www.npmjs.com/package/@21st-dev/cli | beta version `1.1.5`, MIT |
| Sample component page | https://21st.dev/@arlanoska/components/symbols-effect | 200 |
| Sample CDN registry | https://cdn.21st.dev/larsen66/symbols-effect/registry.1783013496574.json | 200 JSON |
| Generic registry guess | https://21st.dev/r/shadcn/button | 403 JSON |

## Site Inventory

Sitemap count:

- 9384 URLs total.
- 8260 author/component pages under `/@...`.
- 1000 tag/category pages under `/community/components/s/...`.
- 92 weekly component pages.
- 26 theme pages.
- `/mcp` is live but was not present in sitemap during this check.

Category checks:

| Category | URL | Observed count |
| --- | --- | ---: |
| Hero | https://21st.dev/community/components/s/hero | 284 |
| Background | https://21st.dev/community/components/s/background | 40 |
| Shader | https://21st.dev/community/components/s/shader | 87 |
| AI Chat | https://21st.dev/community/components/s/ai-chat | 78 |
| Features | https://21st.dev/community/components/s/features | 102 |
| Call to action | https://21st.dev/community/components/s/call-to-action | 56 |

The category and component pages are large Next.js payload pages. Install metadata can be embedded inside the payload instead of visible plain HTML.

## Install And Registry Model

Component pages expose install commands like:

```bash
npx @21st-dev/cli@beta add arlanoska/symbols-effect
```

The NPM package `@21st-dev/cli@beta` returned version `1.1.5`, MIT license, and description: search, retrieve, install 21st.dev components, and configure MCP for editors.

Some pages expose a CDN registry URL:

```text
https://cdn.21st.dev/larsen66/symbols-effect/registry.1783013496574.json
```

Sample registry JSON returned:

- `name`: `symbols-effect`
- keys: `$schema`, `name`, `type`, `title`, `description`, `dependencies`, `registryDependencies`, `files`
- dependencies: `three`
- registry dependencies: none

Do not guess `/r/<name>` endpoints. Generic guesses such as `/r/shadcn/button`, `/r/shadcn/accordion` and `/r/shadcn/dialog` returned 403 during this check.

## Sample Items Checked

| Page | Command | Registry URL | Registry | License | Dependencies |
| --- | --- | --- | --- | --- | --- |
| `/@arlanoska/components/symbols-effect` | `npx @21st-dev/cli@beta add arlanoska/symbols-effect` | CDN JSON 200 | `symbols-effect` | MIT | `three` |
| `/@arlanoska/components/amo-hover-button` | `npx @21st-dev/cli@beta add arlanoska/amo-hover-button` | CDN JSON 200 | `amo-hover-button` | MIT | none observed |
| `/@hero_ui/components/heroui-table` | `npx @21st-dev/cli@beta add hero_ui/heroui-table` | CDN JSON 200 | `heroui-table` | MIT | `@heroui/styles`, `@heroui/react` |
| `/@reapollo/components/animated-sparkline` | `npx @21st-dev/cli@beta add larsen66/animated-sparkline` | CDN JSON 200 | `animated-sparkline` | MIT | `@number-flow/react`, `@phosphor-icons/react` |

## Best Landing Defaults

| Need | Good source surface | Notes |
| --- | --- | --- |
| Reference mining | `/community/components/s/hero`, `/background`, `/shader`, `/features`, `/call-to-action`, `/pricing-section` | Use to find visual directions and section ideas. |
| AI or agent product | `/community/components/s/ai-chat`, `/ai-input`, `/agent`, `/prompt` | Useful for product proof when the offer is AI-adjacent. |
| Visual hero moment | shader, background, 3D, WebGL, text, image/video tags | Use one effect only and verify performance. |
| Product proof widget | table, calendar, chart, avatar, upload, editor, sparkline tags | Only if it clarifies the product workflow. |
| CTA/button detail | button, hover, magnetic, glow tags | Use a local implementation if the 21st component is too heavy. |

## Reject Or Use Carefully

- Reject broad imports from 21st.dev without a chosen exact page.
- Reject generic `/r/*` endpoint guesses; use the component page payload or CDN registry URL.
- Reject heavy WebGL, shader, HeroUI, chart or icon dependencies unless the section story earns them.
- Reject components with missing or unclear license.
- Reject effects that hide critical content behind hover, canvas, autoplay, pointer movement or video.
- Reject community styling that clashes with the landing's brand DNA; adapt token, radius, spacing, typography and motion.

## Selection Flow

1. Identify the section job and reference gap.
2. Search exact 21st.dev category/tag.
3. Capture exact component page and author/item slug.
4. Extract command and CDN registry URL if available.
5. Verify component page status and CDN registry JSON status.
6. Record license, dependencies, registry dependencies, adaptation, fallback, mobile behavior and QA.
7. Map accepted or rejected row to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/39-twenty-first-dev-selection.md
```

The file must record exact source page, author/item slug, command, CDN registry URL or reference-only status, access and license, dependencies, adaptation, fallback, mobile behavior, QA evidence, decision, task ID and change ID.

# Kokonut UI Source Map

Дата проверки: 2026-07-03.

Kokonut UI is an open-source shadcn-compatible component registry built with Tailwind CSS, shadcn/ui and Motion. Use it as a small exact-component source for polished AI inputs, buttons, cards, navigation, backgrounds, inputs and text effects.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://kokonutui.com/ | 200 |
| Docs | https://kokonutui.com/docs | 200 |
| Sitemap | https://kokonutui.com/sitemap.xml | 200, 49 URLs |
| LLM map | https://kokonutui.com/llms.txt | 200 |
| Public registry | https://kokonutui.com/r/registry.json | 200, 40 items |
| Sample item | https://kokonutui.com/r/particle-button.json | 200 JSON |
| GitHub repo | https://github.com/kokonut-labs/kokonutui | 200 |
| License | https://raw.githubusercontent.com/kokonut-labs/kokonutui/main/LICENSE | MIT |
| Pro site | https://kokonutui.pro/ | 200, paid/pro surface |
| Pro registry guess | https://kokonutui.pro/r/registry.json | 404 HTML |

## Site Inventory

Sitemap count:

- 49 URLs total.
- 47 docs URLs.
- 40 public registry items.

Docs categories:

| Category | Count |
| --- | ---: |
| AI | 5 |
| Backgrounds | 4 |
| Buttons | 9 |
| Cards | 10 |
| Inputs | 4 |
| Navigation | 6 |
| Texts | 8 |

Public registry scan:

- 40 `registry:component` items.
- 40/40 item endpoints returned 200.
- Common package dependencies: `motion` on 31 items, `lucide-react` on 20 items.
- Registry dependencies are mostly existing shadcn primitives such as `button`, `card`, `badge`, `textarea`, `input`, `dropdown-menu`, `drawer`, `tooltip`.

## Install Model

Default registry command from site:

```bash
npx shadcn@latest add @kokonutui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://kokonutui.com/r/<name>.json
```

Use exact item names from the public registry. Do not bulk-install all 40 items.

## Pro And License Gate

The open-source GitHub repo has MIT license. The public registry on `kokonutui.com/r/*` is usable as an open-source component source.

`kokonutui.pro` is a separate Pro/templates surface. It returned 200 for the site and templates page, but `https://kokonutui.pro/r/registry.json` returned 404 HTML. Treat Pro components/templates as reference-only unless paid access and license are explicit.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| AI/agent product proof | `ai-prompt`, `ai-input-search`, `ai-loading`, `ai-text-loading`, `ai-voice` | Use only when the product really has AI/agent workflow. |
| CTA tactility | `particle-button`, `gradient-button`, `hold-button`, `attract-button`, `command-button`, `slide-text-button` | One CTA/detail only. |
| Product/card proof | `bento-grid`, `apple-activity-card`, `currency-transfer`, `carousel-cards`, `spotlight-cards` | Replace demo content with real product evidence. |
| Navigation/search detail | `morphic-navbar`, `toolbar`, `smooth-tab`, `profile-dropdown`, `action-search-bar`, `smooth-drawer` | Avoid replacing simple landing nav without reason. |
| Input workflow | `file-upload`, `avatar-picker`, `team-selector` | Useful for product workflow demos. |
| Hero/background/text | `shape-hero`, `beams-background`, `background-paths`, `flow-field`, `shimmer-text`, `dynamic-text`, `sliced-text` | Must preserve contrast and reduced motion. |

## Reject Or Use Carefully

- Reject Kokonut UI Pro items without paid access/license evidence.
- Reject `liquid-glass-card`, `tweet-card`, loaders or fake AI components unless the section story earns them.
- Reject broad replacement of local shadcn UI.
- Reject decorative `motion` components when native CSS, Motion Primitives, Animate UI, Magic UI, React Bits, Cult UI or existing components cover the same result with lower risk.
- Reject any component whose hover/motion hides essential content or breaks mobile.

## Selection Flow

1. Identify the section job and component gap.
2. Check native/local/shadcn, Motion Primitives, Animate UI, Magic UI, React Bits, Cult UI and ReUI first.
3. Choose one exact public Kokonut UI item.
4. Verify docs page and exact registry endpoint.
5. Record dependencies, registry dependencies, license/pro status, adaptation, reduced-motion fallback, mobile behavior and QA.
6. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/40-kokonut-ui-selection.md
```

The file must record exact docs page, item, registry URL, install command, license/pro status, dependencies, registry dependencies, visible purpose, adaptation, fallback, mobile behavior, decision, task ID, change ID, risk and QA evidence.

# Magic UI Source Map

Дата обновления: 2026-07-03.

Magic UI is a shadcn-style source for animated components, marketing effects, templates and blocks. Use it sparingly: one strong effect can help a landing feel memorable; many effects make it look like a component gallery.

## Проверенные источники

| Source | URL | Result |
| --- | --- | --- |
| Website | https://magicui.design | 200 during crawl |
| Docs | https://magicui.design/docs | 91 live docs pages found |
| Components docs | https://magicui.design/docs/components | 77 component docs found |
| Templates docs | https://magicui.design/docs/templates/saas | 9 template docs found; `/docs/templates` itself returned 404 |
| Registry JSON | https://magicui.design/r/registry.json | 200, 247 total items |
| Source repo | https://github.com/magicuidesign/magicui | 200 via GitHub API, MIT license |

Registry count:

- 247 total items.
- 77 `registry:ui`.
- 168 `registry:example`.
- 1 `registry:style`.
- 1 `registry:lib`.

Live crawl count:

- 288 internal paths seen.
- 118 live HTML pages.
- 91 docs HTML pages.
- 77 component docs.
- 9 template docs.

Known crawl caveats:

- `/docs/templates` returned 404, while concrete template pages such as `/docs/templates/saas`, `/docs/templates/startup`, `/docs/templates/devtool`, `/docs/templates/mobile`, `/docs/templates/portfolio`, `/docs/templates/blog`, `/docs/templates/changelog`, `/docs/templates/codeforge`, and `/docs/templates/agent` are live.
- A malformed generated path `/&quot;` returned 404. Do not cite it.

## Install Model

Install one exact registry item:

```bash
npx shadcn@latest add "https://magicui.design/r/marquee.json"
```

Do not bulk-install. Use Magic UI only after `projects/<slug>/30-magic-ui-selection.md` records the item, source URL, install command, dependency impact, motion purpose, fallback, mobile plan and QA.

## Registry Families

| Family | Useful items |
| --- | --- |
| Hero/media | `hero-video-dialog`, `safari`, `iphone`, `android`, `terminal`, `video-text` |
| Feature/proof layout | `bento-grid`, `animated-list`, `avatar-circles`, `marquee`, `tweet-card` |
| Text effects | `animated-gradient-text`, `animated-shiny-text`, `aurora-text`, `hyper-text`, `morphing-text`, `number-ticker`, `text-animate`, `typing-animation`, `word-rotate`, `highlighter` |
| CTA/buttons | `interactive-hover-button`, `pulsating-button`, `rainbow-button`, `ripple-button`, `shimmer-button`, `shiny-button` |
| Background/pattern | `grid-pattern`, `dot-pattern`, `interactive-grid-pattern`, `animated-grid-pattern`, `retro-grid`, `flickering-grid`, `particles`, `meteors`, `warp-background`, `noise-texture`, `light-rays` |
| Surface accents | `magic-card`, `border-beam`, `shine-border`, `glare-hover`, `neon-gradient-card`, `backlight`, `progressive-blur`, `lens`, `pixel-image` |
| Diagrams and motion concepts | `animated-beam`, `orbiting-circles`, `globe`, `icon-cloud`, `dotted-map`, `scroll-progress`, `scroll-based-velocity` |
| High-risk playful effects | `smooth-cursor`, `pointer`, `dock`, `cool-mode`, `confetti`, `comic-text`, `spinning-text`, `text-3d-flip` |

## Best Landing Defaults

| Need | Good items | Notes |
| --- | --- | --- |
| Product demo proof | `hero-video-dialog`, `safari`, `iphone`, `android`, `terminal` | Use real product media, not fake screenshots. |
| Social proof strip | `marquee`, `avatar-circles`, `animated-list` | Only real logos/users/events. |
| Feature hierarchy | `bento-grid`, `magic-card`, `border-beam` | Needs real content hierarchy. |
| Key metric | `number-ticker` | Real metrics only; fallback shows final number. |
| Workflow/integrations | `animated-beam`, `orbiting-circles` | Do not imply integrations that do not exist. |
| Short display emphasis | `highlighter`, `aurora-text`, `animated-gradient-text` | Use for short phrase, not paragraph. |
| Primary CTA polish | `interactive-hover-button`, `shiny-button`, `ripple-button` | One primary CTA max. |

## Reject Or Use Carefully

- Reject `smooth-cursor`, `pointer`, `dock`, and `cool-mode` by default.
- Reject `confetti` unless it appears after a successful user action.
- Reject `globe`, `orbiting-circles`, `icon-cloud`, `dotted-map` when proof/integrations are not real.
- Reject `particles`, `meteors`, `retro-grid`, `flickering-grid`, `animated-grid-pattern`, `warp-background`, `light-rays` if contrast or CTA hierarchy suffers.
- Avoid autoplay carousels or marquee content that carries essential proof.
- Avoid `tweet-card` without real source relevance and permission.

## Dependency Warnings

Top dependencies in the registry:

- `motion`: 30 items.
- `next-themes`: 6 items.
- `@radix-ui/react-icons`: 6 items.
- Other notable dependencies: `framer-motion`, `react-tweet`, `rough-notation`, `shiki`, `cobe`, `canvas-confetti`, `svg-dotted-map`, `countries-list`.

For this project:

- Check `package.json` before install.
- Do not add `framer-motion` if `motion` can solve the effect.
- Treat `cobe`, `canvas-confetti`, `react-tweet`, `shiki`, map libraries and theme libraries as high-impact dependencies.

## Required Output

Fill this file when Magic UI is considered:

```text
projects/<slug>/30-magic-ui-selection.md
```

Promote accepted rows into:

```text
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/28-change-traceability-matrix.md
```

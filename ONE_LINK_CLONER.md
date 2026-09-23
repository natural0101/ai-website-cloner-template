# One-Link Cloner

Send your coding agent a target URL and an optional scope note:

```text
Clone https://example.com exactly, home page only.
Clone https://example.com/docs plus https://example.com/pricing.
Clone https://example.com in the same style, but make the copy unique.
```

The canonical workflow is [`.agents/skills/clone-website/SKILL.md`](.agents/skills/clone-website/SKILL.md). Platform-specific skills and commands are generated compatibility copies.

The agent should:

1. Run `npm run clone:prepare -- <url1> [<url2> ...]` and read `docs/research/CURRENT_TARGETS.*`.
2. Inventory existing routes and resolve route collisions or incompatible origins before changing the application.
3. Follow the canonical skill and its inspection reference with browser automation.
4. Extract screenshots, styles, text, behaviors, and original assets into the planned site/page namespaces.
5. Build shared foundations once, then implement each page at its planned destination route while preserving existing work.
6. Run `npm run check` and verify the cloned routes and responsive behavior.
7. Start `npm run dev` and report the source URL to local preview route mapping.

Each origin and page receives a collision-resistant key. Research and screenshots live under `docs/research/<site-key>/<page-key>/` and `docs/design-references/<site-key>/<page-key>/`; components live under `src/components/sites/`, and assets under `public/sites/`. Query strings and fragments are page states, so their route behavior must be explicit when they share a pathname.

For the first single target in an untouched template, `/` can host the clone. Further targets preserve their source pathnames. A target never authorizes overwriting an existing user-authored page. For different origins, resolve separate prepared app roots versus an intentionally combined app before editing global layout, fonts, or styles.

## Useful commands

```bash
npm run clone:prepare -- --dry-run https://example.com/docs
npm run clone:prepare -- https://example.com/docs https://example.com/pricing
npm run dev
npm run check
npm run design:check
```

The base project is intentionally plain until a target URL is cloned. Optional local Blender vendor files, generated media, and external skill checkouts are separate from the published core workflow.

# One-Link Cloner

This folder is prepared as a simple website-clone workbench.

## How to use it with Codex

Send Codex a target URL and a short scope note:

```text
Clone https://example.com
```

Optional scope hints:

```text
Clone https://example.com exactly, home page only.
Clone https://example.com in the same style, but make the copy unique.
Clone https://example.com plus pricing and contact pages.
```

Codex should then:

1. Run `npm run clone:prepare -- <url>`.
2. Use the local `/clone-website` skill instructions.
3. Inspect the target with browser automation.
4. Extract screenshots, styles, text, behaviors, and assets.
5. Build the clone as a Next.js page.
6. Run `npm run check`.
7. Start `npm run dev` and report the local preview URL.

## Useful commands

```bash
npm run clone:prepare -- https://example.com
npm run dev
npm run check
```

The base project is intentionally plain until a target URL is cloned.

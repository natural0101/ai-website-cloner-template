---
name: hextaui-catalog
description: Use HextaUI safely as a shadcn-compatible source for foundation components and app-oriented blocks. Trigger when choosing, installing, adapting, rejecting, or auditing HextaUI items for landing page product proof, AI workflow sections, auth/billing/settings/team/task screens, shadcn registry commands, exact HextaUI endpoints, or app UI previews.
---

# HextaUI Catalog

## Overview

Use HextaUI only when an exact app UI block or foundation component improves a specific landing section. Prefer local shadcn/custom UI, ReUI, MVPBlocks, SmoothUI, Kokonut UI, Tailark or shadcnblocks when they solve the same need with lower risk.

## Source Facts

- Main site: `https://www.hextaui.com/`.
- Registry index: `https://www.hextaui.com/r/registry.json`.
- Exact endpoint form: `https://www.hextaui.com/r/<name>.json`.
- Official shadcn namespace: `@hextaui`, mapped in `https://ui.shadcn.com/r/registries.json` to `https://hextaui.com/r/{name}.json`.
- LLM map: `https://www.hextaui.com/llms.txt`.
- GitHub repo: `https://github.com/preetsuthar17/HextaUI`.
- License: MIT on GitHub and package metadata.
- Verified inventory on 2026-07-03: 139 registry items, 139/139 exact item endpoints live, 54 foundation items, 14 AI, 16 auth, 15 billing, 18 settings, 15 team, 6 task and 1 project item.
- HTML docs caveat: many individual component/block HTML pages timed out during audit. Use exact registry endpoints, `llms.txt`, GitHub registry and official shadcn registry index as primary evidence.

## Install Commands

Use one exact item at a time:

```bash
npx shadcn@latest add @hextaui/<name>
npx shadcn@latest add https://hextaui.com/r/<name>.json
```

Prefer the exact URL form when the target project does not already know the `@hextaui` namespace. Do not bulk-install.

## Selection Workflow

1. Read the local source map if it exists: `план разработки топового лендинга/47-hextaui-source-map.md`.
2. Identify the section job: AI proof, auth/onboarding, billing/pricing, settings/admin, team/task workflow or exact foundation detail.
3. Check existing project components and lower-risk sources first.
4. Pick one exact HextaUI item or reject HextaUI for that section.
5. Verify `https://www.hextaui.com/r/<name>.json`.
6. Record the item in `projects/<slug>/43-hextaui-selection.md` with source URL, endpoint, command, dependencies, registry dependencies, MIT license, HTML-doc caveat, adaptation, mobile behavior, task ID, change ID and QA evidence.

## Useful Landing Picks

- AI proof: `ai-prompt-input`, `ai-message`, `ai-conversation`, `ai-citations`, `ai-model-selector`, `ai-streaming-response`, `ai-usage-quota`, `ai-file-upload`, `team-ai-room`, `team-prompt-library`.
- Billing/pricing proof: `billing-pricing-table`, `billing-plan-selector`, `billing-subscription-card`, `billing-usage-billing`, `billing-usage-alerts`, `billing-invoice-list`, `billing-payment-method`, `billing-upgrade-prompt`.
- Auth/onboarding proof: `auth-login-form`, `auth-signup-form`, `auth-otp-verify`, `auth-magic-link`, `auth-two-factor-setup`, `auth-session-manager`.
- Settings/admin proof: `settings-api-keys`, `settings-integrations`, `settings-webhooks`, `settings-security`, `settings-team-members`, `settings-notifications`, `settings-domains`.
- Team/task proof: `team-dashboard`, `team-member-list`, `team-permissions-matrix`, `team-projects`, `task-board`, `task-list`, `task-detail`, `project-list`.
- Foundation details: `button-group`, `input-group`, `empty`, `field`, `kbd`, `native-select`, `tree`, `video-player`, `sidebar`.

## Rejection Rules

- Reject HTML docs pages as the sole proof when they time out.
- Reject root `/registry.json` and `registry.hextaui.com` guesses.
- Reject broad replacement of local shadcn primitives.
- Reject AI blocks for non-AI products.
- Reject auth, billing, settings, team and task blocks when they create fake product surfaces.
- Reject heavy dependencies such as `react-markdown`, `shiki`, `recharts`, `next`, `vaul`, `react-day-picker`, `embla-carousel-react` or `react-resizable-panels` without a real product reason.
- Replace demo data, fake users, fake invoices, fake usage metrics and fake prompts before using screenshots or live UI as proof.
- Simplify dense tables, boards, sidebars, permission matrices and settings panels on mobile.

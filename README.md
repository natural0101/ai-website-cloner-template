# AI Website Cloner Template

<a href="https://github.com/JCodesMore/ai-website-cloner-template/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" /></a> <a href="https://github.com/JCodesMore/ai-website-cloner-template/stargazers"><img src="https://img.shields.io/github/stars/JCodesMore/ai-website-cloner-template?style=flat" alt="Stars" /></a> <a href="https://discord.gg/hrTSX5yTpB"><img src="https://img.shields.io/discord/1400896964597383279?label=discord" alt="Discord" /></a>

A reusable template for reverse-engineering any website into a clean, modern Next.js codebase using AI coding agents.

**Recommended: [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with Opus 4.7 for best results** — but works with a variety of AI coding agents.

Point it at a URL, run `/clone-website`, and your AI agent will inspect the site, extract design tokens and assets, write component specs, and dispatch parallel builders to reconstruct every section.

## Enhanced Fork

All checks run locally. GitHub Actions are disabled for this fork; upstream workflow files must not be restored.

This fork combines the upstream cloning workflow with a one-link target planner, reusable design knowledge, landing and commerce blueprints, Blender workflows, and compatibility integrations for additional coding agents. The canonical clone skill is [.agents/skills/clone-website/SKILL.md](.agents/skills/clone-website/SKILL.md); generated platform copies all come from that source.

Each target gets collision-resistant site/page namespaces for research, screenshots, components, and assets. Existing pages are preserved, source pathnames map to destination routes, and styles or metadata are scoped when sites share an application. See [ONE_LINK_CLONER.md](ONE_LINK_CLONER.md) for the one-link workflow.

Reusable instructions and scripts are published. Downloaded vendor bundles, generated media, local session files, and external skill checkouts are optional local resources and are not published with this fork. Install or provide them only for a task that needs them; core cloning does not require them.

## Universal Design Knowledge Base

This repository also contains a reusable design-agent workbench for projects outside this template. Start at:

```text
docs/design-workbench/AGENT_START_HERE.md
```

Use it for dashboards, admin panels, SaaS product UI, AI design studios, canvas editors, component systems, websites, motion, 3D/WebGL, proof/data integrity, and final UI QA. It is intentionally not landing-only.

For handoff prompts and the product UI completion gate, read:

```text
docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md
docs/design-workbench/AGENT_PROMPTS.md
docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json
docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
docs/design-workbench/AGENT_REPORT_EXAMPLES.md
.codex/skills/product-ui-design-orchestrator/SKILL.md
.codex/skills/product-design-taste/SKILL.md
.codex/skills/product-ui-component-sourcing/SKILL.md
.codex/skills/product-ui-visual-qa/SKILL.md
.codex/skills/design-ai-workbench-screens/SKILL.md
```

To verify that the design workbench, generated agent rules, and product UI skills are still wired together, run:

```bash
npm run design:check
```

This checks key design-workbench anchors plus local `.codex/skills`, `.agents/skills`, and global Codex skill copies.
For machine-readable routing, use `docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json`.

To print a ready prompt for an agent working in another project, run:

```bash
npm run design:handoff -- "C:\path\to\target-project"
```

Modes: `auto`, `handoff`, `universal`, `forgestudio`, `dashboard`, `scratch`, `qa`. `auto` inspects the target folder and is the default.
Add `--write` to create `DESIGN_AGENT_HANDOFF.md` inside the target project.
Use `--pack` or `npm run design:pack -- "C:\path\to\target-project"` to create `DESIGN_AGENT_HANDOFF.md` plus `.design-agent/README.md`, `.design-agent/prompt.txt`, `.design-agent/working-brief.md`, `.design-agent/manifest.json`, `.design-agent/acceptance-checklist.md`, `.design-agent/final-report-template.md`, and `.design-agent/AGENTS_SNIPPET.md` in the target project.
Run `npm run design:install-agent-rules -- "C:\path\to\target-project"` when the target project should receive a managed `AGENTS.md` block pointing future agents to the packet.
Then run `npm run design:packet-check -- "C:\path\to\target-project"` to verify the packet before handing it to another agent.
After the agent fills `.design-agent/working-brief.md`, run `npm run design:brief-check -- "C:\path\to\target-project"` before coding. Before final handoff, run `npm run design:final-check -- "C:\path\to\target-project"`.
Run `npm run design:target-audit -- "C:\path\to\target-project" --write` to create `.design-agent/readiness-report.md` with packet, brief, final-report, and next-command status.

## Demo

[![Watch the demo](docs/design-references/comparison.png)](https://youtu.be/O669pVZ_qr0)

> Click the image above to watch the full demo on YouTube.

## Quick Start

> **Important:** Start by making your own copy with GitHub's **Use this template** button. Do not clone this template repository directly for your website project, and do not open pull requests here with your generated website.

1. **Create your own repository from this template**

   On the GitHub page for this project, click **Use this template**, then click **Create a new repository**.

   Give your new repository a name, choose whether it should be public or private, then click **Create repository**. If GitHub shows an **Include all branches** option, you can leave it off.

   This gives you your own separate project to work in, so your website changes stay in your account instead of coming back to the main template.

2. **Open your new repository on your computer**

   After GitHub creates your copy, open that new repository. Click **Code** and open or clone your new repository with your preferred coding tool.

   If you use the terminal, the command will look like this:

   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-NEW-REPOSITORY.git
   cd YOUR-NEW-REPOSITORY
   ```

3. **Install dependencies**
   ```bash
   npm install
   ```
4. **Start your AI agent** — Claude Code recommended:
   ```bash
   claude --chrome
   ```
5. **Run the skill**:
   ```
   /clone-website <target-url1> [<target-url2> ...]
   ```
6. **Customize** (optional) — after the base clone is built, modify as needed

> Using a different agent? Open `AGENTS.md` for project instructions — most agents pick it up automatically.

## Supported Platforms

| Agent                                                         | Status                     |
| ------------------------------------------------------------- | -------------------------- |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | **Recommended** — Opus 4.7 |
| [Codex CLI](https://github.com/openai/codex)                  | Supported                  |
| [OpenCode](https://opencode.ai/)                              | Supported                  |
| [GitHub Copilot](https://github.com/features/copilot)         | Supported                  |
| [Cursor](https://cursor.com/)                                 | Supported                  |
| [Windsurf](https://codeium.com/windsurf)                      | Supported                  |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)     | Supported                  |
| [Kiro](https://kiro.dev/)                                  | Supported                  |
| [Cline](https://github.com/cline/cline)                       | Supported                  |
| [Roo Code](https://github.com/RooCodeInc/Roo-Code)            | Supported                  |
| [Continue](https://continue.dev/)                             | Supported                  |
| [Amazon Q](https://aws.amazon.com/q/developer/)               | Supported                  |
| [Augment Code](https://www.augmentcode.com/)                  | Supported                  |
| [Aider](https://aider.chat/)                                  | Supported                  |

## Prerequisites

- [Node.js](https://nodejs.org/) 24+
- An AI coding agent (see [Supported Platforms](#supported-platforms))

## Tech Stack

- **Next.js 16** — App Router, React 19, TypeScript strict
- **shadcn/ui** — Radix primitives + Tailwind CSS v4
- **Tailwind CSS v4** — oklch design tokens
- **Lucide React** — default icons (replaced by extracted SVGs during cloning)

## How It Works

The `/clone-website` skill runs a multi-phase pipeline:

1. **Reconnaissance** — screenshots, design token extraction, interaction sweep (scroll, click, hover, responsive)
2. **Foundation** — updates fonts, colors, globals, downloads all assets
3. **Component Specs** — writes detailed spec files (`docs/research/components/`) with exact computed CSS values, states, behaviors, and content
4. **Parallel Build** — dispatches builder agents in git worktrees, one per section/component
5. **Assembly & QA** — merges worktrees, wires up the page, runs visual diff against the original

Each builder agent receives the full component specification inline — exact `getComputedStyle()` values, interaction models, multi-state content, responsive breakpoints, and asset paths. No guessing.

## Use Cases

- **Platform migration** — rebuild a site you own from WordPress/Webflow/Squarespace into a modern Next.js codebase
- **Lost source code** — your site is live but the repo is gone, the developer left, or the stack is legacy. Get the code back in a modern format
- **Learning** — deconstruct how production sites achieve specific layouts, animations, and responsive behavior by working with real code

## Not Intended For

- **Phishing or impersonation** — this project must not be used for deceptive purposes, impersonation, or any activity that breaks the law.
- **Passing off someone's design as your own** — logos, brand assets, and original copy belong to their owners.
- **Violating terms of service** — some sites explicitly prohibit scraping or reproduction. Check first.

## Project Structure

```
src/
  app/              # Next.js routes
  components/       # React components
    ui/             # shadcn/ui primitives
    sites/          # Namespaced page components and shared extracted icons
  lib/utils.ts      # cn() utility
  types/            # TypeScript interfaces
  hooks/            # Custom React hooks
public/
  sites/            # Namespaced site/page images, fonts, videos, and SEO assets
docs/
  research/         # Extraction output & component specs
  design-references/ # Screenshots
scripts/
  check-design-workbench.mjs # Verify universal design workbench wiring
  print-design-handoff.mjs # Print/write a ready prompt or design packet for another agent/project
  sync-agent-rules.sh  # Regenerate agent instruction files
  sync-skills.mjs      # Regenerate /clone-website for all platforms
AGENTS.md           # Agent instructions (single source of truth)
CLAUDE.md           # Claude Code config (imports AGENTS.md)
GEMINI.md           # Gemini CLI config (imports AGENTS.md)
```

## Commands

```bash
npm run dev    # Start dev server
npm run build  # Production build
npm run lint   # ESLint check
npm run typecheck # TypeScript check
npm run check  # Run lint + typecheck + build
npm run design:check # Verify design workbench wiring
npm run design:handoff -- "<target-project>" # Print auto-selected design handoff prompt
npm run design:handoff -- "<target-project>" --write # Write DESIGN_AGENT_HANDOFF.md into target project
npm run design:pack -- "<target-project>" # Write DESIGN_AGENT_HANDOFF.md plus .design-agent packet into target project
npm run design:install-agent-rules -- "<target-project>" # Install managed design-agent block into target AGENTS.md
npm run design:packet-check -- "<target-project>" # Verify the target project's .design-agent packet
npm run design:brief-check -- "<target-project>" # Verify working brief was filled before coding
npm run design:final-check -- "<target-project>" # Verify final report has real evidence before handoff
npm run design:target-audit -- "<target-project>" --write # Write .design-agent/readiness-report.md
```

### If using docker

```bash
docker compose up app --build # build and run the app
docker compose up dev --build # run the app in dev mode on port 3001
```

## Updating for Other Platforms

Two source-of-truth files power all platform support. Edit the source, then run the sync script:

| What                   | Source of truth                         | Sync command                       |
| ---------------------- | --------------------------------------- | ---------------------------------- |
| Project instructions   | `AGENTS.md`                             | `bash scripts/sync-agent-rules.sh` |
| `/clone-website` skill | `.agents/skills/clone-website/SKILL.md` | `node scripts/sync-skills.mjs`     |

Each script regenerates the platform-specific copies automatically. The skill generator also copies the inspection reference beside each generated skill and rewrites reference links in command wrappers. Claude Code retains an invocable generated skill; Codex, Cursor, and OpenCode can also discover the canonical cross-agent skill. Keep the generated files committed and verify synchronization after editing the source.


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JCodesMore/ai-website-cloner-template&type=Date)](https://star-history.com/#JCodesMore/ai-website-cloner-template&Date)

## License

MIT

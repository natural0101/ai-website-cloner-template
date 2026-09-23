#!/usr/bin/env node

import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();
const promptsPath = path.join(repoRoot, "docs", "design-workbench", "AGENT_PROMPTS.md");
const manifestPath = path.join(repoRoot, "docs", "design-workbench", "DESIGN_WORKBENCH_MANIFEST.json");
const agentRulesBegin = "<!-- BEGIN:design-agent-packet -->";
const agentRulesEnd = "<!-- END:design-agent-packet -->";

const modes = {
  auto: "",
  handoff: "Handoff Packet Prompt",
  universal: "Universal Product UI Prompt",
  forgestudio: "ForgeStudio-Specific Prompt",
  dashboard: "Dashboard Upgrade Prompt",
  scratch: "New UI From Scratch Prompt",
  qa: "Final QA Prompt",
};

const requiredPromptAnchor = "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md";

function usage() {
  console.log(`Usage: node scripts/print-design-handoff.mjs <target-project-path> [--mode <mode>] [--write] [--pack] [--install-agent-rules] [--output <file>]

Modes:
  auto        Inspect target files and choose a prompt mode (default)
  handoff      Compact packet prompt
  universal   Universal product UI/dashboard/editor prompt
  forgestudio ForgeStudio-like AI design app prompt
  dashboard   Dashboard/admin/data-tool upgrade prompt
  scratch     Product UI from scratch prompt
  qa          Final product UI QA prompt

Options:
  --write       Write DESIGN_AGENT_HANDOFF.md into the target project
  --pack        Write DESIGN_AGENT_HANDOFF.md plus .design-agent/ packet files
  --install-agent-rules
                Add or replace a managed design-agent block in target AGENTS.md
  --output      Custom output file path for --write`);
}

function parseArgs(argv) {
  const args = [...argv];
  let mode = "auto";
  let targetPath = "";
  let write = false;
  let pack = false;
  let installAgentRules = false;
  let outputPath = "";

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      return { help: true, mode, targetPath, write, pack, installAgentRules, outputPath };
    }

    if (arg === "--write") {
      write = true;
      continue;
    }

    if (arg === "--pack") {
      pack = true;
      write = true;
      continue;
    }

    if (arg === "--install-agent-rules" || arg === "--install-agents") {
      installAgentRules = true;
      pack = true;
      write = true;
      continue;
    }

    if (arg === "--output") {
      outputPath = args[index + 1] ?? "";
      index += 1;
      continue;
    }

    if (arg.startsWith("--output=")) {
      outputPath = arg.slice("--output=".length);
      continue;
    }

    if (arg === "--mode") {
      mode = args[index + 1] ?? "";
      index += 1;
      continue;
    }

    if (arg.startsWith("--mode=")) {
      mode = arg.slice("--mode=".length);
      continue;
    }

    if (!targetPath) {
      targetPath = arg;
    }
  }

  return { help: false, mode, targetPath, write, pack, installAgentRules, outputPath };
}

function extractPrompt(markdown, heading) {
  const headingLine = `## ${heading}`;
  const headingIndex = markdown.indexOf(headingLine);
  if (headingIndex === -1) {
    throw new Error(`Prompt section not found: ${heading}`);
  }

  const sectionStart = markdown.indexOf("\n", headingIndex);
  const sectionBodyStart = sectionStart === -1 ? markdown.length : sectionStart + 1;
  const rest = markdown.slice(sectionBodyStart);
  const nextHeadingMatch = rest.match(/^## /m);
  const section = nextHeadingMatch ? rest.slice(0, nextHeadingMatch.index) : rest;

  const codeMatch = section.match(/```text\s*([\s\S]*?)```/);
  if (!codeMatch) {
    throw new Error(`Prompt code block not found: ${heading}`);
  }

  return codeMatch[1].trim();
}

function normalizeMode(mode) {
  const normalized = mode.trim().toLowerCase();
  if (!Object.hasOwn(modes, normalized)) {
    throw new Error(`Unknown mode "${mode}". Use one of: ${Object.keys(modes).join(", ")}`);
  }
  return normalized;
}

function isIgnoredDirectory(name) {
  return [
    ".git",
    ".next",
    ".turbo",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "release",
    ".venv",
    "__pycache__",
  ].includes(name);
}

function collectTargetSnapshot(targetPath) {
  if (!targetPath || targetPath === "<TARGET_PROJECT_PATH>" || !existsSync(targetPath)) {
    return {
      exists: false,
      files: [],
      text: "",
    };
  }

  const files = [];
  const textChunks = [];
  const maxFiles = 500;
  const maxBytesPerFile = 16000;
  const maxDepth = 3;

  function visit(currentPath, depth) {
    if (files.length >= maxFiles || depth > maxDepth) {
      return;
    }

    let entries = [];
    try {
      entries = readdirSync(currentPath, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (files.length >= maxFiles) {
        return;
      }

      if (entry.isDirectory() && isIgnoredDirectory(entry.name)) {
        continue;
      }

      const entryPath = path.join(currentPath, entry.name);
      const relativePath = path.relative(targetPath, entryPath).split(path.sep).join("/");

      if (entry.isDirectory()) {
        visit(entryPath, depth + 1);
        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      files.push(relativePath);

      if (!/\.(md|txt|json|csv|ts|tsx|js|jsx|vue|svelte|css|scss|html)$/i.test(entry.name)) {
        continue;
      }

      try {
        const stats = statSync(entryPath);
        if (stats.size > maxBytesPerFile) {
          continue;
        }
        textChunks.push(`\n--- ${relativePath} ---\n${readFileSync(entryPath, "utf8")}`);
      } catch {
        // Ignore unreadable files; auto mode should be helpful, not fragile.
      }
    }
  }

  visit(targetPath, 0);

  return {
    exists: true,
    files,
    text: `${files.join("\n")}\n${textChunks.join("\n")}`.toLowerCase(),
  };
}

function countMatches(text, patterns) {
  let count = 0;
  for (const pattern of patterns) {
    const matches = text.match(pattern);
    count += matches ? matches.length : 0;
  }
  return count;
}

function chooseAutoMode(targetPath) {
  const snapshot = collectTargetSnapshot(targetPath);
  if (!snapshot.exists || snapshot.files.length < 5) {
    return {
      mode: "scratch",
      reason: snapshot.exists
        ? "target has very few files, so a from-scratch product UI prompt is safest"
        : "target path was not found, so a from-scratch product UI prompt is safest",
    };
  }

  const text = snapshot.text;
  const scores = {
    forgestudio: countMatches(text, [
      /forgestudio/g,
      /designtransaction/g,
      /agent proposal/g,
      /proposal\/diff/g,
      /mcp/g,
      /ledger/g,
      /canvas/g,
      /comment task/g,
      /verification/g,
      /apps\/studio/g,
    ]),
    dashboard: countMatches(text, [
      /dashboard/g,
      /admin/g,
      /analytics/g,
      /metrics/g,
      /records/g,
      /data table/g,
      /datatable/g,
      /tanstack/g,
      /chart/g,
      /filters/g,
      /export/g,
      /saved views/g,
    ]),
  };

  if (scores.forgestudio >= 4 && scores.forgestudio >= scores.dashboard) {
    return {
      mode: "forgestudio",
      reason: `found AI design workbench signals (${scores.forgestudio}) such as canvas/proposal/ledger/agent workflow`,
    };
  }

  if (scores.dashboard >= 4) {
    return {
      mode: "dashboard",
      reason: `found dashboard/admin/data-tool signals (${scores.dashboard}) such as metrics/tables/filters/export`,
    };
  }

  return {
    mode: "universal",
    reason: "target looks like an existing product/site, but no specialized dashboard or ForgeStudio signal dominated",
  };
}

function resolveOutputPath(targetPath, outputPath) {
  if (!targetPath || targetPath === "<TARGET_PROJECT_PATH>") {
    throw new Error("Cannot use --write without a real target project path.");
  }

  if (!existsSync(targetPath)) {
    throw new Error(`Cannot use --write because target path does not exist: ${targetPath}`);
  }

  const stats = statSync(targetPath);
  if (!stats.isDirectory()) {
    throw new Error(`Cannot use --write because target path is not a directory: ${targetPath}`);
  }

  if (!outputPath) {
    return path.join(targetPath, "DESIGN_AGENT_HANDOFF.md");
  }

  return path.isAbsolute(outputPath) ? outputPath : path.join(targetPath, outputPath);
}

function buildHandoffMarkdown({ prompt, promptMode, targetPath, knowledgeBasePath, autoSelection }) {
  const autoBlock = autoSelection
    ? `Auto-selected mode: ${promptMode}\nReason: ${autoSelection.reason}\n`
    : `Mode: ${promptMode}\n`;

  return `# Design Agent Handoff

Generated: ${new Date().toISOString()}
Knowledge base: ${knowledgeBasePath}
Target project: ${targetPath}
${autoBlock}
## Prompt

\`\`\`text
${prompt}
\`\`\`
`;
}

function buildPackReadme({ promptMode, targetPath, knowledgeBasePath, autoSelection }) {
  const reason = autoSelection ? autoSelection.reason : "explicit mode selected";
  return `# Design Agent Packet

This packet was generated from the Universal Design Workbench.

Knowledge base:

\`\`\`text
${knowledgeBasePath}
\`\`\`

Target project:

\`\`\`text
${targetPath}
\`\`\`

Mode: ${promptMode}
Reason: ${reason}

## Use Order

1. Read \`../DESIGN_AGENT_HANDOFF.md\`.
2. Use \`prompt.txt\` as the exact working prompt if the chat context is empty.
3. Use \`manifest.json\` to find the source docs, skills, commands, and non-negotiables.
4. Fill \`working-brief.md\` before coding so the work stays product-shaped.
5. Keep \`acceptance-checklist.md\` open while working.
6. From the knowledge base, run \`npm run design:packet-check -- "${targetPath}"\` when you need to verify packet integrity.
7. From the knowledge base, run \`npm run design:brief-check -- "${targetPath}"\` after filling the working brief and before coding. It checks substance, not only placeholders.
8. Use \`final-report-template.md\` before final handoff.
9. From the knowledge base, run \`npm run design:final-check -- "${targetPath}"\` before final handoff.
10. Run \`npm run design:target-audit -- "${targetPath}" --write\` to refresh \`.design-agent/readiness-report.md\`.

## Rules

- Work in the target project, not in the knowledge-base repository, unless the user asks otherwise.
- Do not force landing-page structure onto dashboards, editors, admin panels, data tools, or AI workbenches.
- Do not start coding from a generic brief. \`working-brief.md\` must name user/job/object, product object model, visual system contract, workflow/action path, data/source truth, route/screen, verification evidence, and top-design target.
- Do not start coding until the brief names the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
- Do not claim completion without target-relative changed-file paths, commands, browser/screenshot evidence, or an explicit remaining-risk note.
- Do not fill \`Product read\`, \`Object model checked\`, \`Visual system checked\`, \`Workflow improved\`, or \`Implementation slice contract\` with generic \`done\` or component-only text; they must reference the brief's route/screen, primary object, visual system contract, workflow/actions, data/source truth, and states.
- Do not fill top-design fields with generic \`passed\`, \`checked\`, or \`improved\`; \`Five-second test\` must name object, state, next action, recovery, and evidence.
- For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, fill \`AI Design App Invariants\` with the concrete proposal-only path plus agent bridge proof: preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. \`N/A\` is allowed only when the surface is not an AI design app.
`;
}

function buildWorkingBrief({ promptMode, targetPath, knowledgeBasePath }) {
  return `# Design Agent Working Brief

Mode: ${promptMode}

Knowledge base:

\`\`\`text
${knowledgeBasePath}
\`\`\`

Target project:

\`\`\`text
${targetPath}
\`\`\`

Fill this before coding. Keep answers short, concrete, and tied to real files/routes/data.

## Project Snapshot

- Stack:
- Main package scripts:
- Existing routes/screens:
- Existing components/tokens:
- Existing data or fixture source:
- Browser/dev-server command:
- Constraints or risky areas:

## Surface Classification

- Surface type:
- Is this marketing, product UI, dashboard/admin, editor/canvas, AI design studio, website, 3D/WebGL, or hybrid?
- Closest product surface blueprint:
- Why:
- Landing-page patterns allowed? yes/no and why:

## Product Read

- Primary user:
- Primary job:
- Core loop:
- Product object model:
- Visual system contract:
- Density target:
- Tone:
- Highest-risk user mistake:

## Scope

- Route/screen/workflow to change:
- Primary object:
- User action path:
- Out of scope:
- Deferred states:

## Implementation Slice Contract

- Route/screen:
- Primary object:
- User job:
- Data/fixture truth:
- Screen recipe/state specs:
- Local files to inspect/change:
- Component state plan:
- Included states:
- Deferred states:
- Actions:
- Responsive behavior:
- Commands to run:
- Screenshots/browser evidence to capture:
- Risks:

## Information Architecture

- App shell/navigation:
- Object hierarchy:
- Main zones:
- Responsive zone changes:
- Recovery/history path:

## Interaction And State Model

- Entry state:
- Empty state:
- Loading state:
- Error state:
- Disabled state:
- Selected/focused state:
- Pending state:
- Success state:
- Retry/rollback state:

## Copy And Status Language

- Status labels:
- Empty/error copy:
- Sample/demo labels:
- Toast vs inline policy:
- Proof/evidence language:

## Decision Or Review Cockpit

- Decision question:
- Options or comparison:
- Evidence:
- Risks:
- Primary action:
- Secondary action:
- After-state:
- Audit/recovery path:

## Trusted Vertical

Use this section for AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like products. For other surfaces, write \`N/A - not an AI design app\` in each field instead of leaving it blank.

- Trusted vertical segment:
- Source-of-truth objects:
- False-state risks:
- Proof/evidence surfaces:
- Decision question:
- After-state:
- Recovery path:

## Top Design Benchmark

- Top-design target:
- Five-second test target:
- Primary object/state/next action:
- Weakest expected visual category:
- Mediocrity risks to avoid:
- Product-specific details to make distinctive:

## Component Plan

- Local components to reuse:
- New components to create:
- External components considered:
- Product job for each external component:
- Demo data to remove or label:

## AI Design App Invariants

Use this section for ForgeStudio-like or AI design apps. For other surfaces, write \`N/A - not an AI design app\`.

- External AI is proposal-only until:
- Preview/diff visible:
- Verification visible:
- Human approval visible:
- Transaction/ledger evidence visible:
- Agent connection/scopes visible:
- Comment-to-task bridge visible:
- Pending proposal/approval bridge visible:
- Failure/recovery handling visible:
- Export/reopen path:

## Verification Plan

- Build/type/lint commands:
- Browser routes:
- Desktop screenshot:
- Tablet/mobile screenshot:
- Keyboard/focus checks:
- Known remaining risks:
`;
}

function buildAcceptanceChecklist({ promptMode }) {
  return `# Design Agent Acceptance Checklist

Mode: ${promptMode}

## Before Coding

- [ ] \`.design-agent/working-brief.md\` filled with project snapshot, product read, scope, and implementation slice.
- [ ] \`npm run design:brief-check -- "<target-project>"\` passes before coding; weak fields such as \`improve UI\`, \`make better\`, \`use app\`, \`done\`, or core-field \`N/A\` are not accepted.
- [ ] Surface classified: dashboard, admin, editor, canvas-workbench, SaaS app, AI design studio, website, landing, 3D/WebGL, or hybrid.
- [ ] Product read stated: user, job, core loop, density, risk, and tone.
- [ ] Product object model names entities, fields/attributes, status lifecycle, permissions/events, and source truth before coding.
- [ ] Visual system contract names typography, spacing/density, radius/borders/surfaces, color/status/contrast, motion/icon policy, and target-local tokens/components before coding.
- [ ] Universal Product Design Brief used.
- [ ] Closest Product Surface Blueprint chosen.
- [ ] Screen recipe/state specs chosen before coding.
- [ ] Local files to inspect/change named before coding.
- [ ] Component state plan names the states the changed components must support.
- [ ] Information architecture mapped: routes, navigation, zones, object hierarchy, responsive behavior, and recovery paths.
- [ ] Product UI Screen Recipe chosen.
- [ ] Interaction transitions defined, including pending, failure, retry, rollback, and success states.
- [ ] Copy/status language defined with object, state, reason, next action, and evidence/sample label when relevant.
- [ ] Decision/review cockpit defined when approval, comparison, triage, or proposal review is involved.
- [ ] For AI design studios/canvas/proposal workflows, trusted vertical segment, source-of-truth objects, false-state risks, proof/evidence surfaces, after-state, and recovery path are filled; for other surfaces, they are marked N/A.
- [ ] For AI design studios/canvas/proposal workflows, \`AI Design App Invariants\` names where proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen are visible; for other surfaces, it is marked N/A.
- [ ] Top-design benchmark target filled: five-second test, primary object/state/next action, weakest expected visual category, mediocrity risks, and product-specific details.
- [ ] Implementation slice contract filled: route/screen, object, data source, states, actions, responsive behavior, commands, screenshots, and risks.

## During Implementation

- [ ] Existing project stack, tokens, components, and conventions checked before adding UI libraries.
- [ ] Component blueprints and key component states used for shells, tables/lists, filters, drawers, inspectors, command menus, review panels, alerts, and toasts.
- [ ] No isolated decorative component is passed off as a product slice.
- [ ] No fake metrics, proof, screenshots, imported assets, agent status, testimonials, or completed work.
- [ ] Dashboard/admin/editor surfaces avoid marketing hero layout unless the surface is actually marketing.
- [ ] Motion supports continuity, hierarchy, feedback, or state change.

## Final QA

- [ ] Product UI Review Rubric scored.
- [ ] Rubric score is numeric on a /30 scale or convertible to /30.
- [ ] PASS uses 26+/30; PASS WITH RISKS uses 18+/30 or higher.
- [ ] \`Product read\`, \`Workflow improved\`, and \`Implementation slice contract\` reference the working brief's route/screen, primary object, workflow/actions, data/fixture truth, and states.
- [ ] Product UI Top Design Benchmark checked; five-second test passes or remaining risk is reported.
- [ ] \`Five-second test\` names object, state, next action, recovery, and evidence; generic \`passed\`, \`checked\`, \`improved\`, or \`looks good\` text is not accepted.
- [ ] \`Mediocrity risks fixed\` references the working brief's \`Mediocrity risks to avoid\`.
- [ ] \`Product-specific details\` references the working brief's \`Product-specific details to make distinctive\`.
- [ ] For AI design studios/canvas/proposal workflows, \`Operational pattern checked\` names proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen evidence.
- [ ] All 0-score rubric categories fixed or reported as blockers.
- [ ] Real project command evidence recorded as 'REAL_PROJECT_COMMANDS' or explicitly marked 'NOT_RUN_WITH_RISK'.
- [ ] Command evidence artifacts recorded as non-empty command logs when 'REAL_PROJECT_COMMANDS' is used.
- [ ] Visual evidence verdict recorded as 'REAL_BROWSER_SCREENSHOTS', 'USER_SCREENSHOTS', 'MANUAL_BROWSER_INSPECTION', or 'NOT_RUN_WITH_RISK'.
- [ ] Manual inspection notes artifact names route/screen, viewport or pixel size, and visual/layout/focus/overlap check when 'MANUAL_BROWSER_INSPECTION' is used.
- [ ] Desktop/tablet/mobile responsive behavior checked when the project can run in browser.
- [ ] No incoherent overlap, clipped text, unstable toolbar/button dimensions, or unreadable contrast found.
- [ ] Keyboard/focus-visible basics checked for changed controls.
- [ ] \`Information architecture checked\` names route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior.
- [ ] \`Interaction model checked\` names primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control.
- [ ] \`Copy/status language checked\` names status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label.
- [ ] \`Decision/review cockpit checked\` names decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path.
- [ ] \`Visual system checked\` names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
- [ ] State coverage checked: empty, loading, error, disabled, selected, hover, focus, pending, success, retry/rollback where relevant.
- [ ] \`State coverage checked\` covers every state promised in \`.design-agent/working-brief.md\` \`Included states\`, except states explicitly listed as deferred.
- [ ] \`Component state evidence checked\` names changed components/controls, concrete states, and screenshot/browser/manual/keyboard/responsive evidence.
- [ ] Visual/browser evidence captured or remaining verification risk stated.
- [ ] \`.design-agent/final-report-template.md\` used for the final report.
- [ ] \`Files changed\` lists target-relative paths that exist in this project.
- [ ] \`Browser routes checked\` includes the route paths from \`.design-agent/working-brief.md\`.
- [ ] Final verdict uses PASS, PASS WITH RISKS, or FAIL.
`;
}

function buildFinalReportTemplate({ promptMode }) {
  return `# Design Agent Final Report Template

Mode: ${promptMode}

Replace every line with real evidence from the target project.
Use target-relative paths in \`Files changed\`; \`design:target-audit\` verifies that those files exist inside the target project.
Keep \`Browser routes checked\` aligned with the route paths from \`.design-agent/working-brief.md\`.
Make \`State coverage checked\` cover the brief's \`Included states\`; only omit states that the brief explicitly marked as deferred.
\`Information architecture checked\` must name the route/screen map, navigation or app shell, main/context zones, and responsive/recovery behavior; generic \`checked\`, \`done\`, or component-only wording is not enough.
\`Interaction model checked\` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control; generic \`checked\`, \`done\`, or static component wording is not enough.
\`Copy/status language checked\` must name status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label; generic \`checked\`, \`done\`, \`success\`, or \`ready\` wording is not enough.
\`Decision/review cockpit checked\` must name decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path; generic \`checked\`, \`done\`, or component-only wording is not enough.
\`Visual system checked\` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic \`checked\`, \`done\`, or \`looks good\` wording is not enough.
\`Component state evidence checked\` must name the changed components/controls, the states checked, and the evidence type such as screenshot, browser inspection, keyboard/focus check, responsive viewport, command output, or manual artifact.
\`Product read\`, \`Object model checked\`, \`Visual system checked\`, \`Workflow improved\`, and \`Implementation slice contract\` must reference the working brief's route/screen, primary object, product object model, visual system contract, workflow/actions, data/fixture truth, and states; generic \`done\`, \`improved\`, or component-only wording keeps \`design:target-audit\` below final handoff readiness.
Before coding, the working brief must name the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
Use a numeric \`Rubric score\`; \`PASS\` requires 26+/30, and \`PASS WITH RISKS\` requires 18+/30 or higher.
\`Five-second test\` must name object, state, next action, recovery, and evidence. \`Mediocrity risks fixed\` and \`Product-specific details\` must reference the working brief; generic \`passed\`, \`checked\`, \`improved\`, or \`looks good\` text keeps \`design:target-audit\` below final handoff readiness.
If using \`MANUAL_BROWSER_INSPECTION\`, the notes artifact must name route/screen, viewport or pixel size, and visual/layout/focus/overlap check.
For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, \`Operational pattern checked\` must name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.

## Verdict

PASS / PASS WITH RISKS / FAIL:

## Work Summary

- Surface classified:
- Product read:
- Runbook phases used:
- Brief/blueprint used:
- Screen recipe/state specs:
- Workflow improved:
- Files changed:

## Product UI Checks

- Information architecture checked:
- Interaction model checked:
- Copy/status language checked:
- Decision/review cockpit checked:
- Object model checked:
- Visual system checked:
- Trusted vertical checked:
- AI source-of-truth/false-state risks checked:
- Top-design benchmark checked:
- Five-second test:
- Mediocrity risks fixed:
- Product-specific details:
- Operational pattern checked:
- Component blueprints checked:
- Component/source choices:
- State coverage checked:
- Component state evidence checked:
- Implementation slice checked:
- Implementation slice contract:
- Motion/proof/data risks handled:

## Evidence

- Commands run:
- Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK:
- Command evidence artifacts:
- Browser routes checked:
- Screenshots/browser checks:
- Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK:
- Accessibility checked:
- Responsive checked:
- Evidence artifacts:

## Quality Result

- Rubric score:
- Blockers fixed:
- Remaining risks:
- Deferred work:
`;
}

function buildTargetAgentRulesBlock({ promptMode, targetPath, knowledgeBasePath, autoSelection }) {
  const reason = autoSelection ? autoSelection.reason : "explicit mode selected";
  return `${agentRulesBegin}
# Design Agent Packet

This project has a generated design-agent packet from:

\`\`\`text
${knowledgeBasePath}
\`\`\`

Mode: ${promptMode}
Reason: ${reason}
Target: ${targetPath}

Before product UI, dashboard, editor, AI design studio, canvas, website, motion, 3D/WebGL, component, or visual QA work:

1. Read \`DESIGN_AGENT_HANDOFF.md\`.
2. Read \`.design-agent/README.md\` and \`.design-agent/prompt.txt\`.
3. Fill \`.design-agent/working-brief.md\` before coding.
4. Keep \`.design-agent/acceptance-checklist.md\` open during implementation.
5. Use \`.design-agent/final-report-template.md\` before final handoff.
6. From the knowledge-base repository, verify packet integrity with:

\`\`\`bash
npm run design:packet-check -- "${targetPath}"
\`\`\`

Then verify the working phase when relevant:

\`\`\`bash
npm run design:brief-check -- "${targetPath}"
npm run design:final-check -- "${targetPath}"
npm run design:target-audit -- "${targetPath}" --write
\`\`\`

Do not force landing-page structure onto dashboards, admin panels, editors, AI workbenches, data tools, or app surfaces. For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, start with \`AI_DESIGN_APP_TRUSTED_VERTICAL.md\` so source-of-truth objects, false-state bans, proof/evidence, decisions, after-state, and recovery are explicit. Work through \`PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md\`: route/screen, primary object, product object model, data truth, states, actions, responsive behavior, commands, screenshots/browser evidence, and risks. Do not claim completion without real commands, browser/screenshot checks, or an explicit remaining-risk note.
\`design:brief-check\` must pass before coding; generic product fields such as \`improve UI\`, \`make better\`, \`use app\`, \`done\`, or core-field \`N/A\` are not accepted.
The brief must also name the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan before coding.
For AI design studios/canvas/proposal workflows, \`design:brief-check\` also requires concrete AI Design App Invariants: external AI is proposal-only, preview/diff is visible, verification is visible, human approval is visible, transaction/ledger evidence is visible, agent connection/scopes are visible, comment-to-task bridge is visible, pending proposal/approval bridge is visible, failure/recovery handling is visible, and export/reopen recovery exists.
When filling \`Files changed\`, list target-relative paths that exist inside this project; the design audit treats missing paths or paths outside the project as not ready for final handoff.
When filling \`Browser routes checked\`, include the route paths from \`.design-agent/working-brief.md\`; checking a different route is not final evidence.
When filling \`Information architecture checked\`, name the route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior; generic \`checked\`, \`done\`, or component-only wording is not enough.
When filling \`Interaction model checked\`, name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control; generic \`checked\`, \`done\`, or static component wording is not enough.
When filling \`Copy/status language checked\`, name status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label; generic \`checked\`, \`done\`, \`success\`, or \`ready\` wording is not enough.
When filling \`Decision/review cockpit checked\`, name decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path; generic \`checked\`, \`done\`, or component-only wording is not enough.
When filling \`Visual system checked\`, name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic \`checked\`, \`done\`, or \`looks good\` wording is not enough.
When filling \`State coverage checked\`, include the brief's included states and name any deferred states honestly.
When filling \`Component state evidence checked\`, name the changed components/controls, concrete states checked, and the screenshot/browser/manual/keyboard/responsive evidence used; generic \`checked\`, \`done\`, or component-only wording is not enough.
When filling \`Product read\`, \`Object model checked\`, \`Visual system checked\`, \`Workflow improved\`, and \`Implementation slice contract\`, preserve the same route/screen, primary object, product object model, visual system contract, workflow/actions, data/source truth, and states named in \`.design-agent/working-brief.md\`.
When filling \`Five-second test\`, name object, state, next action, recovery, and evidence. When filling \`Mediocrity risks fixed\` and \`Product-specific details\`, reference the working brief rather than writing generic \`passed\`, \`checked\`, or \`improved\`.
When filling \`Operational pattern checked\` for an AI design app, name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.
When using \`MANUAL_BROWSER_INSPECTION\`, write notes that name route/screen, viewport or pixel size, and visual/layout/focus/overlap check.
${agentRulesEnd}`;
}

function readManifest() {
  if (!existsSync(manifestPath)) {
    throw new Error(`Missing design workbench manifest: ${manifestPath}`);
  }

  return JSON.parse(readFileSync(manifestPath, "utf8"));
}

function writePacket({ prompt, promptMode, targetPath, knowledgeBasePath, autoSelection, handoffPath }) {
  const manifest = readManifest();
  const packetDir = path.join(targetPath, ".design-agent");
  const generatedAt = new Date().toISOString();
  mkdirSync(packetDir, { recursive: true });

  const packetManifest = {
    version: 1,
    generatedAt,
    promptMode,
    autoReason: autoSelection?.reason ?? null,
    knowledgeBasePath,
    targetPath,
    handoffPath,
    sourceManifestPath: manifestPath,
    sourceManifest: manifest,
  };

  const files = [
    {
      path: path.join(packetDir, "README.md"),
      content: buildPackReadme({ promptMode, targetPath, knowledgeBasePath, autoSelection }),
    },
    {
      path: path.join(packetDir, "prompt.txt"),
      content: `${prompt}\n`,
    },
    {
      path: path.join(packetDir, "working-brief.md"),
      content: buildWorkingBrief({ promptMode, targetPath, knowledgeBasePath }),
    },
    {
      path: path.join(packetDir, "manifest.json"),
      content: `${JSON.stringify(packetManifest, null, 2)}\n`,
    },
    {
      path: path.join(packetDir, "acceptance-checklist.md"),
      content: buildAcceptanceChecklist({ promptMode }),
    },
    {
      path: path.join(packetDir, "final-report-template.md"),
      content: buildFinalReportTemplate({ promptMode }),
    },
    {
      path: path.join(packetDir, "AGENTS_SNIPPET.md"),
      content: `${buildTargetAgentRulesBlock({
        promptMode,
        targetPath,
        knowledgeBasePath,
        autoSelection,
      })}\n`,
    },
  ];

  for (const file of files) {
    writeFileSync(file.path, file.content, "utf8");
  }

  return files.map((file) => file.path);
}

function installTargetAgentRules({ targetPath, promptMode, knowledgeBasePath, autoSelection }) {
  const agentsPath = path.join(targetPath, "AGENTS.md");
  const block = buildTargetAgentRulesBlock({ promptMode, targetPath, knowledgeBasePath, autoSelection });
  const existing = existsSync(agentsPath) ? readFileSync(agentsPath, "utf8") : "";
  const blockPattern = new RegExp(`${agentRulesBegin}[\\s\\S]*?${agentRulesEnd}`, "m");
  const next = blockPattern.test(existing)
    ? existing.replace(blockPattern, block)
    : `${existing.trimEnd()}${existing.trim() ? "\n\n" : ""}${block}\n`;

  writeFileSync(agentsPath, next, "utf8");
  return agentsPath;
}

const { help, mode, targetPath, write, pack, installAgentRules, outputPath } = parseArgs(process.argv.slice(2));
if (help) {
  usage();
  process.exit(0);
}

if (!existsSync(promptsPath)) {
  console.error(`Missing prompt source: ${promptsPath}`);
  process.exit(1);
}

let normalizedMode;
try {
  normalizedMode = normalizeMode(mode);
} catch (error) {
  console.error(error.message);
  usage();
  process.exit(1);
}

const resolvedTarget = targetPath || "<TARGET_PROJECT_PATH>";
const knowledgeBasePath = repoRoot;
const markdown = readFileSync(promptsPath, "utf8");

try {
  const autoSelection = normalizedMode === "auto" ? chooseAutoMode(resolvedTarget) : null;
  const promptMode = autoSelection?.mode ?? normalizedMode;
  const prompt = extractPrompt(markdown, modes[promptMode])
    .replaceAll("C:\\Users\\se-20\\OneDrive\\Рабочий стол\\ai-website-cloner-template", knowledgeBasePath)
    .replaceAll("<TARGET_PROJECT_PATH>", resolvedTarget)
    .replaceAll("<FORGESTUDIO_PROJECT_PATH>", resolvedTarget);

  if (!prompt.includes(requiredPromptAnchor)) {
    throw new Error(`Generated prompt is missing required anchor: ${requiredPromptAnchor}`);
  }

  if (autoSelection) {
    console.log(`Auto-selected design handoff mode: ${promptMode}`);
    console.log(`Reason: ${autoSelection.reason}`);
    console.log("");
  }

  let handoffPath = "";
  if (write) {
    handoffPath = resolveOutputPath(resolvedTarget, outputPath);
    mkdirSync(path.dirname(handoffPath), { recursive: true });
    writeFileSync(
      handoffPath,
      buildHandoffMarkdown({
        prompt,
        promptMode,
        targetPath: resolvedTarget,
        knowledgeBasePath,
        autoSelection,
      }),
      "utf8",
    );
    console.log(`Wrote design handoff: ${handoffPath}`);
    console.log("");
  }

  if (pack) {
    if (!existsSync(resolvedTarget) || !statSync(resolvedTarget).isDirectory()) {
      throw new Error(`Cannot use --pack because target path is not a directory: ${resolvedTarget}`);
    }

    const packetFiles = writePacket({
      prompt,
      promptMode,
      targetPath: resolvedTarget,
      knowledgeBasePath,
      autoSelection,
      handoffPath,
    });

    console.log("Wrote design agent packet:");
    for (const file of packetFiles) {
      console.log(`- ${file}`);
    }
    console.log("");
  }

  if (installAgentRules) {
    if (!existsSync(resolvedTarget) || !statSync(resolvedTarget).isDirectory()) {
      throw new Error(`Cannot use --install-agent-rules because target path is not a directory: ${resolvedTarget}`);
    }

    const agentsPath = installTargetAgentRules({
      targetPath: resolvedTarget,
      promptMode,
      knowledgeBasePath,
      autoSelection,
    });
    console.log(`Installed design agent rules: ${agentsPath}`);
    console.log("");
  }

  console.log(prompt);
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

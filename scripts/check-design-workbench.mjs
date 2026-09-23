#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";

const repoRoot = process.cwd();

const requiredFiles = [
  "AGENTS.md",
  "README.md",
  "package.json",
  "scripts/print-design-handoff.mjs",
  "scripts/check-design-packet.mjs",
  "scripts/check-design-agent-work.mjs",
  "scripts/audit-design-target.mjs",
  "docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json",
  "docs/design-workbench/AGENT_START_HERE.md",
  "docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md",
  "docs/design-workbench/FORGESTUDIO_CONTEXT.md",
  "docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md",
  "docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md",
  "docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md",
  "docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md",
  "docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md",
  "docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md",
  "docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md",
  "docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md",
  "docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md",
  "docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md",
  "docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md",
  "docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md",
  "docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md",
  "docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md",
  "docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
  "docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md",
  "docs/design-workbench/COMPONENT_STATE_SPEC.md",
  "docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md",
  "docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md",
  "docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
  "docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md",
  "docs/design-workbench/PRODUCT_UI_VISUAL_QA.md",
  "docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md",
  "docs/design-workbench/AGENT_REPORT_EXAMPLES.md",
  "docs/design-workbench/AGENT_PROMPTS.md",
];

const productSkills = [
  "product-ui-design-orchestrator",
  "product-design-taste",
  "design-ai-workbench-screens",
  "product-ui-component-sourcing",
  "product-ui-visual-qa",
];

const localSkillRoots = [".codex/skills", ".agents/skills"];

const generatedRuleFiles = [
  ".github/copilot-instructions.md",
  ".clinerules",
  ".continue/rules/project.md",
  ".amazonq/rules/project.md",
];

const requiredAnchors = [
  {
    file: "AGENTS.md",
    patterns: [
      "design:brief-check",
      "product object model",
      "visual system contract",
      "closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan",
    ],
  },
  {
    file: "docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json",
    patterns: [
      "\"notLandingOnly\": true",
      "\"handoffModes\"",
      "\"product-ui-design-orchestrator\"",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "\"npm run design:handoff -- \\\"<target-project>\\\" --write\"",
      "\"npm run design:handoff -- \\\"<target-project>\\\" --pack\"",
      "\"npm run design:pack -- \\\"<target-project>\\\"\"",
      "\"npm run design:install-agent-rules -- \\\"<target-project>\\\"\"",
      "\"npm run design:packet-check -- \\\"<target-project>\\\"\"",
      "\"npm run design:brief-check -- \\\"<target-project>\\\"\"",
      "\"npm run design:final-check -- \\\"<target-project>\\\"\"",
      "\"npm run design:target-audit -- \\\"<target-project>\\\"\"",
      "\"npm run design:target-audit -- \\\"<target-project>\\\" --write\"",
      "\"packetFiles\"",
      "\".design-agent/working-brief.md\"",
      "\".design-agent/final-report-template.md\"",
      "\".design-agent/AGENTS_SNIPPET.md\"",
      "Working briefs must pass substance checks before coding",
      "product object model",
      "visual system contract",
      "closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan",
      "AI design app working briefs must fill AI Design App Invariants before coding",
      "agent connection/scopes",
      "comment-to-task bridge",
      "pending proposal/approval bridge",
      "failure/recovery handling",
      "AI design app final reports must prove the operational pattern",
      "Final implementation-slice reporting must preserve",
    ],
  },
  {
    file: "docs/design-workbench/FORGESTUDIO_CONTEXT.md",
    patterns: [
      "ForgeStudio is a local-first, AI-auditable design engineering studio",
      "Dev Repo Anatomy",
      "proposal -> preview/diff -> verification -> human approval -> `DesignTransaction` -> ledger/history",
    ],
  },
  {
    file: "docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md",
    patterns: [
      "ForgeStudio `dev` was inspected on 2026-07-04",
      "Trusted Vertical",
      "Source-Of-Truth Objects",
      "False-State Ban",
      "Implementation Slice Rule",
      "Beauty here is trust made visible",
    ],
  },
  {
    file: "docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
    patterns: [
      "A slice is not a component",
      "Slice Contract",
      "Minimum Coherent Slice",
      "Output Contract",
    ],
  },
  {
    file: "docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md",
    patterns: [
      "Do not force landing-page structure onto product UI",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "PASS WITH RISKS",
      "Project command evidence",
      "Command evidence artifacts",
      "Visual evidence verdict",
      "real changed files",
    ],
  },
  {
    file: "docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md",
    patterns: [
      "Implementation slice contract",
      "Top-design benchmark",
      "No landing bias",
      "Visual evidence",
      "Changed-file evidence",
      "Route consistency",
      "State consistency",
      "Rubric threshold",
      "Evidence status",
      "Screen/slice selection before coding",
      "Product object model",
      "Visual system contract",
    ],
  },
  {
    file: "docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
    patterns: [
      "Top-Tier Bar",
      "Five-Second Test",
      "AI Design Studio Benchmark",
      "Top-Design Anti-Patterns",
      "Final Benchmark Contract",
    ],
  },
  {
    file: "docs/design-workbench/AGENT_PROMPTS.md",
    patterns: [
      "auto",
      "--write",
      "Universal Product UI Prompt",
      "ForgeStudio-Specific Prompt",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "product object model",
      "visual system contract",
      "local files to inspect/change",
      "component state plan",
    ],
  },
  {
    file: "package.json",
    patterns: [
      "\"design:check\"",
      "\"design:handoff\"",
      "\"design:pack\"",
      "\"design:install-agent-rules\"",
      "\"design:packet-check\"",
      "\"design:brief-check\"",
      "\"design:final-check\"",
      "\"design:target-audit\"",
    ],
  },
  {
    file: "scripts/print-design-handoff.mjs",
    patterns: [
      "Universal Product UI Prompt",
      "ForgeStudio-Specific Prompt",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "--pack",
      ".design-agent",
      "acceptance-checklist.md",
      "working-brief.md",
      "Trusted vertical segment",
      "Closest product surface blueprint",
      "Product object model",
      "Visual system contract",
      "Screen recipe/state specs",
      "Local files to inspect/change",
      "Component state plan",
      "Source-of-truth objects",
      "False-state risks",
      "AI Design App Invariants",
      "External AI is proposal-only until",
      "Agent connection/scopes visible",
      "Comment-to-task bridge visible",
      "Pending proposal/approval bridge visible",
      "Failure/recovery handling visible",
      "Trusted vertical checked",
      "Operational pattern checked",
      "Top-design target",
      "Five-second test",
      "Files changed",
      "Browser routes checked",
      "Information architecture checked",
      "Interaction model checked",
      "Copy/status language checked",
      "Decision/review cockpit checked",
      "State coverage checked",
      "Component state evidence checked",
      "Project command evidence",
      "Visual evidence verdict",
      "final-report-template.md",
      "AGENTS_SNIPPET.md",
      "--install-agent-rules",
      "design:packet-check",
      "design:brief-check",
      "design:final-check",
      "design:target-audit",
    ],
  },
  {
    file: "scripts/check-design-packet.mjs",
    patterns: [
      "Design packet check passed.",
      "DESIGN_AGENT_HANDOFF.md",
      ".design-agent/working-brief.md",
      ".design-agent/final-report-template.md",
      ".design-agent/AGENTS_SNIPPET.md",
      "BEGIN:design-agent-packet",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "## Trusted Vertical",
      "Trusted vertical segment:",
      "Product object model",
      "Object model checked",
      "## AI Design App Invariants",
      "External AI is proposal-only until:",
      "Agent connection/scopes visible:",
      "Comment-to-task bridge visible:",
      "Pending proposal/approval bridge visible:",
      "Failure/recovery handling visible:",
      "## Top Design Benchmark",
      "Top-design target:",
      "Top-design benchmark checked:",
      "Trusted vertical checked:",
      "Operational pattern checked:",
      "Information architecture checked:",
      "Interaction model checked:",
      "Copy/status language checked:",
      "Decision/review cockpit checked:",
      "Component state evidence checked:",
      "Files changed:",
      "Project command evidence:",
      "Command evidence artifacts:",
      "Visual evidence verdict:",
      "notLandingOnly",
      "packetCheck",
    ],
  },
  {
    file: "scripts/check-design-agent-work.mjs",
    patterns: [
      "Design agent work check passed for phase",
      "working-brief.md",
      "final-report-template.md",
      "Implementation Slice Contract",
      "Trusted vertical segment",
      "Trusted vertical checked",
      "Top-design benchmark checked",
      "Five-second test",
      "PASS / PASS WITH RISKS / FAIL",
      "Files changed",
      "Project command evidence",
      "Command evidence artifacts",
      "Visual evidence verdict",
      "Evidence artifacts",
      "REAL_PROJECT_COMMANDS",
      "REAL_BROWSER_SCREENSHOTS",
      "requireSubstantiveBrief",
      "AI design app invariant signal",
      "final AI design app operational signal",
      "agent connection/scopes",
      "comment-to-task bridge",
      "pending approval bridge",
      "failure/recovery handling",
      "weak product brief field",
      "product brief substance signal",
      "object model/lifecycle",
      "visual system/tokens",
      "Product object model",
      "Object model checked",
      "Visual system contract",
      "Visual system checked",
      "visualSystemEvidenceSignalChecks",
      "Information architecture checked",
      "informationArchitectureSignalChecks",
      "Interaction model checked",
      "interactionModelSignalChecks",
      "Copy/status language checked",
      "copyStatusLanguageSignalChecks",
      "Decision/review cockpit checked",
      "decisionReviewCockpitSignalChecks",
      "Component state evidence checked",
      "componentStateEvidenceSignalChecks",
      "screen selection",
      "local implementation target",
      "Closest product surface blueprint",
      "Component state plan",
      "--phase",
    ],
  },
  {
    file: "scripts/audit-design-target.mjs",
    patterns: [
      "Design Target Audit",
      "NOT READY FOR CODING",
      "READY FOR CODING, NOT READY FOR FINAL HANDOFF",
      "READY FOR FINAL HANDOFF",
      "readiness-report.md",
      "Trusted vertical segment",
      "Trusted vertical checked",
      "Top-design benchmark checked",
      "Five-second test",
      "Final evidence ready",
      "Weak working brief fields",
      "Working brief missing substance signals",
      "object model/lifecycle",
      "visual system/tokens",
      "Product object model",
      "Object model checked",
      "Visual system contract",
      "Visual system checked",
      "Visual system evidence",
      "visual system missing signals",
      "screen selection",
      "local implementation target",
      "Closest product surface blueprint",
      "Component state plan",
      "Information architecture evidence",
      "information architecture missing signals",
      "Interaction model evidence",
      "interaction model missing signals",
      "Copy/status language evidence",
      "copy/status language missing signals",
      "Decision/review cockpit evidence",
      "decision/review cockpit missing signals",
      "Visual system evidence",
      "visual system missing signals",
      "Component state evidence",
      "component state evidence missing signals",
      "AI design app detected",
      "Weak AI design app invariant fields",
      "AI design app final missing operational signals",
      "agent connection/scopes",
      "comment-to-task bridge",
      "pending approval bridge",
      "failure/recovery handling",
      "inspectBriefSubstance",
      "Project command evidence",
      "Command artifact files found",
      "Changed files found",
      "missing changed files",
      "final report lists no checkable changed file paths",
      "Brief route paths",
      "Final checked route paths",
      "brief routes not checked in final report",
      "Brief included states",
      "Final checked states",
      "brief included states not checked in final report",
      "Rubric normalized score",
      "rubric score is not numeric",
      "PASS verdict requires rubric score 26+/30",
      "rubric score below PASS WITH RISKS threshold",
      "Valid command artifact files",
      "real project command evidence has no valid command log artifact file",
      "Visual evidence verdict",
      "Evidence artifact files found",
      "Evidence artifact files missing",
      "Valid visual artifact files",
      "Invalid visual artifact files",
      "isSubstantiveManualInspectionText",
      "route/screen, viewport/size, and visual/layout/focus/overlap check",
      "Valid manual inspection artifact files",
      "Invalid manual inspection artifact files",
      "manual browser inspection has no valid notes artifact file",
      "invalid visual artifact files",
      "five-second test missing signals",
      "weak top-design fields",
      "weak implementation-slice fields",
      "implementation slice missing signals",
      "implementation slice does not reference brief primary object",
      "implementation slice does not reference brief workflow/actions",
      "implementation slice does not reference brief data/source truth",
      "mediocrity risks fixed do not reference brief risks",
      "product-specific details do not reference brief details",
      "Five-second test missing signals",
      "Weak top-design fields",
      "Implementation slice missing signals",
      "Weak implementation-slice fields",
      "evidenceWeaknesses",
      "inspectFinalAiDesignAppEvidence",
      "design:target-audit",
    ],
  },
  {
    file: ".codex/skills/product-ui-design-orchestrator/SKILL.md",
    patterns: [
      "DESIGN_WORKBENCH_MANIFEST.json",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "npm run design:pack -- \"<target-project>\"",
      "npm run design:install-agent-rules -- \"<target-project>\"",
      "npm run design:packet-check -- \"<target-project>\"",
      "npm run design:brief-check -- \"<target-project>\"",
      "product substance, not only placeholders",
      "AI Design App Invariants",
      "agent connection/scopes",
      "comment-to-task bridge",
      "pending proposal/approval bridge",
      "failure/recovery handling",
      "Local files to inspect/change",
      "Component state plan",
      "Operational pattern checked",
      "npm run design:final-check -- \"<target-project>\"",
      "npm run design:target-audit -- \"<target-project>\"",
      ".design-agent/working-brief.md",
      ".design-agent/acceptance-checklist.md",
      ".design-agent/AGENTS_SNIPPET.md",
      ".design-agent/final-report-template.md",
    ],
  },
  {
    file: ".codex/skills/product-ui-design-orchestrator/references/universal-product-ui-playbook.md",
    patterns: [
      "Implementation slice planning",
      "Implementation-slice report integrity",
      "Brief readiness",
      "product object model",
      "visual system contract",
      "closest product surface blueprint",
      "component state plan",
      "AI design app invariants",
      "agent connection/scopes",
      "comment-to-task bridge",
      "pending proposal/approval bridge",
      "failure/recovery handling",
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "ForgeStudio-Inspired Product Principles",
      "Isolated visual component polish passed off as a product slice",
    ],
  },
  {
    file: ".codex/skills/product-design-taste/references/product-design-taste-playbook.md",
    patterns: [
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "What slice is being shipped?",
      "The implementation slice contract is named",
      "ForgeStudio-Like Taste",
    ],
  },
  {
    file: ".codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md",
    patterns: [
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "Before coding, turn the chosen slice into a contract",
      "Implementation slice contract is explicit",
      "open folder -> scan report -> page imported",
    ],
  },
  {
    file: ".codex/skills/product-ui-visual-qa/references/visual-qa-checklist.md",
    patterns: [
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "Implementation slice matches `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`",
      "Project command evidence",
      "Visual evidence verdict",
      "REAL_PROJECT_COMMANDS",
      "Files changed",
      "Browser routes checked",
      "State coverage checked",
      "Copy/status language checked",
      "Decision/review cockpit checked",
      "Component state evidence checked",
      "PASS WITH RISKS",
      "26+/30",
      "command-log artifacts",
      "PNG/JPEG/WebP/GIF/MP4/WebM",
      "MANUAL_BROWSER_INSPECTION",
      "route/screen, viewport or pixel size",
      "valid `.json`",
      "coherent implementation slice",
      "implementation-slice evidence",
      "object, state, next action, recovery, and evidence",
      "Operational pattern checked",
      "proposal-only, preview/diff, verification, human approval",
      "Use `FAIL` if P0 blockers remain",
    ],
  },
  {
    file: ".codex/skills/product-ui-component-sourcing/references/component-sourcing-matrix.md",
    patterns: [
      "AI_DESIGN_APP_TRUSTED_VERTICAL.md",
      "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
      "implementation slice",
      "The component belongs to a coherent implementation slice",
      "ForgeStudio-Like Component Needs",
    ],
  },
];

const skillAnchors = [
  "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
  "PRODUCT_UI_INFORMATION_ARCHITECTURE.md",
  "PRODUCT_UI_INTERACTION_MODEL.md",
  "PRODUCT_UI_COPY_STATUS_LANGUAGE.md",
  "PRODUCT_UI_DECISION_REVIEW_COCKPIT.md",
  "PRODUCT_UI_QUALITY_GATE.md",
  "PRODUCT_UI_TOP_DESIGN_BENCHMARK.md",
];

const promptSections = [
  "Handoff Packet Prompt",
  "Universal Product UI Prompt",
  "ForgeStudio-Specific Prompt",
  "Dashboard Upgrade Prompt",
  "New UI From Scratch Prompt",
  "Final QA Prompt",
];

const failures = [];
const warnings = [];

function fullPath(relativePath) {
  return path.join(repoRoot, relativePath);
}

function readRelative(relativePath) {
  return readFileSync(fullPath(relativePath), "utf8");
}

function hasFile(relativePath) {
  return existsSync(fullPath(relativePath));
}

function toPosix(relativePath) {
  return relativePath.split(path.sep).join("/");
}

function listFilesRecursive(rootPath) {
  const files = [];

  function visit(currentPath, relativePrefix) {
    for (const entry of readdirSync(currentPath, { withFileTypes: true })) {
      const entryPath = path.join(currentPath, entry.name);
      const relativePath = relativePrefix ? path.join(relativePrefix, entry.name) : entry.name;
      if (entry.isDirectory()) {
        visit(entryPath, relativePath);
      } else if (entry.isFile()) {
        files.push(toPosix(relativePath));
      }
    }
  }

  visit(rootPath, "");
  return files.sort();
}

function fileHash(filePath) {
  return createHash("sha256").update(readFileSync(filePath)).digest("hex");
}

function extractPromptSection(markdown, heading) {
  const headingLine = `## ${heading}`;
  const headingIndex = markdown.indexOf(headingLine);
  if (headingIndex === -1) {
    fail(`Prompt section not found: ${heading}`);
    return "";
  }

  const sectionStart = markdown.indexOf("\n", headingIndex);
  const sectionBodyStart = sectionStart === -1 ? markdown.length : sectionStart + 1;
  const rest = markdown.slice(sectionBodyStart);
  const nextHeadingMatch = rest.match(/^## /m);
  const section = nextHeadingMatch ? rest.slice(0, nextHeadingMatch.index) : rest;
  const codeMatch = section.match(/```text\s*([\s\S]*?)```/);
  if (!codeMatch) {
    fail(`Prompt code block not found: ${heading}`);
    return "";
  }

  return codeMatch[1];
}

function compareSkillTrees(sourceRoot, targetRoot, skill, label) {
  const sourceDir = path.join(sourceRoot, skill);
  const targetDir = path.join(targetRoot, skill);

  if (!existsSync(sourceDir)) {
    fail(`Missing source skill directory: ${sourceDir}`);
    return;
  }

  if (!existsSync(targetDir)) {
    fail(`Missing ${label} skill directory: ${targetDir}`);
    return;
  }

  const sourceFiles = listFilesRecursive(sourceDir);
  const targetFiles = listFilesRecursive(targetDir);
  const sourceSet = new Set(sourceFiles);
  const targetSet = new Set(targetFiles);

  for (const relativeFile of sourceFiles) {
    if (!targetSet.has(relativeFile)) {
      fail(`Missing ${label} skill file for ${skill}: ${relativeFile}`);
      continue;
    }

    const sourceFile = path.join(sourceDir, ...relativeFile.split("/"));
    const targetFile = path.join(targetDir, ...relativeFile.split("/"));
    if (fileHash(sourceFile) !== fileHash(targetFile)) {
      fail(`Stale ${label} skill file for ${skill}: ${relativeFile}`);
    }
  }

  for (const relativeFile of targetFiles) {
    if (!sourceSet.has(relativeFile)) {
      fail(`Extra ${label} skill file for ${skill}: ${relativeFile}`);
    }
  }
}

function fail(message) {
  failures.push(message);
}

function warn(message) {
  warnings.push(message);
}

for (const file of requiredFiles) {
  if (!hasFile(file)) {
    fail(`Missing required file: ${file}`);
  }
}

for (const { file, patterns } of requiredAnchors) {
  if (!hasFile(file)) {
    fail(`Missing anchored file: ${file}`);
    continue;
  }

  const text = readRelative(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) {
      fail(`Missing anchor in ${file}: ${pattern}`);
    }
  }
}

if (hasFile("docs/design-workbench/AGENT_PROMPTS.md")) {
  const prompts = readRelative("docs/design-workbench/AGENT_PROMPTS.md");
  for (const section of promptSections) {
    const prompt = extractPromptSection(prompts, section);
    if (prompt && !prompt.includes("PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md")) {
      fail(`Prompt section missing implementation slice contract: ${section}`);
    }
  }
}

if (hasFile("docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json")) {
  try {
    const manifest = JSON.parse(readRelative("docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json"));
    const manifestPaths = [
      ...(Array.isArray(manifest.firstRead) ? manifest.firstRead : []),
      ...(Array.isArray(manifest.coreContracts) ? manifest.coreContracts : []),
      ...(Array.isArray(manifest.skills) ? manifest.skills.map((skill) => skill.path) : []),
    ];

    if (!manifest.notLandingOnly) {
      fail("Manifest must explicitly set notLandingOnly to true.");
    }

    for (const mode of ["auto", "universal", "forgestudio", "dashboard", "scratch", "qa"]) {
      if (!manifest.handoffModes?.[mode]) {
        fail(`Manifest missing handoff mode: ${mode}`);
      }
    }

    for (const packetFile of [
      "DESIGN_AGENT_HANDOFF.md",
      ".design-agent/README.md",
      ".design-agent/prompt.txt",
      ".design-agent/working-brief.md",
      ".design-agent/manifest.json",
      ".design-agent/acceptance-checklist.md",
      ".design-agent/final-report-template.md",
      ".design-agent/AGENTS_SNIPPET.md",
    ]) {
      if (!manifest.packetFiles?.includes(packetFile)) {
        fail(`Manifest missing packet file: ${packetFile}`);
      }
    }

    for (const manifestPath of manifestPaths) {
      if (!hasFile(manifestPath)) {
        fail(`Manifest references missing file: ${manifestPath}`);
      }
    }
  } catch (error) {
    fail(`Manifest JSON is invalid: ${error.message}`);
  }
}

for (const ruleFile of generatedRuleFiles) {
  if (!hasFile(ruleFile)) {
    fail(`Missing generated agent rule: ${ruleFile}`);
    continue;
  }

  const text = readRelative(ruleFile);
  if (!text.includes("PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md")) {
    fail(`Generated agent rule is stale: ${ruleFile}`);
  }
  if (!text.includes("product object model")) {
    fail(`Generated agent rule is missing product object model gate: ${ruleFile}`);
  }
  if (!text.includes("visual system contract")) {
    fail(`Generated agent rule is missing visual system contract gate: ${ruleFile}`);
  }
  if (!text.includes("closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan")) {
    fail(`Generated agent rule is missing screen/slice selection gate: ${ruleFile}`);
  }
}

for (const skillRoot of localSkillRoots) {
  for (const skill of productSkills) {
    const skillFile = `${skillRoot}/${skill}/SKILL.md`;
    if (!hasFile(skillFile)) {
      fail(`Missing product skill: ${skillFile}`);
      continue;
    }

    const text = readRelative(skillFile);
    const anchors = skill === "design-ai-workbench-screens"
      ? [...skillAnchors, "AI_DESIGN_APP_TRUSTED_VERTICAL.md", "AI_WORKBENCH_IMPLEMENTATION_SLICES.md"]
      : [...skillAnchors, "AI_DESIGN_APP_TRUSTED_VERTICAL.md"];

    for (const anchor of anchors) {
      if (!text.includes(anchor)) {
        fail(`Missing skill anchor in ${skillFile}: ${anchor}`);
      }
    }

    for (const anchor of [
      ".design-agent/working-brief.md",
      ".design-agent/final-report-template.md",
      "npm run design:brief-check -- \"<target-project>\"",
      "npm run design:final-check -- \"<target-project>\"",
      "npm run design:target-audit -- \"<target-project>\" --write",
    ]) {
      if (!text.includes(anchor)) {
        fail(`Missing packet discipline anchor in ${skillFile}: ${anchor}`);
      }
    }
  }
}

const globalSkillRoot = path.join(os.homedir(), ".codex", "skills");
if (existsSync(globalSkillRoot)) {
  for (const skill of productSkills) {
    const globalSkillFile = path.join(globalSkillRoot, skill, "SKILL.md");
    if (!existsSync(globalSkillFile)) {
      fail(`Missing global Codex skill: ${globalSkillFile}`);
      continue;
    }

    const text = readFileSync(globalSkillFile, "utf8");
    if (!text.includes("PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md")) {
      fail(`Global Codex skill is stale: ${globalSkillFile}`);
    }
    if (!text.includes("npm run design:target-audit -- \"<target-project>\" --write")) {
      fail(`Global Codex skill missing packet discipline: ${globalSkillFile}`);
    }
    if (!text.includes("AI_DESIGN_APP_TRUSTED_VERTICAL.md")) {
      fail(`Global Codex skill missing trusted vertical: ${globalSkillFile}`);
    }
    if (!text.includes("PRODUCT_UI_TOP_DESIGN_BENCHMARK.md")) {
      fail(`Global Codex skill missing top-design benchmark: ${globalSkillFile}`);
    }
  }

  for (const skill of productSkills) {
    compareSkillTrees(fullPath(".codex/skills"), fullPath(".agents/skills"), skill, ".agents");
    compareSkillTrees(fullPath(".codex/skills"), globalSkillRoot, skill, "global Codex");
  }
} else {
  warn(`Global Codex skill root not found, skipped: ${globalSkillRoot}`);
}

if (warnings.length > 0) {
  console.warn("Design workbench warnings:");
  for (const message of warnings) {
    console.warn(`- ${message}`);
  }
}

if (failures.length > 0) {
  console.error("Design workbench check failed:");
  for (const message of failures) {
    console.error(`- ${message}`);
  }
  process.exit(1);
}

console.log("Design workbench check passed.");

#!/usr/bin/env node

import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

const requiredFiles = [
  "DESIGN_AGENT_HANDOFF.md",
  ".design-agent/README.md",
  ".design-agent/prompt.txt",
  ".design-agent/working-brief.md",
  ".design-agent/manifest.json",
  ".design-agent/acceptance-checklist.md",
  ".design-agent/final-report-template.md",
  ".design-agent/AGENTS_SNIPPET.md",
];

const requiredAnchors = [
  {
    file: "DESIGN_AGENT_HANDOFF.md",
    patterns: [
      "# Design Agent Handoff",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "## Prompt",
    ],
  },
  {
    file: ".design-agent/README.md",
    patterns: [
      "# Design Agent Packet",
      "working-brief.md",
      "acceptance-checklist.md",
      "final-report-template.md",
    ],
  },
  {
    file: ".design-agent/prompt.txt",
    patterns: [
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md",
      "PRODUCT_UI_REVIEW_RUBRIC",
      "VISUAL_QA_EVIDENCE_PLAYBOOK",
    ],
  },
  {
    file: ".design-agent/working-brief.md",
    patterns: [
      "# Design Agent Working Brief",
      "## Surface Classification",
      "Closest product surface blueprint:",
      "## Product Read",
      "Product object model:",
      "Visual system contract:",
      "## Implementation Slice Contract",
      "Screen recipe/state specs:",
      "Local files to inspect/change:",
      "Component state plan:",
      "## Decision Or Review Cockpit",
      "## Trusted Vertical",
      "Trusted vertical segment:",
      "Source-of-truth objects:",
      "False-state risks:",
      "## Top Design Benchmark",
      "Top-design target:",
      "Five-second test target:",
      "## AI Design App Invariants",
      "External AI is proposal-only until:",
      "Preview/diff visible:",
      "Transaction/ledger evidence visible:",
      "Agent connection/scopes visible:",
      "Comment-to-task bridge visible:",
      "Pending proposal/approval bridge visible:",
      "Failure/recovery handling visible:",
      "## Verification Plan",
    ],
  },
  {
    file: ".design-agent/acceptance-checklist.md",
    patterns: [
      "# Design Agent Acceptance Checklist",
      ".design-agent/working-brief.md",
      "## Before Coding",
      "trusted vertical segment",
      "AI Design App Invariants",
      "Top-design benchmark target",
      "Product object model",
      "Visual system contract",
      "Screen recipe/state specs chosen before coding",
      "Local files to inspect/change named before coding",
      "Component state plan",
      "Visual system checked",
      "Information architecture checked",
      "Interaction model checked",
      "Copy/status language checked",
      "Decision/review cockpit checked",
      "Component state evidence checked",
      "Real project command evidence",
      "Command evidence artifacts",
      "Visual evidence verdict",
      "## Final QA",
      "PASS, PASS WITH RISKS, or FAIL",
    ],
  },
  {
    file: ".design-agent/final-report-template.md",
    patterns: [
      "# Design Agent Final Report Template",
      "## Verdict",
      "## Product UI Checks",
      "Trusted vertical checked:",
      "AI source-of-truth/false-state risks checked:",
      "Operational pattern checked:",
      "Information architecture checked:",
      "Interaction model checked:",
      "Copy/status language checked:",
      "Decision/review cockpit checked:",
      "Object model checked:",
      "Visual system checked:",
      "Top-design benchmark checked:",
      "Five-second test:",
      "Files changed:",
      "## Evidence",
      "Commands run:",
      "Project command evidence:",
      "Command evidence artifacts:",
      "Screenshots/browser checks:",
      "Visual evidence verdict:",
      "State coverage checked:",
      "Component state evidence checked:",
      "Rubric score:",
      "Remaining risks:",
    ],
  },
  {
    file: ".design-agent/AGENTS_SNIPPET.md",
    patterns: [
      "<!-- BEGIN:design-agent-packet -->",
      "DESIGN_AGENT_HANDOFF.md",
      ".design-agent/working-brief.md",
      "npm run design:packet-check",
      "npm run design:brief-check",
      "npm run design:final-check",
      "PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT",
      "AI Design App Invariants",
      "closest product surface blueprint",
      "screen recipe/state specs",
      "Information architecture checked",
      "Interaction model checked",
      "Copy/status language checked",
      "Decision/review cockpit checked",
      "Visual system checked",
      "local files to inspect/change",
      "component state plan",
      "<!-- END:design-agent-packet -->",
    ],
  },
];

const failures = [];
const warnings = [];

function usage() {
  console.log("Usage: node scripts/check-design-packet.mjs <target-project-path>");
}

function fail(message) {
  failures.push(message);
}

function warn(message) {
  warnings.push(message);
}

function targetFile(targetRoot, relativePath) {
  return path.join(targetRoot, ...relativePath.split("/"));
}

function readTarget(targetRoot, relativePath) {
  return readFileSync(targetFile(targetRoot, relativePath), "utf8");
}

const targetPath = process.argv[2];
if (!targetPath || targetPath === "--help" || targetPath === "-h") {
  usage();
  process.exit(targetPath ? 0 : 1);
}

if (!existsSync(targetPath)) {
  fail(`Target path does not exist: ${targetPath}`);
} else if (!statSync(targetPath).isDirectory()) {
  fail(`Target path is not a directory: ${targetPath}`);
}

if (failures.length === 0) {
  for (const relativeFile of requiredFiles) {
    if (!existsSync(targetFile(targetPath, relativeFile))) {
      fail(`Missing design packet file: ${relativeFile}`);
    }
  }
}

if (failures.length === 0) {
  for (const { file, patterns } of requiredAnchors) {
    if (!existsSync(targetFile(targetPath, file))) {
      continue;
    }

    const text = readTarget(targetPath, file);
    for (const pattern of patterns) {
      if (!text.includes(pattern)) {
        fail(`Missing anchor in ${file}: ${pattern}`);
      }
    }
  }
}

if (failures.length === 0) {
  try {
    const manifest = JSON.parse(readTarget(targetPath, ".design-agent/manifest.json"));
    const normalizedTarget = path.resolve(targetPath);
    const manifestTarget = manifest.targetPath ? path.resolve(manifest.targetPath) : "";

    if (manifest.version !== 1) {
      fail("Packet manifest version must be 1.");
    }

    if (!manifest.promptMode) {
      fail("Packet manifest missing promptMode.");
    }

    if (!manifest.knowledgeBasePath) {
      fail("Packet manifest missing knowledgeBasePath.");
    }

    if (manifestTarget && manifestTarget !== normalizedTarget) {
      warn(`Packet manifest targetPath differs from checked path: ${manifest.targetPath}`);
    }

    if (!manifest.sourceManifest?.notLandingOnly) {
      fail("Packet source manifest must set notLandingOnly to true.");
    }

    if (!manifest.sourceManifest?.commands?.pack) {
      fail("Packet source manifest missing commands.pack.");
    }

    if (!manifest.sourceManifest?.commands?.packetCheck) {
      fail("Packet source manifest missing commands.packetCheck.");
    }

    for (const requiredFile of requiredFiles) {
      if (!manifest.sourceManifest?.packetFiles?.includes(requiredFile)) {
        fail(`Packet source manifest missing packetFiles entry: ${requiredFile}`);
      }
    }
  } catch (error) {
    fail(`Packet manifest JSON is invalid: ${error.message}`);
  }
}

if (failures.length === 0 && existsSync(targetFile(targetPath, "AGENTS.md"))) {
  const agentsText = readTarget(targetPath, "AGENTS.md");
  if (agentsText.includes("<!-- BEGIN:design-agent-packet -->")) {
    for (const pattern of [
      "<!-- END:design-agent-packet -->",
      ".design-agent/working-brief.md",
      ".design-agent/final-report-template.md",
      "npm run design:packet-check",
      "npm run design:brief-check",
      "npm run design:final-check",
    ]) {
      if (!agentsText.includes(pattern)) {
        fail(`Installed AGENTS.md design block is missing anchor: ${pattern}`);
      }
    }
  }
}

if (warnings.length > 0) {
  console.warn("Design packet warnings:");
  for (const message of warnings) {
    console.warn(`- ${message}`);
  }
}

if (failures.length > 0) {
  console.error("Design packet check failed:");
  for (const message of failures) {
    console.error(`- ${message}`);
  }
  process.exit(1);
}

console.log("Design packet check passed.");

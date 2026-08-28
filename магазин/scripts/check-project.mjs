#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const moduleRoot = path.resolve(scriptDir, "..");
const slug = process.argv[2];

if (!slug) {
  console.error('Usage: node "магазин/scripts/check-project.mjs" <slug>');
  process.exit(1);
}

const projectDir = path.join(moduleRoot, "projects", slug);
const requiredFiles = {
  "01-brief.md": ["Mode:", "Primary conversion:", "Primary CTA:", "Price source:", "Unknowns", "Success metrics"],
  "02-flow-map.md": ["Happy path", "Failure and recovery paths", "ERR-001", "ERR-008", "Post-purchase/manage flow"],
  "03-page-blueprint.md": ["Route map", "First viewport", "Mobile transformation", "Product/service detail", "Checkout and confirmation"],
  "04-commerce-state-model.md": ["Systems of record", "State machines", "Server invariants", "Idempotency key", "Webhook verification"],
  "05-copy-proof-and-trust.md": ["Claim ledger", "Evidence artifact", "Policies and legal owner approval", "Forbidden or removed proof"],
  "06-implementation-plan.md": ["Vertical slices", "TASK-001", "Integrations", "Analytics", "Dependency and performance budget", "Rollout and rollback"],
  "07-qa-report.md": ["Verdict:", "Commercial flow checks", "server-confirmed success", "Accessibility and responsive", "Remaining risks"],
  "08-reference-board.md": ["Closeness", "Borrow", "Transform", "Do not copy", "Risk", "QA", "Rejected references"]
};

const failures = [];
if (!fs.existsSync(projectDir)) {
  failures.push(`Project folder not found: ${projectDir}`);
} else {
  for (const [fileName, terms] of Object.entries(requiredFiles)) {
    const filePath = path.join(projectDir, fileName);
    if (!fs.existsSync(filePath)) {
      failures.push(`Missing ${fileName}`);
      continue;
    }

    const text = fs.readFileSync(filePath, "utf8");
    for (const term of terms) {
      if (!text.toLowerCase().includes(term.toLowerCase())) {
        failures.push(`${fileName} must mention: ${term}`);
      }
    }
  }

  const briefPath = path.join(projectDir, "01-brief.md");
  if (fs.existsSync(briefPath)) {
    const brief = fs.readFileSync(briefPath, "utf8");
    if (!/Mode:\s*(catalog|pizzeria|booking|quote|hybrid)\b/i.test(brief)) {
      failures.push("01-brief.md must contain a valid commerce Mode.");
    }
  }
}

if (failures.length > 0) {
  console.error("Commerce project check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`Commerce project structure passed: ${projectDir}`);
console.log("Note: this checks document structure, not implementation truth or completed QA evidence.");

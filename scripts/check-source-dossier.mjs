#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const requiredHeadings = [
  "Product Snapshot",
  "Current Site Map",
  "Current Landing Structure",
  "Visual Audit",
  "Evidence Inventory",
  "Brand And Content Preservation",
  "Upgrade Opportunities",
  "Reference Hooks",
  "Technical Constraints",
  "Handoff Summary",
];

const requiredTerms = [
  "primary CTA",
  "conversion goal",
  "routes",
  "main files",
  "components",
  "assets",
  "dependencies",
  "mobile",
  "screenshot",
  "viewport",
  "first viewport",
  "overflow",
  "crop",
  "source files",
  "commands run",
  "console",
  "Lighthouse",
  "manual accessibility",
  "heuristic",
  "severity",
  "token",
  "accessibility",
  "preserve",
  "risk",
];

function usage() {
  console.log("Usage: node scripts/check-source-dossier.mjs <path/to/landing-source-dossier.md>");
}

const input = process.argv[2];
if (!input || input === "--help" || input === "-h") {
  usage();
  process.exit(input ? 0 : 1);
}

const dossierPath = path.resolve(process.cwd(), input);
if (!fs.existsSync(dossierPath) || !fs.statSync(dossierPath).isFile()) {
  console.error(`Dossier not found: ${dossierPath}`);
  process.exit(1);
}

const text = fs.readFileSync(dossierPath, "utf8");
const failures = [];
const warnings = [];
const placeholderPattern = new RegExp(`\\bTO${"DO"}\\b|\\btbd\\b|\\bplaceholder\\b`, "i");

for (const heading of requiredHeadings) {
  const pattern = new RegExp(`^#{1,3}\\s*\\d*\\.?\\s*${heading}\\s*$`, "im");
  if (!pattern.test(text)) failures.push(`Missing heading: ${heading}`);
}

for (const term of requiredTerms) {
  const pattern = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i");
  if (!pattern.test(text)) warnings.push(`Expected term not found: ${term}`);
}

const urls = text.match(/https?:\/\/[^\s)]+/g) ?? [];
if (urls.length < 3) {
  warnings.push("Fewer than 3 URLs found. Add references, live URL, repo docs, screenshots, or source links where available.");
}

if (/\bunknown\b/gi.test(text)) {
  warnings.push("Dossier contains unknown fields. That is acceptable, but planning agent must resolve or mark them as assumptions.");
}

if (placeholderPattern.test(text)) {
  failures.push("Placeholder text remains in dossier.");
}

if (text.length < 2500) {
  warnings.push("Dossier is short. Check that section structure, visual audit, preservation, and technical constraints are specific.");
}

const filePathMatches = text.match(/(?:src|app|pages|components|public|assets|styles|lib|hooks|content|data|docs)[/\\][^\s),:`]+/gi) ?? [];
if (filePathMatches.length < 3) {
  warnings.push("Fewer than 3 project file paths found. Add page, component, style, asset, or config paths.");
}

if (!/\bdesktop\b/i.test(text) || !/\bmobile\b/i.test(text)) {
  warnings.push("Dossier should mention both desktop and mobile evidence.");
}

if (!/\b\d{3,4}\s*x\s*\d{3,4}\b/i.test(text)) {
  warnings.push("No viewport dimensions found. Add desktop and mobile viewport sizes or explain why unavailable.");
}

if (!/\.(png|jpe?g|webp|avif)\b/i.test(text) && !/screenshot[^.\n]*(unavailable|not available|unknown)/i.test(text)) {
  warnings.push("No screenshot file path or unavailable reason found.");
}

if (!/(npm|pnpm|yarn|bun)\s+(run\s+)?(dev|build|check|lint|typecheck|test)/i.test(text)) {
  warnings.push("No dev/build/check command found.");
}

if (!/(color|palette|font|typography|radius|spacing|token|shadow|border)/i.test(text)) {
  warnings.push("No visual token evidence found.");
}

if (!/(cosmetic|minor|major|blocker)/i.test(text)) {
  warnings.push("No severity scale values found. Add cosmetic/minor/major/blocker ratings to upgrade opportunities or heuristic issues.");
}

if (warnings.length) {
  console.log("Warnings:");
  for (const warning of warnings) console.log(`- ${warning}`);
}

if (failures.length) {
  console.error("Source dossier check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Source dossier check passed.");

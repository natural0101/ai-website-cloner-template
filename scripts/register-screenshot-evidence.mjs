#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log("Usage: node scripts/register-screenshot-evidence.mjs <project-slug-or-path> --id shot-001 --path evidence/screenshots/file.png --source current|reference|final --viewport desktop|mobile|crop --purpose \"why\" --section \"Hero\" [--notes \"text\"]");
}

const args = process.argv.slice(2);
const input = args[0];
if (!input || input === "--help" || input === "-h") {
  usage();
  process.exit(input ? 0 : 1);
}

function readFlag(name, fallback = "") {
  const index = args.indexOf(`--${name}`);
  if (index === -1) return fallback;
  return args[index + 1] ?? fallback;
}

const required = ["id", "path", "source", "viewport", "purpose", "section"];
const values = Object.fromEntries(required.map((key) => [key, readFlag(key)]));
values.notes = readFlag("notes");

const missing = required.filter((key) => !values[key]);
if (missing.length) {
  console.error(`Missing required flags: ${missing.join(", ")}`);
  usage();
  process.exit(1);
}

const root = process.cwd();
const projectsRoot = path.join(root, "план разработки топового лендинга", "projects");
const candidate = path.isAbsolute(input) ? input : path.join(projectsRoot, input);
const planDir = fs.existsSync(candidate) ? candidate : path.resolve(root, input);

if (!fs.existsSync(planDir) || !fs.statSync(planDir).isDirectory()) {
  console.error(`Plan folder not found: ${planDir}`);
  process.exit(1);
}

const manifestPath = path.join(planDir, "evidence", "screenshot-manifest.md");
if (!fs.existsSync(manifestPath)) {
  console.error(`Screenshot manifest not found: ${manifestPath}`);
  process.exit(1);
}

const clean = (value) => String(value).replace(/\r?\n/g, " ").replace(/\|/g, "\\|").trim();
const row = `| ${clean(values.id)} | ${clean(values.path)} | ${clean(values.source)} | ${clean(values.viewport)} | ${clean(values.purpose)} | ${clean(values.section)} | ${clean(values.notes)} |`;

let text = fs.readFileSync(manifestPath, "utf8");
if (text.includes(`| ${values.id} |`)) {
  console.error(`Screenshot ID already exists: ${values.id}`);
  process.exit(1);
}

const tableHeader = "| ID | Path | Source | Viewport | Purpose | Related section | Notes |";
const insertAt = text.indexOf("\n## ");
if (text.includes(tableHeader) && insertAt !== -1) {
  text = `${text.slice(0, insertAt).trimEnd()}\n${row}\n\n${text.slice(insertAt).trimStart()}`;
} else {
  text = `${text.trimEnd()}\n${row}\n`;
}

fs.writeFileSync(manifestPath, text);
console.log(`Registered screenshot evidence: ${values.id}`);


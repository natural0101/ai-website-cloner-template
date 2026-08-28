#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const moduleRoot = path.resolve(scriptDir, "..");
const templateDir = path.join(moduleRoot, "projects", "_template");
const allowedModes = new Set(["catalog", "pizzeria", "booking", "quote", "hybrid"]);

function usage() {
  console.log('Usage: node "магазин/scripts/create-project.mjs" <slug> --mode <catalog|pizzeria|booking|quote|hybrid>');
}

function slugify(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9а-яё]+/giu, "-")
    .replace(/^-+|-+$/g, "");
}

const args = process.argv.slice(2);
const rawSlug = args[0];
const modeIndex = args.indexOf("--mode");
const mode = modeIndex >= 0 ? args[modeIndex + 1] : null;

if (!rawSlug || !mode || !allowedModes.has(mode)) {
  usage();
  process.exit(1);
}

const slug = slugify(rawSlug);
if (!slug) {
  console.error("Project slug is empty after normalization.");
  process.exit(1);
}

const targetDir = path.join(moduleRoot, "projects", slug);
if (fs.existsSync(targetDir)) {
  console.error(`Project already exists: ${targetDir}`);
  process.exit(1);
}

fs.cpSync(templateDir, targetDir, { recursive: true });

for (const entry of fs.readdirSync(targetDir, { withFileTypes: true })) {
  if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
  const filePath = path.join(targetDir, entry.name);
  const text = fs.readFileSync(filePath, "utf8").replaceAll("{{MODE}}", mode);
  fs.writeFileSync(filePath, text, "utf8");
}

console.log(`Created ${mode} commerce project: ${targetDir}`);
console.log(`Next: fill 01-brief.md through 08-reference-board.md, then run check-project.mjs ${slug}.`);

#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const planRoot = path.join(root, "план разработки топового лендинга");
const templateDir = path.join(planRoot, "projects", "_template");

function usage() {
  console.log("Usage: node scripts/create-landing-plan.mjs <project-slug> [--dossier path]");
}

function slugify(input) {
  return input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9а-яё]+/giu, "-")
    .replace(/^-+|-+$/g, "");
}

const args = process.argv.slice(2);
const rawSlug = args[0];

if (!rawSlug || rawSlug === "--help" || rawSlug === "-h") {
  usage();
  process.exit(rawSlug ? 0 : 1);
}

const slug = slugify(rawSlug);
if (!slug) {
  console.error("Project slug is empty after normalization.");
  process.exit(1);
}

let dossierPath = null;
for (let i = 1; i < args.length; i += 1) {
  if (args[i] === "--dossier") {
    dossierPath = args[i + 1] ?? null;
    i += 1;
  }
}

if (!fs.existsSync(templateDir)) {
  console.error(`Template folder not found: ${templateDir}`);
  process.exit(1);
}

const targetDir = path.join(planRoot, "projects", slug);
if (fs.existsSync(targetDir)) {
  console.error(`Plan folder already exists: ${targetDir}`);
  process.exit(1);
}

fs.cpSync(templateDir, targetDir, { recursive: true });

if (dossierPath) {
  const absoluteDossier = path.resolve(root, dossierPath);
  if (!fs.existsSync(absoluteDossier)) {
    console.error(`Dossier not found: ${absoluteDossier}`);
    process.exit(1);
  }
  fs.copyFileSync(absoluteDossier, path.join(targetDir, "landing-source-dossier.md"));
}

console.log(`Created landing plan: ${targetDir}`);
console.log("Next: fill the numbered plan files, evidence manifests, and any copied dossier with project-specific evidence.");

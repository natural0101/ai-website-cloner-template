#!/usr/bin/env node

import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const rawTargets = args.filter((arg) => arg !== '--dry-run');

if (rawTargets.length === 0) {
  console.error('Usage: npm run clone:prepare -- <url1> [url2...]');
  console.error('       npm run clone:prepare -- --dry-run <url1> [url2...]');
  process.exit(1);
}

function parseTarget(value) {
  const raw = /^[a-z][a-z0-9+.-]*:\/\//i.test(value) ? value : `https://${value}`;
  const url = new URL(raw);
  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new Error(`Only http/https URLs are supported: ${value}`);
  }
  return url;
}

function slugFor(url) {
  const host = url.hostname.replace(/^www\./i, '');
  const path = url.pathname.replace(/\/+$/g, '').replace(/^\/+/g, '');
  const raw = [host, path].filter(Boolean).join('-') || 'target';
  const slug = raw
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80);
  return slug || 'target';
}

const createdAt = new Date().toISOString();
const targets = rawTargets.map((value) => {
  const url = parseTarget(value);
  const slug = slugFor(url);
  return {
    input: value,
    url: url.href,
    hostname: url.hostname,
    slug,
    researchDir: `docs/research/${slug}`,
    referencesDir: `docs/design-references/${slug}`,
    imageDir: `public/images/${slug}`,
    videoDir: `public/videos/${slug}`,
    seoDir: `public/seo/${slug}`,
  };
});

const baseDirs = [
  'docs/research',
  'docs/research/components',
  'docs/design-references',
  'public/images',
  'public/videos',
  'public/seo',
  'scripts',
];

const targetDirs = targets.flatMap((target) => [
  target.researchDir,
  target.referencesDir,
  target.imageDir,
  target.videoDir,
  target.seoDir,
]);

if (!dryRun) {
  for (const dir of [...baseDirs, ...targetDirs]) {
    mkdirSync(join(process.cwd(), dir), { recursive: true });
  }

  writeFileSync(
    join(process.cwd(), 'docs/research/CURRENT_TARGETS.json'),
    `${JSON.stringify({ createdAt, targets }, null, 2)}\n`,
    'utf8'
  );

  writeFileSync(
    join(process.cwd(), 'docs/research/CURRENT_TARGETS.md'),
    [
      '# Current Clone Targets',
      '',
      `Prepared: ${createdAt}`,
      '',
      ...targets.flatMap((target, index) => [
        `## ${index + 1}. ${target.url}`,
        '',
        `- Slug: \`${target.slug}\``,
        `- Research: \`${target.researchDir}\``,
        `- Screenshots: \`${target.referencesDir}\``,
        `- Images: \`${target.imageDir}\``,
        `- Videos: \`${target.videoDir}\``,
        `- SEO assets: \`${target.seoDir}\``,
        '',
      ]),
    ].join('\n'),
    'utf8'
  );
}

console.log(dryRun ? 'Dry run: target plan is valid.' : 'Clone target workspace prepared.');
for (const target of targets) {
  console.log(`- ${target.url}`);
  console.log(`  slug: ${target.slug}`);
}

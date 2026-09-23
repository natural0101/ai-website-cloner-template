#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const hash = (value) => createHash('sha256').update(value).digest('hex').slice(0, 8);
const readable = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'segment';
const normalizeSource = (value) => value.replace(/\s+/g, ' ').trim();
// Exact known scaffolds only; a matching phrase inside user code is insufficient.
const scaffolds = [
  `export default function Home() { return ( <main className="flex min-h-screen items-center justify-center"> <p className="text-muted-foreground"> Clone target not yet built. Run <code className="font-mono text-foreground">/clone-website</code> to start. </p> </main> ); }`,
  `export default function Home() { return ( <main className="flex min-h-screen items-center justify-center px-6"> <div className="max-w-xl space-y-4"> <h1 className="text-3xl font-semibold tracking-tight">Website Cloner</h1> <p className="text-muted-foreground"> Отправьте агенту ссылку на сайт, который хотите скопировать. Шаблон готов к новой задаче. </p> </div> </main> ); }`,
].map(normalizeSource);

function parseTarget(value) {
  if (typeof value !== 'string' || !value.trim() || value.startsWith('--') || /[\s\\]/u.test(value)) {
    throw new Error(`Invalid target URL: ${value}`);
  }
  const hasScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(value);
  const url = new URL(hasScheme ? value : `https://${value}`);
  if (!['http:', 'https:'].includes(url.protocol) || !url.hostname || url.username || url.password) {
    throw new Error(`Only http/https URLs without credentials are supported: ${value}`);
  }
  decodeURI(url.pathname + url.search + url.hash);
  return url;
}

function inventoryRoutes(root) {
  const routes = [];
  function visit(dir, parts = []) {
    if (!existsSync(join(root, dir))) return;
    for (const entry of readdirSync(join(root, dir), { withFileTypes: true })) {
      const file = `${dir}/${entry.name}`;
      if (entry.isDirectory()) visit(file, [...parts, entry.name]);
      else if (entry.isFile() && /^(page\.(tsx|ts|jsx|js|mdx)|route\.(ts|js))$/.test(entry.name)) {
        const special = parts.some((part) => /[()[\]@%]/.test(part) || part.startsWith('_'));
        routes.push({
          file, kind: entry.name.startsWith('route.') ? 'handler' : 'page',
          pathname: special ? null : `/${parts.join('/')}`,
          requiresRouteVerification: special,
          scaffold: file === 'src/app/page.tsx' && scaffolds.includes(normalizeSource(readFileSync(join(root, file), 'utf8'))),
        });
      }
    }
  }
  visit('src/app');
  visit('app');
  return routes.sort((a, b) => a.file.localeCompare(b.file));
}

function routeSegments(pathname) {
  return pathname.split('/').filter(Boolean).map((segment) => segment
    .replace(/^_/, '%5F').replace(/^@/, '%40')
    .replace(/\(/g, '%28').replace(/\)/g, '%29')
    .replace(/\[/g, '%5B').replace(/\]/g, '%5D'));
}

export function createPlan(rawTargets, root = process.cwd()) {
  if (rawTargets.length === 0) throw new Error('Usage: npm run clone:prepare -- [--dry-run] <url1> [url2...]');
  // Validate the whole batch before inspecting or writing target output.
  const urls = rawTargets.map(parseTarget);
  const existingRoutes = inventoryRoutes(root);
  const conflicts = [];
  const origins = [...new Set(urls.map((url) => url.origin))];
  const addConflict = (code, targetIndexes, detail, approvalNeeded = true) => conflicts.push({ code, targetIndexes, detail, approvalNeeded });
  if (origins.length > 1) addConflict('multi-origin-foundation', urls.map((_, i) => i), 'Approve separate prepared application roots or an intentionally combined app with route-scoped foundations. appRoot is only a proposal.');
  const untouchedScaffold = existingRoutes.length === 1 && existingRoutes[0].scaffold
    && !existsSync(join(root, 'src/components/sites')) && !existsSync(join(root, 'public/sites'));
  const targets = urls.map((url, index) => {
    const siteKey = `${readable(url.origin).slice(0, 64)}-${hash(url.origin)}`;
    const pathLabel = url.pathname === '/' ? 'root' : url.pathname.split('/').filter(Boolean).map(readable).join('--').slice(0, 80);
    const pageKey = `${pathLabel || 'root'}-${hash(url.pathname + url.search + url.hash)}`;
    const routePathname = urls.length === 1 && untouchedScaffold ? '/' : url.pathname;
    const routeFile = ['src/app', ...routeSegments(routePathname), 'page.tsx'].join('/');
    const researchDir = `docs/research/${siteKey}/${pageKey}`;
    const referencesDir = `docs/design-references/${siteKey}/${pageKey}`;
    const assetDir = `public/sites/${siteKey}/${pageKey}`;
    const specialSegments = /[()[\]@%]/.test(routePathname) || routePathname.split('/').some((part) => part.startsWith('_')) || routePathname.includes('//');
    if (url.search || url.hash) addConflict('state-behavior-unresolved', [index], 'Infer and record query/fragment behavior from the requested URL; ask only when ambiguous. State does not create a separate App Router pathname.', false);
    const existing = existingRoutes.filter((route) => route.file.toLowerCase() === routeFile.toLowerCase()
      || (route.pathname !== null && route.pathname.replace(/\/$/, '').toLowerCase() === routePathname.replace(/\/$/, '').toLowerCase()));
    const scaffoldReplacement = urls.length === 1 && untouchedScaffold && existing.length === 1 && existing[0].scaffold;
    if (existing.length && !scaffoldReplacement) addConflict('existing-route', [index], `Explicitly approve update, alternate route, or skip: ${existing.map((route) => route.file).join(', ')}`);
    return {
      input: rawTargets[index], url: url.href, hostname: url.hostname, origin: url.origin,
      pathname: url.pathname, query: url.search, fragment: url.hash,
      appRoot: '.', siteKey, pageKey,
      // Backward-compatible field names now use collision-resistant namespaces.
      slug: `${siteKey}/${pageKey}`, researchDir, referencesDir,
      componentDir: `src/components/sites/${siteKey}/${pageKey}`,
      sharedComponentDir: `src/components/sites/${siteKey}/shared`,
      assetDir, sharedAssetDir: `public/sites/${siteKey}/shared`,
      imageDir: `${assetDir}/images`, videoDir: `${assetDir}/videos`, seoDir: `${assetDir}/seo`,
      downloaderFile: `scripts/download-assets-${siteKey}-${pageKey}.mjs`,
      routing: {
        pathname: routePathname, routeFile, scaffoldReplacement,
        existingRouteFiles: existing.map((route) => route.file),
        specialSegments, verified: false, status: 'planned',
        verification: 'Build and request the exact normalized URL before claiming route resolution.',
      },
    };
  });
  const seenArtifacts = new Map();
  const seenRoutes = new Map();
  targets.forEach((target, index) => {
    const artifact = target.researchDir.toLowerCase();
    if (seenArtifacts.has(artifact)) addConflict('artifact-collision', [seenArtifacts.get(artifact), index], 'Duplicate normalized target or hash collision; do not share output without approval.');
    else seenArtifacts.set(artifact, index);
    const route = target.routing.routeFile.toLowerCase();
    if (seenRoutes.has(route)) addConflict('planned-route-collision', [seenRoutes.get(route), index], 'Targets propose the same route file. Resolve origin/state/path behavior before application edits.');
    else seenRoutes.set(route, index);
  });
  if (existingRoutes.some((route) => route.requiresRouteVerification || route.file.startsWith('app/'))) {
    addConflict('existing-route-topology-unresolved', targets.map((_, index) => index), 'Analyze existing route groups, slots, dynamic/encoded/private segments, or root app directory before editing; this planner does not infer their runtime URLs. Approval is required only if analysis finds an actual replacement/collision.', false);
  }
  targets.forEach((target, index) => {
    const decisions = conflicts.filter((conflict) => conflict.targetIndexes.includes(index));
    target.conflicts = decisions.map((conflict) => conflict.code);
    target.approvalNeeded = decisions.some((conflict) => conflict.approvalNeeded);
    target.planDecisionNeeded = decisions.length > 0;
    target.routing.status = target.approvalNeeded ? 'approval-required' : target.planDecisionNeeded ? 'plan-decision-required' : target.routing.specialSegments ? 'verification-required' : 'planned';
  });
  return {
    schemaVersion: 2, createdAt: new Date().toISOString(), mode: 'knowledge-only',
    applicationWrites: false, approvalNeeded: conflicts.some((conflict) => conflict.approvalNeeded),
    planDecisionNeeded: conflicts.length > 0,
    routeResolutionVerified: false, existingRoutes, conflicts, targets,
  };
}

function markdown(plan) {
  return [
    '# Current Clone Targets', '', `Prepared: ${plan.createdAt}`, '',
    'Knowledge-only preparation: no routes, components, assets, or downloaders were written.',
    `Approval needed before application edits: ${plan.approvalNeeded ? 'yes — resolve the conflicts below' : 'no; any state decisions below may be inferred from the request'}.`, '',
    ...plan.targets.flatMap((target, index) => [
      `## ${index + 1}. ${target.url}`, '',
      `- App root (proposed): \`${target.appRoot}\``,
      `- Site key: \`${target.siteKey}\``, `- Page key: \`${target.pageKey}\``,
      `- Route (proposed, not runtime verified): \`${target.routing.pathname}\` → \`${target.routing.routeFile}\``,
      `- Route status: ${target.routing.status}`,
      `- Research: \`${target.researchDir}\``, `- Screenshots: \`${target.referencesDir}\``,
      `- Components (planned): \`${target.componentDir}\``, `- Assets (planned): \`${target.assetDir}\``,
      `- Downloader (planned): \`${target.downloaderFile}\``,
      `- Conflicts: ${target.conflicts.join(', ') || 'none detected'}`, '',
    ]),
    '## Conflicts requiring a decision', '',
    ...plan.conflicts.map((conflict) => `- ${conflict.code}: ${conflict.detail}`),
    ...(plan.conflicts.length ? [] : ['None detected.']), '',
  ].join('\n');
}

export function prepareTargets(rawTargets, { root = process.cwd(), dryRun = false } = {}) {
  const plan = createPlan(rawTargets, root);
  if (!dryRun) {
    for (const target of plan.targets) {
      for (const dir of [target.researchDir, `${target.researchDir}/components`, target.referencesDir]) {
        mkdirSync(join(root, dir), { recursive: true });
      }
    }
    // Only current-plan pointers change; existing per-page artifacts are preserved.
    writeFileSync(join(root, 'docs/research/CURRENT_TARGETS.json'), `${JSON.stringify(plan, null, 2)}\n`, 'utf8');
    writeFileSync(join(root, 'docs/research/CURRENT_TARGETS.md'), markdown(plan), 'utf8');
  }
  return plan;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    const dryRun = args.includes('--dry-run');
    const plan = prepareTargets(args.filter((arg) => arg !== '--dry-run'), { dryRun });
    console.log(dryRun ? 'Dry run: knowledge-only target plan (no writes).' : 'Clone research workspace prepared; application files unchanged.');
    console.log(JSON.stringify(plan, null, 2));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}

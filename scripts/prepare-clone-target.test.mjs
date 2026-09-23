import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { createPlan, prepareTargets } from './prepare-clone-target.mjs';

function fixture(t) {
  const base = resolve(tmpdir());
  const root = mkdtempSync(join(base, 'clone-plan-test-'));
  t.after(() => {
    assert.ok(resolve(root).startsWith(`${base}${sep}clone-plan-test-`));
    rmSync(root, { recursive: true, force: true });
  });
  return root;
}
function put(root, file, content) {
  mkdirSync(dirname(join(root, file)), { recursive: true });
  writeFileSync(join(root, file), content);
}
const codes = (plan) => plan.conflicts.map((conflict) => conflict.code);

test('origin scheme, ports and lossy host slugs receive separate stable namespaces', (t) => {
  const root = fixture(t);
  const urls = ['https://a-b.test/docs', 'https://a.b.test/docs', 'http://a-b.test/docs', 'https://a-b.test:8443/docs'];
  const plan = createPlan(urls, root);
  assert.equal(new Set(plan.targets.map((target) => target.siteKey)).size, 4);
  assert.ok(plan.targets[3].siteKey.includes('8443'));
  for (const target of plan.targets) {
    const digest = createHash('sha256').update(target.origin).digest('hex').slice(0, 8);
    assert.ok(target.siteKey.endsWith(`-${digest}`));
  }
  assert.ok(codes(plan).includes('multi-origin-foundation'));
  assert.equal(plan.approvalNeeded, true);
  const normalized = createPlan(['HTTPS://A-B.TEST:443/docs'], root);
  assert.equal(normalized.targets[0].siteKey, plan.targets[0].siteKey);
});

test('pathname boundaries, punctuation and state create distinct artifact keys', (t) => {
  const root = fixture(t);
  const paths = ['/a/b', '/a-b', '/a_b', '/a/b?tab=one', '/a/b?tab=two', '/a/b#one'];
  const plan = createPlan(paths.map((path) => `https://example.test${path}`), root);
  assert.equal(new Set(plan.targets.map((target) => target.pageKey)).size, paths.length);
  assert.equal(new Set(plan.targets.map((target) => target.downloaderFile)).size, paths.length);
  assert.match(plan.targets[0].pageKey, /^a--b-/);
  assert.equal(plan.targets[0].routing.routeFile, 'src/app/a/b/page.tsx');
  for (const index of [3, 4, 5]) {
    assert.equal(plan.targets[index].routing.routeFile, plan.targets[0].routing.routeFile);
    assert.equal(plan.targets[index].routing.status, 'approval-required');
    assert.ok(plan.targets[index].conflicts.includes('state-behavior-unresolved'));
    assert.ok(plan.targets[index].conflicts.includes('planned-route-collision'));
  }
  assert.equal(plan.routeResolutionVerified, false);
});

test('existing authored routes and research are preserved; plan reports exact conflicts', (t) => {
  const root = fixture(t);
  put(root, 'src/app/page.tsx', 'export default function Home() { return "My work"; }');
  put(root, 'src/app/docs/intro/page.tsx', '// protected existing page');
  const urls = ['https://example.test/docs/intro', 'https://example.test/other'];
  const preliminary = createPlan(urls, root);
  const artifact = `${preliminary.targets[0].researchDir}/notes.md`;
  put(root, artifact, 'preserve research');
  const plan = prepareTargets(urls, { root });
  assert.equal(readFileSync(join(root, 'src/app/page.tsx'), 'utf8'), 'export default function Home() { return "My work"; }');
  assert.equal(readFileSync(join(root, 'src/app/docs/intro/page.tsx'), 'utf8'), '// protected existing page');
  assert.equal(readFileSync(join(root, artifact), 'utf8'), 'preserve research');
  assert.equal(plan.targets[0].routing.routeFile, 'src/app/docs/intro/page.tsx');
  assert.deepEqual(plan.targets[0].routing.existingRouteFiles, ['src/app/docs/intro/page.tsx']);
  assert.ok(plan.targets[0].conflicts.includes('existing-route'));
  assert.equal(existsSync(join(root, 'src/app/other')), false);
  assert.equal(existsSync(join(root, 'public')), false);
  assert.equal(existsSync(join(root, 'src/components')), false);
  assert.deepEqual(JSON.parse(readFileSync(join(root, 'docs/research/CURRENT_TARGETS.json'))), plan);
  assert.equal(existsSync(join(root, plan.targets[1].referencesDir)), true);
});

test('dry-run leaves even an empty working directory untouched', (t) => {
  const root = fixture(t);
  const plan = prepareTargets(['https://example.test/hello'], { root, dryRun: true });
  assert.equal(plan.targets[0].routing.pathname, '/hello');
  assert.deepEqual(readdirSync(root), []);
  const cli = spawnSync(process.execPath, [fileURLToPath(new URL('./prepare-clone-target.mjs', import.meta.url)), '--dry-run', 'https://example.test/hello'], { cwd: root, encoding: 'utf8' });
  assert.equal(cli.status, 0, cli.stderr);
  assert.match(cli.stdout, /no writes/);
  assert.deepEqual(readdirSync(root), []);
});

test('any invalid member rejects the whole batch before writes and preserves previous plan', (t) => {
  const root = fixture(t);
  put(root, 'docs/research/CURRENT_TARGETS.json', 'previous plan');
  for (const bad of ['ftp://example.test/a', 'https://', 'https://example.test/%zz', '--unknown', 'https://user:pass@example.test', 'not a URL']) {
    assert.throws(() => prepareTargets(['https://good.test/path', bad], { root }));
    assert.equal(readFileSync(join(root, 'docs/research/CURRENT_TARGETS.json'), 'utf8'), 'previous plan');
    assert.deepEqual(readdirSync(join(root, 'docs/research')), ['CURRENT_TARGETS.json']);
    assert.equal(existsSync(join(root, 'docs/design-references')), false);
  }
});

test('literal App Router syntax is escaped and route resolution remains unverified', (t) => {
  const root = fixture(t);
  const plan = createPlan(['https://example.test/_private/@slot/(group)/[slug]'], root);
  assert.equal(plan.targets[0].routing.routeFile, 'src/app/%5Fprivate/%40slot/%28group%29/%5Bslug%5D/page.tsx');
  assert.equal(plan.targets[0].routing.status, 'verification-required');
  assert.equal(plan.targets[0].routing.verified, false);
  assert.equal(existsSync(join(root, 'src')), false);
});

test('existing dynamic/group/slot topology cannot be mistaken for an available route', (t) => {
  const root = fixture(t);
  put(root, 'src/app/(marketing)/[slug]/page.tsx', '// existing dynamic route');
  const plan = prepareTargets(['https://example.test/hello'], { root });
  assert.equal(plan.existingRoutes[0].pathname, null);
  assert.ok(codes(plan).includes('existing-route-topology-unresolved'));
  assert.equal(plan.targets[0].routing.status, 'plan-decision-required');
  assert.equal(readFileSync(join(root, 'src/app/(marketing)/[slug]/page.tsx'), 'utf8'), '// existing dynamic route');
});

test('duplicate canonical targets and case-insensitive route collisions are explicit', (t) => {
  const root = fixture(t);
  const plan = createPlan(['https://example.test/Foo', 'https://example.test/foo', 'https://EXAMPLE.test:443/foo'], root);
  assert.ok(codes(plan).includes('artifact-collision'));
  assert.ok(codes(plan).includes('planned-route-collision'));
  assert.equal(plan.targets.every((target) => target.approvalNeeded), true);
});

test('first exact scaffold may propose root replacement; authored lookalikes may not', (t) => {
  const root = fixture(t);
  const scaffold = `export default function Home() { return ( <main className="flex min-h-screen items-center justify-center"> <p className="text-muted-foreground"> Clone target not yet built. Run <code className="font-mono text-foreground">/clone-website</code> to start. </p> </main> ); }`;
  put(root, 'src/app/page.tsx', scaffold);
  const first = prepareTargets(['https://example.test/docs'], { root });
  assert.equal(first.targets[0].routing.pathname, '/');
  assert.equal(first.targets[0].routing.scaffoldReplacement, true);
  assert.equal(first.approvalNeeded, false);
  assert.equal(readFileSync(join(root, 'src/app/page.tsx'), 'utf8'), scaffold);
  put(root, 'src/app/page.tsx', `${scaffold}\n// user-owned addition`);
  const later = createPlan(['https://example.test/docs'], root);
  assert.equal(later.targets[0].routing.pathname, '/docs');
  assert.equal(later.targets[0].routing.scaffoldReplacement, false);
});

test('single state URL needs a behavior plan without an unnecessary approval gate', (t) => {
  const root = fixture(t);
  const plan = createPlan(['https://example.test/search?q=hello#results'], root);
  assert.equal(plan.approvalNeeded, false);
  assert.equal(plan.planDecisionNeeded, true);
  assert.equal(plan.targets[0].routing.pathname, '/search');
  assert.equal(plan.targets[0].routing.status, 'plan-decision-required');
});

test('current neutral Website Cloner scaffold supports first root clone', (t) => {
  const root = fixture(t);
  put(root, 'src/app/page.tsx', `export default function Home() { return ( <main className="flex min-h-screen items-center justify-center px-6"> <div className="max-w-xl space-y-4"> <h1 className="text-3xl font-semibold tracking-tight">Website Cloner</h1> <p className="text-muted-foreground"> Отправьте агенту ссылку на сайт, который хотите скопировать. Шаблон готов к новой задаче. </p> </div> </main> ); }`);
  const plan = createPlan(['https://example.test/docs/intro'], root);
  assert.equal(plan.targets[0].routing.routeFile, 'src/app/page.tsx');
  assert.equal(plan.targets[0].routing.scaffoldReplacement, true);
  assert.equal(plan.approvalNeeded, false);
});

test('existing route handlers conflict with pages at the same pathname and remain untouched', (t) => {
  const root = fixture(t);
  put(root, 'src/app/contact/route.ts', '// protected handler');
  put(root, 'src/app/api/route.js', '// protected JavaScript handler');
  const plan = prepareTargets(['https://example.test/contact', 'https://example.test/api'], { root });
  assert.equal(plan.existingRoutes.every((route) => route.kind === 'handler'), true);
  assert.equal(plan.targets.every((target) => target.approvalNeeded && target.conflicts.includes('existing-route')), true);
  assert.equal(existsSync(join(root, 'src/app/contact/page.tsx')), false);
  assert.equal(existsSync(join(root, 'src/app/api/page.tsx')), false);
  assert.equal(readFileSync(join(root, 'src/app/contact/route.ts'), 'utf8'), '// protected handler');
  assert.equal(readFileSync(join(root, 'src/app/api/route.js'), 'utf8'), '// protected JavaScript handler');
});

#!/usr/bin/env node

/** Generate compatibility skills/commands from the canonical cross-agent skill. */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CANONICAL = '.agents/skills/clone-website';
const raw = readFileSync(join(ROOT, CANONICAL, 'SKILL.md'), 'utf8').replace(/\r\n/g, '\n');
const guide = readFileSync(join(ROOT, CANONICAL, 'references/inspection-guide.md'), 'utf8').replace(/\r\n/g, '\n');
const match = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
if (!match) throw new Error('Canonical SKILL.md has invalid frontmatter');
const body = match[2];
const shortDesc = 'Reverse-engineer and clone one or more websites as pixel-perfect replicas';
const header = `<!-- AUTO-GENERATED from ${CANONICAL}/SKILL.md — do not edit directly.\n     Run \`node scripts/sync-skills.mjs\` to regenerate. -->\n\n`;
let generated = 0;
function write(destination, content) {
  const full = join(ROOT, destination);
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, content, 'utf8');
  generated += 1;
  console.log(`  ${destination}`);
}
function commandBody(destination) {
  const reference = relative(dirname(join(ROOT, destination)), join(ROOT, CANONICAL, 'references/inspection-guide.md')).replace(/\\/g, '/');
  return body.replaceAll('(references/inspection-guide.md)', `(${reference})`);
}

// Keep compatibility skills for agents using their platform-specific discovery paths.
// Claude retains a generated invocable skill, avoiding a duplicate command with the same name.
for (const platform of ['.claude', '.codex', '.github', '.kiro', '.cline', '.roo']) {
  const skillRoot = `${platform}/skills/clone-website`;
  const content = platform === '.claude'
    ? raw.replace('\n---\n', '\nargument-hint: "<url1> [<url2> ...]"\nuser-invocable: true\n---\n')
    : raw;
  write(`${skillRoot}/SKILL.md`, content);
  write(`${skillRoot}/references/inspection-guide.md`, guide);
}
write('.roo/commands/clone-website.md', `---\ndescription: "${shortDesc}"\nargument-hint: "<url1> [<url2> ...]"\n---\n${header}Use the \`clone-website\` skill for the target URL or URLs provided by the user. Load that skill and follow its workflow exactly.\n`);
for (const destination of ['.cursor/commands/clone-website.md', '.windsurf/workflows/clone-website.md']) {
  write(destination, header + commandBody(destination));
}
for (const [destination, frontmatter, argumentsLine] of [
  ['.opencode/commands/clone-website.md', `description: "${shortDesc}"`, 'Target URL arguments: $ARGUMENTS'],
  ['.augment/commands/clone-website.md', `description: "${shortDesc}"\nargument-hint: "<url1> [<url2> ...]"`, 'Target URLs are provided in the user request.'],
  ['.continue/commands/clone-website.md', `name: clone-website\ndescription: "${shortDesc}"\ninvokable: true`, 'Target URLs are provided in the user request.'],
]) {
  write(destination, `---\n${frontmatter}\n---\n${header}${argumentsLine}\n\n${commandBody(destination)}`);
}
const geminiPath = '.gemini/commands/clone-website.toml';
write(geminiPath, `# AUTO-GENERATED from ${CANONICAL}/SKILL.md\n# Run \`node scripts/sync-skills.mjs\` to regenerate.\n\ndescription = "${shortDesc}"\nname = "clone-website"\n\nprompt = '''\nTarget URL arguments: {{args}}\n\n${commandBody(geminiPath)}\n'''\n`);
const amazonPath = '.amazonq/cli-agents/clone-website.json';
write(amazonPath, `${JSON.stringify({
  name: 'clone-website',
  description: shortDesc,
  prompt: commandBody(amazonPath),
  fileContext: ['AGENTS.md', `${CANONICAL}/references/**`, 'docs/research/**'],
}, null, 2)}\n`);
console.log(`Done: ${generated} compatibility files generated from ${CANONICAL}.`);

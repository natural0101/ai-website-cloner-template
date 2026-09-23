#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const requiredFiles = [
  "01-current-state-audit.md",
  "02-copy-and-offer-audit.md",
  "03-reference-board.md",
  "04-visual-benchmark.md",
  "05-visual-direction.md",
  "06-section-by-section-upgrade-plan.md",
  "07-animation-storyboard.md",
  "08-component-and-asset-plan.md",
  "09-implementation-tasks.md",
  "10-quality-gate.md",
  "11-implementation-handoff-prompt.md",
  "12-final-qa-report.md",
  "13-section-pattern-selection.md",
  "14-animate-ui-selection.md",
  "29-motion-primitives-selection.md",
  "30-magic-ui-selection.md",
  "31-aceternity-ui-selection.md",
  "32-tailark-section-selection.md",
  "33-shadcnblocks-selection.md",
  "34-micro-component-selection.md",
  "35-react-bits-selection.md",
  "36-pacekit-gsap-selection.md",
  "37-cult-ui-selection.md",
  "38-reui-selection.md",
  "39-twenty-first-dev-selection.md",
  "40-kokonut-ui-selection.md",
  "41-mvpblocks-selection.md",
  "42-smoothui-selection.md",
  "43-hextaui-selection.md",
  "44-skiper-ui-selection.md",
  "45-eldora-ui-selection.md",
  "46-blocks-so-selection.md",
  "47-intent-ui-selection.md",
  "24-thematic-reference-map.md",
  "25-brand-dna-map.md",
  "15-reference-scorecard.md",
  "22-inspiration-synthesis.md",
  "26-motion-reference-map.md",
  "16-motion-recipe-selection.md",
  "17-visual-style-tile.md",
  "18-section-storyboard-canvas.md",
  "19-asset-production-queue.md",
  "27-responsive-viewport-map.md",
  "20-implementation-task-graph.md",
  "28-change-traceability-matrix.md",
  "21-plan-self-review.md",
  "23-presentation-quality-review.md",
];

const evidenceFiles = [
  "evidence/reference-manifest.md",
  "evidence/screenshot-manifest.md",
  "evidence/asset-manifest.md",
  "evidence/decision-log.md",
];

function usage() {
  console.log("Usage: node scripts/check-landing-plan.mjs <project-slug-or-path>");
}

const input = process.argv[2];
if (!input || input === "--help" || input === "-h") {
  usage();
  process.exit(input ? 0 : 1);
}

const root = process.cwd();
const planRoot = path.join(root, "план разработки топового лендинга", "projects");
const candidatePath = path.isAbsolute(input) ? input : path.join(planRoot, input);
const planDir = fs.existsSync(candidatePath) ? candidatePath : path.resolve(root, input);

if (!fs.existsSync(planDir) || !fs.statSync(planDir).isDirectory()) {
  console.error(`Plan folder not found: ${planDir}`);
  process.exit(1);
}

const failures = [];
const warnings = [];
const placeholderPattern = new RegExp(`\\bTO${"DO"}\\b|\\btbd\\b|\\bplaceholder\\b`, "i");
const exampleUrlPattern = /https?:\/\/example\.com/i;

for (const file of requiredFiles) {
  const filePath = path.join(planDir, file);
  if (!fs.existsSync(filePath)) {
    failures.push(`Missing required file: ${file}`);
    continue;
  }

  const text = fs.readFileSync(filePath, "utf8");
  const nonEmptyLines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (nonEmptyLines.length < 8) {
    failures.push(`Too little content: ${file}`);
  }

  if (placeholderPattern.test(text)) {
    failures.push(`Placeholder text remains: ${file}`);
  }

  if (exampleUrlPattern.test(text)) {
    failures.push(`Example URL remains: ${file}`);
  }

  if (/^\|\s*\|\s*\|\s*\|/m.test(text)) {
    warnings.push(`Empty table rows may remain: ${file}`);
  }

  if (/:\s*$/m.test(text)) {
    warnings.push(`Empty field labels may remain: ${file}`);
  }
}

for (const file of evidenceFiles) {
  const filePath = path.join(planDir, file);
  if (!fs.existsSync(filePath)) {
    warnings.push(`Evidence file is missing: ${file}`);
  }
}

const referenceBoard = path.join(planDir, "03-reference-board.md");
if (fs.existsSync(referenceBoard)) {
  const text = fs.readFileSync(referenceBoard, "utf8");
  const urls = text.match(/https?:\/\/[^\s)]+/g) ?? [];
  if (urls.length < 5) {
    failures.push("Reference board should contain at least 5 concrete URLs.");
  }
  for (const term of ["Source lane", "Access status", "Closeness reason", "Transform", "Do not copy", "Section mapping"]) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Reference board should mention ${term}.`);
    }
  }
}

const referenceManifest = path.join(planDir, "evidence", "reference-manifest.md");
if (fs.existsSync(referenceManifest)) {
  const text = fs.readFileSync(referenceManifest, "utf8");
  const urls = text.match(/https?:\/\/[^\s)]+/g) ?? [];
  if (urls.length === 0) {
    warnings.push("Reference manifest has no concrete URLs yet.");
  }
}

const referenceScorecard = path.join(planDir, "15-reference-scorecard.md");
if (fs.existsSync(referenceScorecard)) {
  const text = fs.readFileSync(referenceScorecard, "utf8");
  const urls = text.match(/https?:\/\/[^\s)]+/g) ?? [];
  if (urls.length < 1) {
    failures.push("Reference scorecard should contain at least 1 concrete scored URL.");
  }
  if (!/\b(ref-\d{3}|anti-reference|Core reference|Section reference|Detail reference|Reject)/i.test(text)) {
    failures.push("Reference scorecard should include scored IDs and decisions.");
  }
  if (!/Access status/i.test(text)) {
    failures.push("Reference scorecard should include access status for each scored reference.");
  }
}

const thematicReferenceMap = path.join(planDir, "24-thematic-reference-map.md");
if (fs.existsSync(thematicReferenceMap)) {
  const text = fs.readFileSync(thematicReferenceMap, "utf8");
  const requiredTerms = ["Search Brief", "Reference Lanes", "Access status", "Closeness reason", "Query Log", "Closeness Matrix", "Candidate Mix", "Promotion To Scorecard", "Anti-reference"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Thematic reference map should mention ${term}.`);
    }
  }
}

const brandDnaMap = path.join(planDir, "25-brand-dna-map.md");
if (fs.existsSync(brandDnaMap)) {
  const text = fs.readFileSync(brandDnaMap, "utf8");
  const requiredTerms = ["Source Evidence", "Brand Read", "DNA Decisions", "Preserve List", "Evolve List", "Remove List", "Introduce List", "Downstream Instructions", "Protect"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Brand DNA map should mention ${term}.`);
    }
  }
}

const inspirationSynthesis = path.join(planDir, "22-inspiration-synthesis.md");
if (fs.existsSync(inspirationSynthesis)) {
  const text = fs.readFileSync(inspirationSynthesis, "utf8");
  const requiredTerms = ["Closeness reason", "Borrow", "Transform", "Do not copy", "Concrete visible decision", "Motion Translation", "Asset Translation", "Anti-Reference"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Inspiration synthesis should mention ${term}.`);
    }
  }
}

const motionReferenceMap = path.join(planDir, "26-motion-reference-map.md");
if (fs.existsSync(motionReferenceMap)) {
  const text = fs.readFileSync(motionReferenceMap, "utf8");
  const requiredTerms = ["Motion Search Brief", "Verified Motion Sources", "Pattern Candidates", "Section Motion Map", "Borrow", "Transform", "Do not copy", "Reduced-motion fallback", "Mobile simplification", "Motion safety verdict", "Promotion", "Motion Budget"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Motion reference map should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog/i.test(text)) {
    failures.push("Motion reference map should include motion candidate decisions.");
  }
}

const motionRecipeSelection = path.join(planDir, "16-motion-recipe-selection.md");
if (fs.existsSync(motionRecipeSelection)) {
  const text = fs.readFileSync(motionRecipeSelection, "utf8");
  for (const term of ["Reduced-motion fallback", "Mobile simplification", "Performance risk", "Motion safety verdict", "QA"]) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Motion recipe selection should mention ${term}.`);
    }
  }
  if (!/recipe|trigger|timing|library|QA/i.test(text)) {
    failures.push("Motion recipe selection should include recipe, trigger, timing, library, and QA fields.");
  }
}

const screenshotManifest = path.join(planDir, "evidence", "screenshot-manifest.md");
if (fs.existsSync(screenshotManifest)) {
  const text = fs.readFileSync(screenshotManifest, "utf8");
  if (!/\.(png|jpe?g|webp|avif)/i.test(text)) {
    warnings.push("Screenshot manifest has no screenshot file paths yet.");
  }
}

const motionStoryboard = path.join(planDir, "07-animation-storyboard.md");
if (fs.existsSync(motionStoryboard)) {
  const text = fs.readFileSync(motionStoryboard, "utf8");
  if (!/reduced[- ]motion/i.test(text)) {
    failures.push("Animation storyboard must mention reduced-motion fallback.");
  }
  for (const term of ["Mobile simplification", "Performance risk", "Motion safety verdict"]) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Animation storyboard should mention ${term}.`);
    }
  }
}

const animateUiSelection = path.join(planDir, "14-animate-ui-selection.md");
if (fs.existsSync(animateUiSelection)) {
  const text = fs.readFileSync(animateUiSelection, "utf8");
  const requiredTerms = ["Live docs branch", "Candidate registry item", "Install command", "Dependency impact", "Motion purpose", "Reduced-motion fallback", "Icon Decisions"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Animate UI selection should mention ${term}.`);
    }
  }
}

const motionPrimitivesSelection = path.join(planDir, "29-motion-primitives-selection.md");
if (fs.existsSync(motionPrimitivesSelection)) {
  const text = fs.readFileSync(motionPrimitivesSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Components", "Installation Queue", "Rejected Items", "Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Motion Primitives selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none/i.test(text)) {
    failures.push("Motion Primitives selection should include explicit candidate decisions.");
  }
}

const magicUiSelection = path.join(planDir, "30-magic-ui-selection.md");
if (fs.existsSync(magicUiSelection)) {
  const text = fs.readFileSync(magicUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Components", "Installation Queue", "Rejected Items", "Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Magic UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none/i.test(text)) {
    failures.push("Magic UI selection should include explicit candidate decisions.");
  }
}

const aceternityUiSelection = path.join(planDir, "31-aceternity-ui-selection.md");
if (fs.existsSync(aceternityUiSelection)) {
  const text = fs.readFileSync(aceternityUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Components Or Blocks", "Installation Queue", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Aceternity UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Aceternity UI selection should include explicit candidate decisions.");
  }
}

const tailarkSectionSelection = path.join(planDir, "32-tailark-section-selection.md");
if (fs.existsSync(tailarkSectionSelection)) {
  const text = fs.readFileSync(tailarkSectionSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Sections Or Blocks", "Installation Queue", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Tailark section selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Tailark section selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Tailark section selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Tailark section selection should map selections to change IDs.");
  }
}

const shadcnblocksSelection = path.join(planDir, "33-shadcnblocks-selection.md");
if (fs.existsSync(shadcnblocksSelection)) {
  const text = fs.readFileSync(shadcnblocksSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Blocks Components Or Pages", "Installation Queue", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`shadcnblocks selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("shadcnblocks selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("shadcnblocks selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("shadcnblocks selection should map selections to change IDs.");
  }
}

const microComponentSelection = path.join(planDir, "34-micro-component-selection.md");
if (fs.existsSync(microComponentSelection)) {
  const text = fs.readFileSync(microComponentSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Micro Components", "Installation Or Copy Queue", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification", "Keyboard/focus QA", "Live endpoint verification", "Heavy endpoint"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Micro component selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Micro component selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Micro component selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Micro component selection should map selections to change IDs.");
  }
}

const reactBitsSelection = path.join(planDir, "35-react-bits-selection.md");
if (fs.existsSync(reactBitsSelection)) {
  const text = fs.readFileSync(reactBitsSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate React Bits Items", "Installation Queue", "Heavy Runtime Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`React Bits selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("React Bits selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("React Bits selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("React Bits selection should map selections to change IDs.");
  }
  if (!/TS-TW|TypeScript \+ Tailwind/i.test(text)) {
    failures.push("React Bits selection should state the chosen implementation variant.");
  }
}

const pacekitGsapSelection = path.join(planDir, "36-pacekit-gsap-selection.md");
if (fs.existsSync(pacekitGsapSelection)) {
  const text = fs.readFileSync(pacekitGsapSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate PaceKit GSAP Items", "Installation Queue", "GSAP Runtime Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`PaceKit GSAP selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("PaceKit GSAP selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("PaceKit GSAP selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("PaceKit GSAP selection should map selections to change IDs.");
  }
  if (!/gsap/i.test(text)) {
    failures.push("PaceKit GSAP selection should state GSAP dependency impact.");
  }
}

const cultUiSelection = path.join(planDir, "37-cult-ui-selection.md");
if (fs.existsSync(cultUiSelection)) {
  const text = fs.readFileSync(cultUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Cult UI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile simplification"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Cult UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Cult UI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Cult UI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Cult UI selection should map selections to change IDs.");
  }
  if (!/cult-ui\.com\/r\//i.test(text)) {
    failures.push("Cult UI selection should include exact Cult UI registry URLs or an explicit none/reject row.");
  }
}

const reuiSelection = path.join(planDir, "38-reui-selection.md");
if (fs.existsSync(reuiSelection)) {
  const text = fs.readFileSync(reuiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate ReUI Items", "Installation Queue", "Access And Registry Gate", "Rejected Items", "License And Adaptation Notes", "Keyboard/Focus QA", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`ReUI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("ReUI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("ReUI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("ReUI selection should map selections to change IDs.");
  }
  const hasReuiRegistryUrl = /reui\.io\/r\//i.test(text);
  const hasExplicitNoReuiRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasReuiRegistryUrl && !hasExplicitNoReuiRow) {
    failures.push("ReUI selection should include exact ReUI registry URLs or an explicit none/reject row.");
  }
  if (!/401|403|license|free|pro|REUI_LICENSE_KEY/i.test(text)) {
    failures.push("ReUI selection should state access or license gate status.");
  }
}

const twentyFirstDevSelection = path.join(planDir, "39-twenty-first-dev-selection.md");
if (fs.existsSync(twentyFirstDevSelection)) {
  const text = fs.readFileSync(twentyFirstDevSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate 21st.dev Items", "Installation Queue", "Access And Registry Gate", "Heavy Runtime Gate", "Rejected Items", "License And Adaptation Notes", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term.replace(".", "\\."), "i").test(text)) {
      failures.push(`21st.dev selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("21st.dev selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("21st.dev selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("21st.dev selection should map selections to change IDs.");
  }
  const hasTwentyFirstEvidence = /@21st-dev\/cli|21st\.dev\/@|cdn\.21st\.dev/i.test(text);
  const hasExplicitNoTwentyFirstRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasTwentyFirstEvidence && !hasExplicitNoTwentyFirstRow) {
    failures.push("21st.dev selection should include exact component, command, CDN registry URL, or an explicit none/reject row.");
  }
  if (!/license|MIT|reference-only|public|installable/i.test(text)) {
    failures.push("21st.dev selection should state access or license gate status.");
  }
}

const kokonutUiSelection = path.join(planDir, "40-kokonut-ui-selection.md");
if (fs.existsSync(kokonutUiSelection)) {
  const text = fs.readFileSync(kokonutUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Kokonut UI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Kokonut UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Kokonut UI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Kokonut UI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Kokonut UI selection should map selections to change IDs.");
  }
  const hasKokonutRegistryUrl = /kokonutui\.com\/r\//i.test(text);
  const hasExplicitNoKokonutRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasKokonutRegistryUrl && !hasExplicitNoKokonutRow) {
    failures.push("Kokonut UI selection should include exact Kokonut UI registry URLs or an explicit none/reject row.");
  }
  if (!/MIT|Pro|license|reference-only|public/i.test(text)) {
    failures.push("Kokonut UI selection should state license or Pro access gate status.");
  }
}

const mvpblocksSelection = path.join(planDir, "41-mvpblocks-selection.md");
if (fs.existsSync(mvpblocksSelection)) {
  const text = fs.readFileSync(mvpblocksSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate MVPBlocks Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`MVPBlocks selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("MVPBlocks selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("MVPBlocks selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("MVPBlocks selection should map selections to change IDs.");
  }
  const hasMvpblocksEvidence = /blocks\.mvp-subha\.me\/r\/[^ \n|)]+\.json|npx\s+mvpblocks\s+add/i.test(text);
  const hasExplicitNoMvpblocksRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasMvpblocksEvidence && !hasExplicitNoMvpblocksRow) {
    failures.push("MVPBlocks selection should include exact item endpoints, CLI commands, or an explicit none/reject row.");
  }
  if (!/BSD-3-Clause|MIT|license|reference-only|public/i.test(text)) {
    failures.push("MVPBlocks selection should state license gate status.");
  }
  if (/\/r\/registry\.json|\/registry\.json/i.test(text) && !/not used|404|reject/i.test(text)) {
    failures.push("MVPBlocks selection should not use root registry indexes as valid install evidence.");
  }
}

const smoothuiSelection = path.join(planDir, "42-smoothui-selection.md");
if (fs.existsSync(smoothuiSelection)) {
  const text = fs.readFileSync(smoothuiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate SmoothUI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion fallback", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`SmoothUI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("SmoothUI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("SmoothUI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("SmoothUI selection should map selections to change IDs.");
  }
  const hasSmoothuiEvidence = /smoothui\.dev\/r\/[^ \n|)]+\.json|@smoothui\/|smoothui-cli/i.test(text);
  const hasExplicitNoSmoothuiRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasSmoothuiEvidence && !hasExplicitNoSmoothuiRow) {
    failures.push("SmoothUI selection should include exact item endpoints, CLI commands, namespace commands, or an explicit none/reject row.");
  }
  if (!/MIT|license|reference-only|public/i.test(text)) {
    failures.push("SmoothUI selection should state license gate status.");
  }
  if (/\/api\/v1\/blocks/i.test(text) && !/not used|empty|500|reject|not use|no/i.test(text)) {
    failures.push("SmoothUI selection should not use the broken blocks API as valid install evidence.");
  }
}

const hextauiSelection = path.join(planDir, "43-hextaui-selection.md");
if (fs.existsSync(hextauiSelection)) {
  const text = fs.readFileSync(hextauiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate HextaUI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "HTML docs caveat", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`HextaUI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("HextaUI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("HextaUI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("HextaUI selection should map selections to change IDs.");
  }
  const hasHextauiEvidence = /hextaui\.com\/r\/[^ \n|)]+\.json|@hextaui\//i.test(text);
  const hasExplicitNoHextauiRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasHextauiEvidence && !hasExplicitNoHextauiRow) {
    failures.push("HextaUI selection should include exact item endpoints, namespace commands, or an explicit none/reject row.");
  }
  if (!/MIT|license|reference-only|public/i.test(text)) {
    failures.push("HextaUI selection should state license gate status.");
  }
  if (/registry\.hextaui\.com|\/registry\.json/i.test(text) && !/not used|404|reject|not use|no/i.test(text)) {
    failures.push("HextaUI selection should not use broken registry guesses as valid install evidence.");
  }
}

const skiperUiSelection = path.join(planDir, "44-skiper-ui-selection.md");
if (fs.existsSync(skiperUiSelection)) {
  const text = fs.readFileSync(skiperUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Skiper UI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "Access And Adaptation Notes", "Terms/access", "Reduced-motion Fallback", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Skiper UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Skiper UI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Skiper UI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Skiper UI selection should map selections to change IDs.");
  }
  const hasSkiperEvidence = /skiper-ui\.com\/registry\/[^ \n|)]+\.json|@skiper-ui\//i.test(text);
  const hasExplicitNoSkiperRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasSkiperEvidence && !hasExplicitNoSkiperRow) {
    failures.push("Skiper UI selection should include exact item endpoints, namespace commands, or an explicit none/reject row.");
  }
  if (!/terms|access|license|public-registry|reference-only|not MIT/i.test(text)) {
    failures.push("Skiper UI selection should state terms/access/license gate status.");
  }
  if (/(\/preview\/skiper|skiper-ui\.com\/r\/|skiper-ui\.com\/registry\.json)/i.test(text) && !/not used|404|reject|not use|no|wrong/i.test(text)) {
    failures.push("Skiper UI selection should not use broken preview or wrong registry paths as valid install evidence.");
  }
}

const eldoraUiSelection = path.join(planDir, "45-eldora-ui-selection.md");
if (fs.existsSync(eldoraUiSelection)) {
  const text = fs.readFileSync(eldoraUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Eldora UI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Reduced-motion Fallback", "Mobile Behavior", "Performance Risk"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Eldora UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Eldora UI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Eldora UI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Eldora UI selection should map selections to change IDs.");
  }
  const hasEldoraEvidence = /eldoraui\.site\/r\/[^ \n|)]+\.json|@eldoraui\//i.test(text);
  const hasExplicitNoEldoraRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasEldoraEvidence && !hasExplicitNoEldoraRow) {
    failures.push("Eldora UI selection should include exact item endpoints, namespace commands, or an explicit none/reject row.");
  }
  if (!/MIT|license|reference-only|public/i.test(text)) {
    failures.push("Eldora UI selection should state license gate status.");
  }
  if (/eldoraui\.site\/registry\/[^ \n|)]+\.json/i.test(text) && !/not used|404|reject|not use|no|wrong/i.test(text)) {
    failures.push("Eldora UI selection should not use the wrong /registry/<name>.json path as valid install evidence.");
  }
}

const blocksSoSelection = path.join(planDir, "46-blocks-so-selection.md");
if (fs.existsSync(blocksSoSelection)) {
  const text = fs.readFileSync(blocksSoSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Blocks.so Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "Demo-data Replacement", "Accessibility Notes", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term.replace(".", "\\."), "i").test(text)) {
      failures.push(`Blocks.so selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Blocks.so selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Blocks.so selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Blocks.so selection should map selections to change IDs.");
  }
  const hasBlocksSoEvidence = /blocks\.so\/r\/[^ \n|)]+\.json|@blocks-so\//i.test(text);
  const hasExplicitNoBlocksSoRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasBlocksSoEvidence && !hasExplicitNoBlocksSoRow) {
    failures.push("Blocks.so selection should include exact item endpoints, namespace commands, or an explicit none/reject row.");
  }
  if (!/MIT|license|reference-only|public/i.test(text)) {
    failures.push("Blocks.so selection should state license gate status.");
  }
  if (!/fake proof|demo data|demo-data|real project content|replaced/i.test(text)) {
    failures.push("Blocks.so selection should state demo-data replacement and fake proof handling.");
  }
  if (/blocks\.so\/r\/registry\.json/i.test(text) && !/not used|reset|ECONNRESET|reject|not use|no/i.test(text)) {
    failures.push("Blocks.so selection should not use the live registry index body as item evidence.");
  }
}

const intentUiSelection = path.join(planDir, "47-intent-ui-selection.md");
if (fs.existsSync(intentUiSelection)) {
  const text = fs.readFileSync(intentUiSelection, "utf8");
  const requiredTerms = ["Selection Summary", "Candidate Intent UI Items", "Installation Queue", "Runtime And Style Gate", "Rejected Items", "License And Adaptation Notes", "React Aria", "Accessibility Notes", "Mobile Behavior"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Intent UI selection should mention ${term}.`);
    }
  }
  if (!/accept|adapt|reject|backlog|none|reference-only/i.test(text)) {
    failures.push("Intent UI selection should include explicit candidate decisions.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Intent UI selection should map selections to task IDs.");
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Intent UI selection should map selections to change IDs.");
  }
  const hasIntentUiEvidence = /intentui\.com\/r\/[^ \n|)]+|@intentui\//i.test(text);
  const hasExplicitNoIntentUiRow = /\|\s*none\s*\|[^\n]*(reject|reference-only)/i.test(text);
  if (!hasIntentUiEvidence && !hasExplicitNoIntentUiRow) {
    failures.push("Intent UI selection should include exact item endpoints, namespace commands, or an explicit none/reject row.");
  }
  if (!/MIT|license|reference-only|public/i.test(text)) {
    failures.push("Intent UI selection should state license gate status.");
  }
  if (!/react-aria-components|React Aria/i.test(text)) {
    failures.push("Intent UI selection should state React Aria dependency impact.");
  }
  if (/@intentui\/all|\bintentui\.com\/r\/all\b/i.test(text) && !/not used|reject|not use|no/i.test(text)) {
    failures.push("Intent UI selection should not use @intentui/all as valid install evidence.");
  }
  if (/registry:page/i.test(text) && !/reference-only|reject|not production|example/i.test(text)) {
    failures.push("Intent UI selection should treat registry:page examples as reference-only unless explicitly justified.");
  }
}

const visualStyleTile = path.join(planDir, "17-visual-style-tile.md");
if (fs.existsSync(visualStyleTile)) {
  const text = fs.readFileSync(visualStyleTile, "utf8");
  const requiredTerms = ["Typography", "Color", "Spacing", "Radius", "Surface", "Assets", "Motion"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Visual style tile should mention ${term}.`);
    }
  }
  if (!/Reading this as/i.test(text)) {
    failures.push("Visual style tile should include a visual read.");
  }
}

const sectionStoryboard = path.join(planDir, "18-section-storyboard-canvas.md");
if (fs.existsSync(sectionStoryboard)) {
  const text = fs.readFileSync(sectionStoryboard, "utf8");
  const requiredTerms = ["User job", "Frame sketch", "Copy/proof", "Visual style", "Asset", "Reference", "Motion", "Mobile", "QA"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Section storyboard canvas should mention ${term}.`);
    }
  }
}

const assetProductionQueue = path.join(planDir, "19-asset-production-queue.md");
if (fs.existsSync(assetProductionQueue)) {
  const text = fs.readFileSync(assetProductionQueue, "utf8");
  const requiredTerms = ["Asset", "Section", "Role", "Type", "Source", "Spec", "Alt text", "Performance", "Status", "QA"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Asset production queue should mention ${term}.`);
    }
  }
}

const responsiveViewportMap = path.join(planDir, "27-responsive-viewport-map.md");
if (fs.existsSync(responsiveViewportMap)) {
  const text = fs.readFileSync(responsiveViewportMap, "utf8");
  const requiredTerms = ["Viewport Set", "First Viewport Plan", "Section Transformations", "Typography And UI Fit", "Asset Crop Rules", "Overflow And Sticky Risk Register", "Screenshot QA Matrix", "Task Graph Updates", "mobile", "tablet", "wide"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Responsive viewport map should mention ${term}.`);
    }
  }
}

const implementationTaskGraph = path.join(planDir, "20-implementation-task-graph.md");
if (fs.existsSync(implementationTaskGraph)) {
  const text = fs.readFileSync(implementationTaskGraph, "utf8");
  const requiredTerms = ["Task ID", "Change IDs", "Ring", "Blocked by", "Blocks", "Files or routes", "Plan sources", "Visible result", "Verification", "Evidence", "Screenshot Matrix", "Dependency Budget"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Implementation task graph should mention ${term}.`);
    }
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Implementation task graph should include stable task IDs.");
  }
}

const changeTraceabilityMatrix = path.join(planDir, "28-change-traceability-matrix.md");
if (fs.existsSync(changeTraceabilityMatrix)) {
  const text = fs.readFileSync(changeTraceabilityMatrix, "utf8");
  const requiredTerms = ["Traceability Summary", "Change Inventory", "Source Evidence Links", "Implementation Mapping", "QA Mapping", "Protected Change Review", "Orphan Or Blocked Decisions", "Handoff Notes"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Change traceability matrix should mention ${term}.`);
    }
  }
  if (!/chg-\d{3}/i.test(text)) {
    failures.push("Change traceability matrix should include stable change IDs.");
  }
  if (!/task-\d{3}/i.test(text)) {
    failures.push("Change traceability matrix should map changes to task IDs.");
  }
}

const planSelfReview = path.join(planDir, "21-plan-self-review.md");
if (fs.existsSync(planSelfReview)) {
  const text = fs.readFileSync(planSelfReview, "utf8");
  const requiredTerms = ["readiness verdict", "Review Scorecard", "Blocking Findings", "Generic Language Sweep", "Reference To Decision", "Motion And Asset", "Required Plan Patches", "Handoff Decision"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Plan self-review should mention ${term}.`);
    }
  }
}

const presentationQualityReview = path.join(planDir, "23-presentation-quality-review.md");
if (fs.existsSync(presentationQualityReview)) {
  const text = fs.readFileSync(presentationQualityReview, "utf8");
  const requiredTerms = ["presentation verdict", "First impression", "Above the fold", "Visual hierarchy", "Trust and credibility", "Distinctiveness", "Reference Translation", "Motion And Interaction", "Asset Presentation", "Final Decision"];
  for (const term of requiredTerms) {
    if (!new RegExp(term, "i").test(text)) {
      failures.push(`Presentation quality review should mention ${term}.`);
    }
  }
}

if (warnings.length) {
  console.log("Warnings:");
  for (const warning of warnings) console.log(`- ${warning}`);
}

if (failures.length) {
  console.error("Landing plan check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Landing plan check passed.");

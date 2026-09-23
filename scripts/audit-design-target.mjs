#!/usr/bin/env node

import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";

const packetFiles = [
  "DESIGN_AGENT_HANDOFF.md",
  ".design-agent/README.md",
  ".design-agent/prompt.txt",
  ".design-agent/working-brief.md",
  ".design-agent/manifest.json",
  ".design-agent/acceptance-checklist.md",
  ".design-agent/final-report-template.md",
  ".design-agent/AGENTS_SNIPPET.md",
];

const briefRequiredLabels = [
  "Stack",
  "Main package scripts",
  "Existing routes/screens",
  "Existing components/tokens",
  "Browser/dev-server command",
  "Surface type",
  "Closest product surface blueprint",
  "Landing-page patterns allowed? yes/no and why",
  "Primary user",
  "Primary job",
  "Core loop",
  "Product object model",
  "Visual system contract",
  "Route/screen/workflow to change",
  "Primary object",
  "User action path",
  "Route/screen",
  "Screen recipe/state specs",
  "Local files to inspect/change",
  "Component state plan",
  "Data/fixture truth",
  "Actions",
  "Commands to run",
  "Screenshots/browser evidence to capture",
  "Trusted vertical segment",
  "Source-of-truth objects",
  "False-state risks",
  "Proof/evidence surfaces",
  "After-state",
  "Recovery path",
  "External AI is proposal-only until",
  "Preview/diff visible",
  "Verification visible",
  "Human approval visible",
  "Transaction/ledger evidence visible",
  "Agent connection/scopes visible",
  "Comment-to-task bridge visible",
  "Pending proposal/approval bridge visible",
  "Failure/recovery handling visible",
  "Export/reopen path",
  "Top-design target",
  "Five-second test target",
  "Primary object/state/next action",
  "Weakest expected visual category",
  "Mediocrity risks to avoid",
  "Product-specific details to make distinctive",
  "Browser routes",
  "Known remaining risks",
];

const finalRequiredLabels = [
  "PASS / PASS WITH RISKS / FAIL",
  "Surface classified",
  "Product read",
  "Workflow improved",
  "Files changed",
  "Information architecture checked",
  "Interaction model checked",
  "Copy/status language checked",
  "Decision/review cockpit checked",
  "Trusted vertical checked",
  "AI source-of-truth/false-state risks checked",
  "Top-design benchmark checked",
  "Five-second test",
  "Mediocrity risks fixed",
  "Product-specific details",
  "Operational pattern checked",
  "Object model checked",
  "Visual system checked",
  "Implementation slice contract",
  "State coverage checked",
  "Component state evidence checked",
  "Commands run",
  "Project command evidence",
  "Command evidence artifacts",
  "Browser routes checked",
  "Screenshots/browser checks",
  "Visual evidence verdict",
  "Evidence artifacts",
  "Rubric score",
  "Remaining risks",
];

function usage() {
  console.log("Usage: node scripts/audit-design-target.mjs <target-project-path> [--write]");
}

function parseArgs(argv) {
  let targetPath = "";
  let write = false;

  for (const arg of argv) {
    if (arg === "--help" || arg === "-h") {
      return { help: true, targetPath, write };
    }

    if (arg === "--write") {
      write = true;
      continue;
    }

    if (!targetPath) {
      targetPath = arg;
    }
  }

  return { help: false, targetPath, write };
}

function targetFile(targetRoot, relativePath) {
  return path.join(targetRoot, ...relativePath.split("/"));
}

function readText(filePath) {
  return readFileSync(filePath, "utf8");
}

function readTarget(targetRoot, relativePath) {
  return readText(targetFile(targetRoot, relativePath));
}

function existsTarget(targetRoot, relativePath) {
  return existsSync(targetFile(targetRoot, relativePath));
}

function extractLabelValue(markdown, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`^(?:[-*][ \\t]*)?${escaped}:[ \\t]*(.*)$`, "im");
  const match = regex.exec(markdown);
  if (!match) {
    return "";
  }

  const sameLineValue = match[1]?.trim() ?? "";
  if (sameLineValue) {
    return sameLineValue;
  }

  const continuationLines = [];
  const afterLabel = markdown.slice(match.index + match[0].length);
  for (const line of afterLabel.split(/\r?\n/)) {
    const trimmed = line.trim();

    if (!trimmed) {
      if (continuationLines.length > 0) {
        break;
      }
      continue;
    }

    if (/^#{1,6}\s/.test(trimmed) || /^```/.test(trimmed)) {
      break;
    }

    if (/^(?:[-*][ \t]*)?[A-ZА-Я][^:\n]{1,80}:[ \t]*/.test(trimmed)) {
      break;
    }

    continuationLines.push(trimmed.replace(/^[-*][ \t]*/, ""));
    if (continuationLines.length >= 20) {
      break;
    }
  }

  return continuationLines.join("; ").trim();
}

function isUnfilled(value) {
  const normalized = value.trim().toLowerCase();
  return [
    "",
    "-",
    "--",
    "...",
    "todo",
    "tbd",
    "unknown",
    "not sure",
    "???",
    "<todo>",
    "<fill>",
    "<fill me>",
  ].includes(normalized);
}

function isWeakGenericEvidence(value) {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[.!?]+$/g, "")
    .replace(/\s+/g, " ");

  if (isUnfilled(value)) {
    return true;
  }

  const weakPhrases = new Set([
    "yes",
    "checked",
    "done",
    "ok",
    "okay",
    "passed",
    "pass",
    "complete",
    "completed",
    "fixed",
    "improved",
    "improve ui",
    "make better",
    "better design",
    "good design",
    "use app",
    "looks good",
    "looks fine",
    "all good",
    "no issues",
    "n/a",
    "na",
    "not applicable",
  ]);

  if (weakPhrases.has(normalized)) {
    return true;
  }

  const words = normalized.split(/\s+/).filter(Boolean);
  if (words.length < 5) {
    const weakTokens = new Set([
      "yes",
      "checked",
      "done",
      "ok",
      "passed",
      "pass",
      "fixed",
      "improved",
      "improve",
      "good",
      "better",
      "design",
      "ui",
      "app",
    ]);
    return words.every((word) => weakTokens.has(word));
  }

  return false;
}

function missingFilledLabels(markdown, labels) {
  return labels.filter((label) => isUnfilled(extractLabelValue(markdown, label)));
}

function splitArtifactCandidates(value) {
  return value
    .split(/[;,]/)
    .map((part) => part.trim())
    .map((part) => part.replace(/^[-*]\s*/, ""))
    .map((part) => part.replace(/^["'`]+|["'`.:]+$/g, ""))
    .filter(Boolean)
    .filter((part) => /[\\/]|\.png$|\.jpe?g$|\.webp$|\.gif$|\.mp4$|\.webm$|\.json$|\.html$|\.txt$|\.md$|\.log$/i.test(part));
}

function splitChangedFileCandidates(value) {
  return value
    .split(/[;,\n]/)
    .map((part) => part.trim())
    .map((part) => part.replace(/^[-*]\s*/, ""))
    .map((part) => {
      const markdownLink = part.match(/^\[[^\]]+\]\(([^)]+)\)$/);
      return markdownLink?.[1] ?? part;
    })
    .map((part) => part.replace(/^["'`]+|["'`.:]+$/g, ""))
    .map((part) => part.replace(/^\.\//, ""))
    .map((part) => {
      const pathMatch = part.match(/(?:[A-Za-z]:[\\/])?[\w@.+() -]+(?:[\\/][\w@.+() -]+)+\.[A-Za-z0-9]+/);
      return pathMatch?.[0] ?? part;
    })
    .filter(Boolean)
    .filter((part) => !/^(none|n\/a|not applicable|no files changed|qa only)$/i.test(part))
    .filter((part) => /[\\/].+\.[A-Za-z0-9]+$/.test(part) || /^\w[\w.-]*\.[A-Za-z0-9]+$/.test(part));
}

function extractRouteCandidates(value) {
  const routes = [];
  const regex = /(?:^|[\s"'`(])((?:https?:\/\/[^/\s"'`),;]+)?\/[A-Za-z0-9._~!$&'()*+,;=:@/%-]*)(?=[\s"'`),;.]|$)/g;
  let match = regex.exec(value);

  while (match) {
    const route = normalizeRouteCandidate(match[1]);
    if (route) {
      routes.push(route);
    }
    match = regex.exec(value);
  }

  return [...new Set(routes)];
}

function normalizeRouteCandidate(route) {
  let normalized = route.trim().replace(/^["'`]+|["'`.,;:]+$/g, "");

  if (/^https?:\/\//i.test(normalized)) {
    try {
      const parsed = new URL(normalized);
      normalized = `${parsed.pathname}${parsed.search}${parsed.hash}`;
    } catch {
      return "";
    }
  }

  if (!normalized.startsWith("/")) {
    return "";
  }

  if (normalized.length > 1) {
    normalized = normalized.replace(/\/+$/, "");
  }

  if (/\.(?:png|jpe?g|webp|gif|mp4|webm|json|html|txt|md|log|tsx?|jsx?|css|scss|svg|ico|woff2?)$/i.test(normalized)) {
    return "";
  }

  if (/^\/(?:src|public|docs|qa|node_modules|\.design-agent|\.next)(?:\/|$)/i.test(normalized)) {
    return "";
  }

  return normalized || "/";
}

function routeBase(route) {
  const [withoutHash] = route.split("#");
  const [withoutQuery] = withoutHash.split("?");
  return withoutQuery.length > 1 ? withoutQuery.replace(/\/+$/, "") : "/";
}

function routesMatch(expected, checked) {
  return routeBase(expected) === routeBase(checked);
}

const stateAliases = [
  { name: "loaded", pattern: /\b(loaded|load|entry|default)\b/i },
  { name: "empty", pattern: /\b(empty|no data|no project|zero state|blank state)\b/i },
  { name: "loading", pattern: /\b(loading|skeleton|spinner|running|scan running)\b/i },
  { name: "error", pattern: /\b(error|failed|failure|invalid|render error)\b/i },
  { name: "disabled", pattern: /\b(disabled|unavailable|locked|blocked)\b/i },
  { name: "selected", pattern: /\b(selected|selection|focused|focus)\b/i },
  { name: "hover", pattern: /\bhover\b/i },
  { name: "pending", pattern: /\b(pending|queued|in progress|processing)\b/i },
  { name: "success", pattern: /\b(success|successful|approved|applied|completed|complete)\b/i },
  { name: "retry", pattern: /\b(retry|undo|rollback|restore|reopen|recovery)\b/i },
  { name: "stale", pattern: /\bstale\b/i },
  { name: "disconnected", pattern: /\b(disconnected|offline|no agent)\b/i },
  { name: "permission", pattern: /\b(permission|denied|access denied|unauthorized)\b/i },
];

function extractStateNames(value) {
  const states = [];

  for (const { name, pattern } of stateAliases) {
    if (pattern.test(value)) {
      states.push(name);
    }
  }

  return [...new Set(states)];
}

const rubricCategories = [
  "Surface fit",
  "Workflow clarity",
  "Information architecture",
  "Interaction model",
  "Copy/status clarity",
  "Decision/review support",
  "Information hierarchy",
  "State coverage",
  "Component craft",
  "Data/proof honesty",
  "Accessibility",
  "Responsive behavior",
  "Visual system",
  "Motion/feedback",
  "Evidence",
];

function inspectRubricScore(finalReportText) {
  const rubricValue = extractLabelValue(finalReportText, "Rubric score");
  const scoreFromSlash = rubricValue.match(/\b(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)\b/);
  const scoreFromTotal = rubricValue.match(/\bTotal\s*:\s*(\d+(?:\.\d+)?)(?:\s*\/\s*(\d+(?:\.\d+)?))?\b/i) ??
    finalReportText.match(/^Total\s*:\s*(\d+(?:\.\d+)?)(?:\s*\/\s*(\d+(?:\.\d+)?))?\b/im);
  let score = null;
  let max = null;

  if (scoreFromSlash) {
    score = Number(scoreFromSlash[1]);
    max = Number(scoreFromSlash[2]);
  } else if (scoreFromTotal) {
    score = Number(scoreFromTotal[1]);
    max = scoreFromTotal[2] ? Number(scoreFromTotal[2]) : 30;
  }

  const normalizedScore = score !== null && max && max > 0 ? (score / max) * 30 : score;
  const blockingCategoriesValue = extractLabelValue(finalReportText, "Blocking categories");
  const blockingCategories = isUnfilled(blockingCategoriesValue) || /^(none|no|n\/a|not applicable)$/i.test(blockingCategoriesValue.trim())
    ? ""
    : blockingCategoriesValue;
  const zeroCategories = rubricCategories.filter((category) => {
    const escaped = category.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`\\b${escaped}\\b\\s*(?:[:=]|-)??\\s*0\\b`, "i").test(finalReportText);
  });

  return {
    value: rubricValue,
    score,
    max,
    normalizedScore,
    blockingCategories,
    zeroCategories,
  };
}

function resolveArtifactPath(targetPath, artifactPath) {
  return path.isAbsolute(artifactPath) ? artifactPath : targetFile(targetPath, artifactPath);
}

function resolveChangedFilePath(targetPath, changedFile) {
  return path.isAbsolute(changedFile) ? changedFile : targetFile(targetPath, changedFile);
}

function isInsideTarget(targetPath, filePath) {
  const relativePath = path.relative(path.resolve(targetPath), path.resolve(filePath));
  return relativePath === "" || (!relativePath.startsWith("..") && !path.isAbsolute(relativePath));
}

function getArtifactExtension(artifactPath) {
  return path.extname(artifactPath).toLowerCase();
}

function isVisualArtifactPath(artifactPath) {
  return [".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm"].includes(getArtifactExtension(artifactPath));
}

function isManualInspectionArtifactPath(artifactPath) {
  return [".md", ".txt", ".html", ".json"].includes(getArtifactExtension(artifactPath));
}

function isCommandArtifactPath(artifactPath) {
  return [".log", ".txt", ".md", ".html", ".json"].includes(getArtifactExtension(artifactPath));
}

function bufferStartsWith(buffer, bytes) {
  return bytes.every((byte, index) => buffer[index] === byte);
}

function hasAsciiAt(buffer, offset, value) {
  return buffer.toString("ascii", offset, offset + value.length) === value;
}

function isValidVisualArtifact(filePath) {
  const extension = getArtifactExtension(filePath);
  const buffer = readFileSync(filePath);

  if (buffer.length === 0) {
    return false;
  }

  if (extension === ".png") {
    return buffer.length >= 8 && bufferStartsWith(buffer, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  }

  if (extension === ".jpg" || extension === ".jpeg") {
    return buffer.length >= 3 && bufferStartsWith(buffer, [0xff, 0xd8, 0xff]);
  }

  if (extension === ".webp") {
    return buffer.length >= 12 && hasAsciiAt(buffer, 0, "RIFF") && hasAsciiAt(buffer, 8, "WEBP");
  }

  if (extension === ".gif") {
    return buffer.length >= 6 && (hasAsciiAt(buffer, 0, "GIF87a") || hasAsciiAt(buffer, 0, "GIF89a"));
  }

  if (extension === ".mp4") {
    return buffer.length >= 12 && hasAsciiAt(buffer, 4, "ftyp");
  }

  if (extension === ".webm") {
    return buffer.length >= 4 && bufferStartsWith(buffer, [0x1a, 0x45, 0xdf, 0xa3]);
  }

  return false;
}

function isValidManualInspectionArtifact(filePath) {
  const extension = getArtifactExtension(filePath);
  const buffer = readFileSync(filePath);

  if (buffer.length === 0) {
    return false;
  }

  let text = "";
  if (extension === ".json") {
    try {
      text = JSON.stringify(JSON.parse(buffer.toString("utf8")));
    } catch {
      return false;
    }
  } else if ([".md", ".txt", ".html"].includes(extension)) {
    text = buffer.toString("utf8");
  } else {
    return false;
  }

  return isSubstantiveManualInspectionText(text);
}

function isValidCommandArtifact(filePath) {
  const extension = getArtifactExtension(filePath);
  const buffer = readFileSync(filePath);

  if (buffer.length === 0) {
    return false;
  }

  if (extension === ".json") {
    try {
      JSON.parse(buffer.toString("utf8"));
      return true;
    } catch {
      return false;
    }
  }

  return [".log", ".txt", ".md", ".html"].includes(extension);
}

function isSubstantiveManualInspectionText(text) {
  const normalized = text.toLowerCase();
  const hasRouteOrScreen = /(?:^|[\s"'`(])\/[a-z0-9._~!$&'()*+,;=:@/%-]+/im.test(text) ||
    /\b(route|routes|screen|screens|page|pages|url|browser route|маршрут|маршруты|экран|экраны|страница|страницы)\b/i.test(text);
  const hasViewport = /\b(desktop|tablet|mobile|viewport|viewports|wide|narrow|десктоп|планшет|мобайл|мобильн|вьюпорт)\b/i.test(text) ||
    /\b\d{3,4}\s*x\s*\d{3,4}\b/.test(normalized);
  const hasVisualCheck = /\b(checked|inspected|manual|visual|layout|responsive|overlap|clipping|clip|focus|keyboard|contrast|blank|spacing|провер|ручн|визуал|макет|адаптив|перекры|обрез|фокус|клавиатур|контраст|пуст|спейсинг)\b/i.test(text);

  return hasRouteOrScreen && hasViewport && hasVisualCheck;
}

function inspectEvidenceArtifacts(targetPath, finalReportText) {
  const combined = [
    extractLabelValue(finalReportText, "Evidence artifacts"),
    extractLabelValue(finalReportText, "Screenshots/browser checks"),
  ].join("; ");
  const artifacts = [...new Set(splitArtifactCandidates(combined))];
  const existing = [];
  const missing = [];
  const validVisual = [];
  const invalidVisual = [];
  const validManual = [];
  const invalidManual = [];

  for (const artifact of artifacts) {
    const artifactPath = resolveArtifactPath(targetPath, artifact);
    if (existsSync(artifactPath) && statSync(artifactPath).isFile() && statSync(artifactPath).size > 0) {
      existing.push(artifact);
      if (isVisualArtifactPath(artifact)) {
        if (isValidVisualArtifact(artifactPath)) {
          validVisual.push(artifact);
        } else {
          invalidVisual.push(artifact);
        }
      }
      if (isManualInspectionArtifactPath(artifact)) {
        if (isValidManualInspectionArtifact(artifactPath)) {
          validManual.push(artifact);
        } else {
          invalidManual.push(artifact);
        }
      }
    } else {
      missing.push(artifact);
    }
  }

  return { artifacts, existing, missing, validVisual, invalidVisual, validManual, invalidManual };
}

function inspectCommandArtifacts(targetPath, finalReportText) {
  const artifacts = [...new Set(splitArtifactCandidates(extractLabelValue(finalReportText, "Command evidence artifacts")))];
  const existing = [];
  const missing = [];
  const validCommand = [];
  const invalidCommand = [];

  for (const artifact of artifacts) {
    const artifactPath = resolveArtifactPath(targetPath, artifact);
    if (existsSync(artifactPath) && statSync(artifactPath).isFile() && statSync(artifactPath).size > 0) {
      existing.push(artifact);
      if (isCommandArtifactPath(artifact)) {
        if (isValidCommandArtifact(artifactPath)) {
          validCommand.push(artifact);
        } else {
          invalidCommand.push(artifact);
        }
      } else {
        invalidCommand.push(artifact);
      }
    } else {
      missing.push(artifact);
    }
  }

  return { artifacts, existing, missing, validCommand, invalidCommand };
}

function inspectChangedFiles(targetPath, finalReportText) {
  const files = [...new Set(splitChangedFileCandidates(extractLabelValue(finalReportText, "Files changed")))];
  const existing = [];
  const missing = [];
  const outsideTarget = [];
  const notFiles = [];

  for (const file of files) {
    const filePath = resolveChangedFilePath(targetPath, file);
    if (!isInsideTarget(targetPath, filePath)) {
      outsideTarget.push(file);
      continue;
    }

    if (!existsSync(filePath)) {
      missing.push(file);
      continue;
    }

    if (!statSync(filePath).isFile()) {
      notFiles.push(file);
      continue;
    }

    existing.push(file);
  }

  return { files, existing, missing, outsideTarget, notFiles };
}

function inspectRouteConsistency(targetPath, finalReportText) {
  if (!existsTarget(targetPath, ".design-agent/working-brief.md")) {
    return { briefRoutes: [], finalRoutes: [], missingFromFinal: [] };
  }

  const briefText = readTarget(targetPath, ".design-agent/working-brief.md");
  const briefRoutes = [
    ...extractRouteCandidates(extractLabelValue(briefText, "Route/screen/workflow to change")),
    ...extractRouteCandidates(extractLabelValue(briefText, "Route/screen")),
    ...extractRouteCandidates(extractLabelValue(briefText, "Browser routes")),
  ];
  const uniqueBriefRoutes = [...new Set(briefRoutes)];
  const finalRoutes = extractRouteCandidates(extractLabelValue(finalReportText, "Browser routes checked"));
  const missingFromFinal = uniqueBriefRoutes.filter(
    (briefRoute) => !finalRoutes.some((finalRoute) => routesMatch(briefRoute, finalRoute)),
  );

  return { briefRoutes: uniqueBriefRoutes, finalRoutes, missingFromFinal };
}

function inspectStateConsistency(targetPath, finalReportText) {
  if (!existsTarget(targetPath, ".design-agent/working-brief.md")) {
    return { briefStates: [], finalStates: [], missingFromFinal: [] };
  }

  const briefText = readTarget(targetPath, ".design-agent/working-brief.md");
  const includedStates = extractStateNames(extractLabelValue(briefText, "Included states"));
  const deferredStates = new Set(extractStateNames(extractLabelValue(briefText, "Deferred states")));
  const briefStates = includedStates.filter((state) => !deferredStates.has(state));
  const finalStates = [
    ...extractStateNames(extractLabelValue(finalReportText, "State coverage checked")),
    ...extractStateNames(extractLabelValue(finalReportText, "States checked")),
  ];
  const uniqueFinalStates = [...new Set(finalStates)];
  const missingFromFinal = briefStates.filter((state) => !uniqueFinalStates.includes(state));

  return { briefStates, finalStates: uniqueFinalStates, missingFromFinal };
}

const substantiveBriefLabels = [
  "Existing routes/screens",
  "Existing components/tokens",
  "Browser/dev-server command",
  "Surface type",
  "Closest product surface blueprint",
  "Landing-page patterns allowed? yes/no and why",
  "Primary user",
  "Primary job",
  "Core loop",
  "Product object model",
  "Visual system contract",
  "Route/screen/workflow to change",
  "Primary object",
  "User action path",
  "Route/screen",
  "Screen recipe/state specs",
  "Local files to inspect/change",
  "Component state plan",
  "Data/fixture truth",
  "Actions",
  "Commands to run",
  "Screenshots/browser evidence to capture",
  "Top-design target",
  "Five-second test target",
  "Primary object/state/next action",
  "Mediocrity risks to avoid",
  "Product-specific details to make distinctive",
  "Browser routes",
  "Known remaining risks",
];

const briefSignalChecks = [
  {
    name: "product user/job/object",
    pattern: /\b(user|operator|designer|founder|admin|analyst|manager|customer|viewer|editor|reviewer|job|task|object|record|row|proposal|project|asset|document|пользователь|оператор|дизайнер|админ|аналитик|задач|объект|предлож|проект)\b/i,
  },
  {
    name: "workflow/action path",
    pattern: /\b(inspect|decide|act|verify|recover|select|filter|edit|save|approve|revise|retry|export|open|review|compare|workflow|loop|действ|сценар|выбрать|провер|одобр|сравн|экспорт|откры|сохран|повтор)\b/i,
  },
  {
    name: "data/source truth",
    pattern: /\b(data|source|fixture|sample|demo|mock|api|backend|local|file|truth|real|disconnected|unavailable|database|источник|данн|фикстур|пример|демо|мок|файл|бекенд)\b/i,
  },
  {
    name: "object model/lifecycle",
    pattern: /\b(object model|entity|record|status|state|lifecycle|field|attribute|property|owner|permission|event|relationship|history|audit|version|модель|сущност|статус|состояни|поле|атрибут|владел|прав|событ|связ|истори)\b/i,
  },
  {
    name: "visual system/tokens",
    pattern: /\b(visual system|design system|token|typography|spacing|radius|color|status color|contrast|density|icon|border|shadow|motion|type scale|grid|систем|токен|типограф|отступ|радиус|цвет|контраст|плотност|икон|границ|тень)\b/i,
  },
  {
    name: "verification evidence",
    pattern: /\b(command|build|lint|typecheck|test|screenshot|browser|manual|viewport|evidence|artifact|route|команд|сборк|тест|скрин|браузер|ручн|вьюпорт|доказ)\b/i,
  },
  {
    name: "screen selection",
    pattern: /\b(blueprint|recipe|screen|dashboard|admin|table|list|master detail|inspector|canvas|studio|proposal|verification|ledger|export|drawer|form|экран|рецепт|дашборд|таблиц|список|канва|инспектор)\b/i,
  },
  {
    name: "local implementation target",
    pattern: /\b(src|app|pages|routes|components|widgets|features|views|screens|\.tsx|\.jsx|\.vue|\.svelte|\.css|\.scss|route|file|файл|компонент)\b|\/[A-Za-z0-9._~!$&'()*+,;=:@/%-]+/i,
  },
];

const aiInvariantLabels = [
  "External AI is proposal-only until",
  "Preview/diff visible",
  "Verification visible",
  "Human approval visible",
  "Transaction/ledger evidence visible",
  "Agent connection/scopes visible",
  "Comment-to-task bridge visible",
  "Pending proposal/approval bridge visible",
  "Failure/recovery handling visible",
  "Export/reopen path",
];

const aiDesignAppSignalPattern = /\b(forgestudio|ai design|design studio|ai studio|canvas editor|canvas-workbench|workbench|proposal\/diff|preview\/diff|designtransaction|transaction\/ledger|mcp|external ai|agent proposal|agent task|anchored comment|ledger|verification)\b/i;

const aiInvariantSignalChecks = [
  {
    name: "proposal-only",
    pattern: /\b(proposal-only|proposal only|proposal|propose|pending proposal|agent proposal)\b/i,
  },
  {
    name: "preview/diff",
    pattern: /\b(preview\/diff|preview|diff|before\/after|comparison|compare)\b/i,
  },
  {
    name: "verification",
    pattern: /\b(verification|verify|verifier|check|test|screenshot|command evidence)\b/i,
  },
  {
    name: "human approval",
    pattern: /\b(human approval|approval|approve|revise|reject|accepted diff|review decision)\b/i,
  },
  {
    name: "transaction/ledger",
    pattern: /\b(designtransaction|transaction|ledger|history|audit row|accepted transaction)\b/i,
  },
  {
    name: "agent connection/scopes",
    pattern: /\b(agent session|agent connection|agent connected|agent disconnected|connected|disconnected|connecting|scope|scopes|permission|capability|mcp|daemon|provider)\b/i,
  },
  {
    name: "comment-to-task bridge",
    pattern: /\b(comment task|comment-to-task|comment to task|anchored comment|comment|anchor|thread|inbox|agent task|linked comment|revision request)\b/i,
  },
  {
    name: "pending approval bridge",
    pattern: /\b(pending approval|pending proposal|approval bridge|approve-back|approve back|live session|session live|poll|merge|approval queue)\b/i,
  },
  {
    name: "failure/recovery handling",
    pattern: /\b(inline error|inline failure|failure|failed|warning|silent|console\.warn|toast|retry|rollback|reopen|recovery|blocked|reason|permission denied)\b/i,
  },
  {
    name: "export/reopen recovery",
    pattern: /\b(export|reopen|rollback|recover|recovery|history)\b/i,
  },
];

const componentStateEvidenceSignalChecks = [
  {
    name: "component/control",
    pattern: /\b(component|button|icon button|input|select|combobox|table|row|list|tree|layer|card|panel|drawer|dialog|popover|tabs|filter|inspector|field|toolbar|menu|toast|alert|badge|chip|canvas|viewer|component name|компонент|кноп|поле|таблиц|строк|список|дерев|слой|панел|карточ|инспектор|меню|тост|бейдж|чип|канва)\b/i,
  },
  {
    name: "state",
    pattern: /\b(state|states|empty|loading|skeleton|error|failed|disabled|selected|hover|focus|focus-visible|active|pending|success|retry|rollback|stale|disconnected|permission|open|closed|invalid|locked|warning|состояни|загруз|скелет|ошиб|отключ|выбран|фокус|ожидан|успех|повтор|откат|устар|прав|открыт|закрыт|предупреж)\b/i,
  },
  {
    name: "evidence/check",
    pattern: /\b(evidence|screenshot|browser|viewport|manual|keyboard|focus|responsive|artifact|checked|tested|verified|qa|command|route|desktop|mobile|tablet|скрин|браузер|вьюпорт|ручн|клавиатур|фокус|адаптив|артефакт|провер|команд|маршрут|мобил)\b/i,
  },
];

const informationArchitectureSignalChecks = [
  {
    name: "route/screen",
    pattern: /\b(route|routes|screen|screens|page|pages|view|views|workspace|dashboard|admin|studio|editor|маршрут|экран|страниц|вид|воркспейс|дашборд|админ|студи|редактор)\b|\/[a-z0-9/_-]+/i,
  },
  {
    name: "navigation/hierarchy",
    pattern: /\b(navigation|nav|sidebar|rail|breadcrumb|tabs|menu|app shell|shell|hierarchy|object hierarchy|primary|secondary|global|local|навигац|сайдбар|меню|таб|иерарх|объект|основн|вторич)\b/i,
  },
  {
    name: "zones/panels",
    pattern: /\b(zone|zones|panel|panels|drawer|toolbar|table|list|detail|inspector|canvas|content area|main work|review rail|зон|панел|drawer|тулбар|таблиц|список|детал|инспектор|канва|област)\b/i,
  },
  {
    name: "responsive/recovery",
    pattern: /\b(responsive|mobile|tablet|desktop|collapse|stack|drawer|fallback|recovery|history|empty|error|loading|адаптив|мобил|планшет|десктоп|сверн|стек|восстанов|истори|пуст|ошиб|загруз)\b/i,
  },
];

const interactionModelSignalChecks = [
  {
    name: "action/transition",
    pattern: /\b(action|actions|transition|flow|trigger|submit|save|apply|approve|reject|revise|retry|export|filter|select|edit|delete|confirm|open|close|действ|переход|триггер|сохран|примен|одобр|отклон|повтор|экспорт|фильтр|выбор|редакт|удал|подтверд|откры|закры)\b/i,
  },
  {
    name: "pending/success/failure",
    pattern: /\b(pending|loading|submitting|saving|running|success|done|complete|failed|failure|error|warning|blocked|ожидан|загруз|сохран|выполн|успех|готов|заверш|ошиб|сбой|предупреж|заблок)\b/i,
  },
  {
    name: "recovery/permission",
    pattern: /\b(retry|undo|redo|rollback|recover|recovery|reset|reopen|cancel|permission|disabled|denied|locked|повтор|откат|восстанов|сброс|переоткр|отмен|прав|запрещ|отключ|заблок)\b/i,
  },
  {
    name: "object/proximity",
    pattern: /\b(object|row|record|item|selection|selected|local|inline|near|affected|target|job|task|proposal|canvas|layer|entity|объект|строк|запис|элемент|выбран|локаль|рядом|затронут|цель|задач|предлож|канва|слой|сущност)\b/i,
  },
];

const copyStatusLanguageSignalChecks = [
  {
    name: "object",
    pattern: /\b(object|row|record|item|task|job|proposal|asset|file|project|page|export|connection|verification|metric|table|selection|selected|объект|строк|запис|элемент|задач|предлож|файл|проект|страниц|экспорт|соедин|провер|метрик|выбран)\b/i,
  },
  {
    name: "state/status",
    pattern: /\b(state|status|empty|loading|pending|running|success|done|complete|failed|failure|error|warning|stale|disabled|disconnected|sample|demo|ready|blocked|состоян|статус|пуст|загруз|ожидан|выполн|успех|готов|ошиб|сбой|предупреж|устар|отключ|демо|пример|заблок)\b/i,
  },
  {
    name: "reason/next action",
    pattern: /\b(reason|because|why|next action|retry|reconnect|review|approve|revise|reject|open|clear|reset|request access|permission|denied|blocked|fix|choose|download|повтор|переподключ|провер|одобр|исправ|отклон|откры|очист|сброс|доступ|прав|запрещ|причин|почему|следующ)\b/i,
  },
  {
    name: "evidence/source/sample",
    pattern: /\b(evidence|source|proof|sample|demo|fixture|mock|timestamp|updated|actor|command|artifact|path|ledger|history|diff|local|api|backend|доказ|источник|пример|демо|фикстур|мок|время|обнов|команд|артефакт|путь|журнал|истори|локаль|бекенд)\b/i,
  },
];

const decisionReviewCockpitSignalChecks = [
  {
    name: "decision question",
    pattern: /\b(decision|question|decide|review|approval|approve|reject|revise|triage|choose|choice|should|whether|решени|вопрос|выбор|провер|одобр|отклон|исправ|триаж|стоит|нужно ли)\b/i,
  },
  {
    name: "options/comparison",
    pattern: /\b(option|options|comparison|compare|before|after|diff|alternative|variant|approve|revise|reject|retry|export|вариант|сравнен|до|после|дифф|альтернатив|одобр|исправ|отклон|повтор|экспорт)\b/i,
  },
  {
    name: "evidence/risk",
    pattern: /\b(evidence|proof|source|verification|verified|risk|impact|confidence|reason|limit|warning|error|доказ|источник|провер|риск|влияни|уверен|причин|огранич|предупреж|ошиб)\b/i,
  },
  {
    name: "action/after-state/recovery",
    pattern: /\b(action|primary action|secondary action|after-state|after state|next state|audit|recovery|recover|rollback|history|ledger|approve|revise|reject|retry|open|действ|основн|вторич|после|следующ|аудит|восстанов|откат|истори|журнал|одобр|исправ|отклон|повтор|откры)\b/i,
  },
];

const visualSystemEvidenceSignalChecks = [
  {
    name: "typography/type scale",
    pattern: /\b(typography|type|type scale|font|text|heading|label|scale|size|weight|line-height|letter|14px|16px|шрифт|типограф|текст|заголов|лейбл|размер|вес)\b/i,
  },
  {
    name: "spacing/density",
    pattern: /\b(spacing|gap|padding|margin|grid|rhythm|density|compact|comfortable|8px|12px|16px|отступ|интервал|сетка|ритм|плотн|компакт)\b/i,
  },
  {
    name: "surface/radius/border",
    pattern: /\b(surface|surfaces|panel|card|background|layer|radius|rounded|border|divider|stroke|shadow|elevation|6px|8px|поверх|панел|карточ|фон|слой|радиус|границ|бордер|раздел|тень)\b/i,
  },
  {
    name: "color/status/contrast",
    pattern: /\b(color|palette|accent|neutral|status|semantic|success|warning|error|danger|info|pending|contrast|oklch|цвет|палитр|акцент|нейтрал|статус|успех|предупреж|ошиб|контраст)\b/i,
  },
  {
    name: "target-local tokens/components",
    pattern: /\b(token|tokens|css variable|theme|tailwind|class|component|local|existing|shadcn|radix|design system|ui primitive|токен|тема|компонент|локальн|существующ|дизайн-систем)\b/i,
  },
];

function componentStateEvidenceMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return componentStateEvidenceSignalChecks.map(({ name }) => name);
  }

  return componentStateEvidenceSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function visualSystemEvidenceMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return visualSystemEvidenceSignalChecks.map(({ name }) => name);
  }

  return visualSystemEvidenceSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function informationArchitectureMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return informationArchitectureSignalChecks.map(({ name }) => name);
  }

  return informationArchitectureSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function interactionModelMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return interactionModelSignalChecks.map(({ name }) => name);
  }

  return interactionModelSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function copyStatusLanguageMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return copyStatusLanguageSignalChecks.map(({ name }) => name);
  }

  return copyStatusLanguageSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function decisionReviewCockpitMissingSignals(value) {
  if (isWeakGenericEvidence(value)) {
    return decisionReviewCockpitSignalChecks.map(({ name }) => name);
  }

  return decisionReviewCockpitSignalChecks.filter(({ pattern }) => !pattern.test(value)).map(({ name }) => name);
}

function isAiDesignAppBrief(markdown) {
  const surfaceValue = [
    extractLabelValue(markdown, "Surface type"),
    extractLabelValue(markdown, "Is this marketing, product UI, dashboard/admin, editor/canvas, AI design studio, website, 3D/WebGL, or hybrid?"),
    extractLabelValue(markdown, "Route/screen/workflow to change"),
    extractLabelValue(markdown, "Primary object"),
    extractLabelValue(markdown, "Core loop"),
  ].join("; ");
  const invariantValue = [
    extractLabelValue(markdown, "Trusted vertical segment"),
    extractLabelValue(markdown, "Source-of-truth objects"),
    extractLabelValue(markdown, "False-state risks"),
    extractLabelValue(markdown, "Proof/evidence surfaces"),
    ...aiInvariantLabels.map((label) => extractLabelValue(markdown, label)),
  ].join("; ");

  if (aiDesignAppSignalPattern.test(surfaceValue)) {
    return true;
  }

  const invariantValueWithoutNegativeNa = invariantValue.replace(/n\/a\s*-\s*not an ai design app/gi, "");
  if (/n\/a\s*-\s*not an ai design app/i.test(invariantValue) && !aiDesignAppSignalPattern.test(invariantValueWithoutNegativeNa)) {
    return false;
  }

  return aiDesignAppSignalPattern.test(invariantValueWithoutNegativeNa);
}

function isSubstantiveBriefValue(label, value) {
  if (isWeakGenericEvidence(value)) {
    return false;
  }

  if (label === "Landing-page patterns allowed? yes/no and why") {
    return /^(yes|no)\b/i.test(value.trim()) && value.trim().split(/\s+/).length >= 4;
  }

  if (["Route/screen/workflow to change", "Route/screen", "Browser routes"].includes(label)) {
    return extractRouteCandidates(value).length > 0;
  }

  if (label === "Commands to run") {
    return /\b(npm|pnpm|yarn|bun|node|python|pytest|vitest|playwright|build|lint|typecheck|test)\b/i.test(value);
  }

  if (label === "Browser/dev-server command") {
    return /\b(npm|pnpm|yarn|bun|node|python|vite|next|dev|serve|start|localhost|127\.0\.0\.1|http:\/\/|https:\/\/)\b/i.test(value);
  }

  if (label === "Product object model") {
    const hasObject = /\b(object|entity|record|row|proposal|project|page|asset|task|job|file|document|metric|customer|order|invoice|layer|node|comment|объект|сущност|запис|строк|заказ|задач|проект|файл|слой)\b/i.test(value);
    const hasState = /\b(status|state|lifecycle|draft|queued|pending|approved|rejected|failed|resolved|active|inactive|open|closed|retry|error|состояни|статус|жизнен|чернов|очеред|ожидан|одоб|отклон|ошиб|актив|закрыт|повтор)\b/i.test(value);
    const hasShape = /\b(field|attribute|property|id|name|owner|role|permission|timestamp|source|event|relationship|relation|history|audit|version|поле|атрибут|свойств|владел|роль|прав|время|источник|событ|связ|истори|верси)\b/i.test(value);
    return hasObject && hasState && hasShape;
  }

  if (label === "Visual system contract") {
    const hasType = /\b(typography|type|font|text|heading|label|scale|size|weight|типограф|шрифт|текст|заголов|размер|вес)\b/i.test(value);
    const hasSpacing = /\b(spacing|space|gap|padding|margin|grid|rhythm|density|compact|отступ|сетка|ритм|плотност)\b/i.test(value);
    const hasShape = /\b(radius|corner|border|divider|shadow|elevation|surface|радиус|угол|границ|раздел|тень|поверхност)\b/i.test(value);
    const hasColor = /\b(color|palette|accent|neutral|status|success|warning|error|info|contrast|цвет|палитр|акцент|нейтр|статус|успех|предупреж|ошиб|контраст)\b/i.test(value);
    return hasType && hasSpacing && hasShape && hasColor;
  }

  if (label === "Closest product surface blueprint") {
    return /\b(dashboard|admin|saas|workflow|ai design|design studio|canvas|editor|data tool|website|landing|3d|webgl|hybrid|дашборд|админ|студи|канва|редактор|сайт|лендинг)\b/i.test(value);
  }

  if (label === "Screen recipe/state specs") {
    return /\b(recipe|screen|dashboard overview|master detail|admin records|ai design studio|proposal|diff|verification|ledger|export|share|app shell|table|list|drawer|inspector|form|component state|state spec|рецепт|экран|таблиц|список|инспектор|форма|состояни)\b/i.test(value);
  }

  if (label === "Local files to inspect/change") {
    return /\b(src|app|pages|routes|components|widgets|features|views|screens|public|styles|\.tsx|\.jsx|\.ts|\.js|\.vue|\.svelte|\.css|\.scss|файл|компонент)\b|[A-Za-z0-9_.@() -]+[\\/][A-Za-z0-9_.@() -]+/i.test(value);
  }

  if (label === "Component state plan") {
    return /\b(empty|loading|error|disabled|selected|hover|focus|pending|success|retry|rollback|stale|disconnected|permission|skeleton|state|состояни|загруз|ошиб|выбран|фокус|повтор|откат)\b/i.test(value);
  }

  if (label === "Screenshots/browser evidence to capture") {
    return /\b(screenshot|browser|manual|viewport|desktop|tablet|mobile|png|jpg|webp|mp4|скрин|браузер|ручн|вьюпорт)\b/i.test(value);
  }

  return value.trim().split(/\s+/).length >= 2 || extractMeaningfulTerms(value).length > 0;
}

function isSubstantiveAiInvariantValue(label, value) {
  if (isWeakGenericEvidence(value) || /^n\/a\b/i.test(value.trim())) {
    return false;
  }

  const patternByLabel = {
    "External AI is proposal-only until": /\b(proposal-only|proposal only|proposal|preview|diff|verification|approval|approve|transaction|ledger)\b/i,
    "Preview/diff visible": /\b(preview\/diff|preview|diff|before|after|comparison|compare|changed)\b/i,
    "Verification visible": /\b(verification|verify|verifier|check|test|screenshot|command|evidence)\b/i,
    "Human approval visible": /\b(human|approval|approve|revise|reject|decision|review)\b/i,
    "Transaction/ledger evidence visible": /\b(designtransaction|transaction|ledger|history|audit|hash|row)\b/i,
    "Agent connection/scopes visible": /\b(agent session|agent connection|agent connected|agent disconnected|connected|disconnected|connecting|scope|scopes|permission|capability|mcp|daemon|provider)\b/i,
    "Comment-to-task bridge visible": /\b(comment task|comment-to-task|comment to task|anchored comment|comment|anchor|thread|inbox|agent task|linked comment|revision request)\b/i,
    "Pending proposal/approval bridge visible": /\b(pending approval|pending proposal|approval bridge|approve-back|approve back|live session|session live|poll|merge|approval queue)\b/i,
    "Failure/recovery handling visible": /\b(inline error|inline failure|failure|failed|warning|silent|console\.warn|toast|retry|rollback|reopen|recovery|blocked|reason|permission denied)\b/i,
    "Export/reopen path": /\b(export|reopen|rollback|recover|recovery|history|artifact)\b/i,
  };

  return patternByLabel[label]?.test(value) ?? false;
}

function inspectBriefSubstance(markdown) {
  const weakFields = substantiveBriefLabels.filter((label) => !isSubstantiveBriefValue(label, extractLabelValue(markdown, label)));
  const combined = [
    extractLabelValue(markdown, "Primary user"),
    extractLabelValue(markdown, "Primary job"),
    extractLabelValue(markdown, "Core loop"),
    extractLabelValue(markdown, "Product object model"),
    extractLabelValue(markdown, "Visual system contract"),
    extractLabelValue(markdown, "Primary object"),
    extractLabelValue(markdown, "User action path"),
    extractLabelValue(markdown, "Closest product surface blueprint"),
    extractLabelValue(markdown, "Screen recipe/state specs"),
    extractLabelValue(markdown, "Local files to inspect/change"),
    extractLabelValue(markdown, "Component state plan"),
    extractLabelValue(markdown, "Data/fixture truth"),
    extractLabelValue(markdown, "Actions"),
    extractLabelValue(markdown, "Commands to run"),
    extractLabelValue(markdown, "Screenshots/browser evidence to capture"),
  ].join("; ");
  const missingSignals = briefSignalChecks
    .filter(({ pattern }) => !pattern.test(combined))
    .map(({ name }) => name);
  const isAiDesignApp = isAiDesignAppBrief(markdown);
  const aiInvariantCombined = aiInvariantLabels.map((label) => extractLabelValue(markdown, label)).join("; ");
  const weakAiInvariantFields = isAiDesignApp
    ? aiInvariantLabels.filter((label) => !isSubstantiveAiInvariantValue(label, extractLabelValue(markdown, label)))
    : [];
  const missingAiInvariantSignals = isAiDesignApp
    ? aiInvariantSignalChecks.filter(({ pattern }) => !pattern.test(aiInvariantCombined)).map(({ name }) => name)
    : [];

  return { weakFields, missingSignals, isAiDesignApp, weakAiInvariantFields, missingAiInvariantSignals };
}

const topDesignSignalChecks = [
  {
    name: "primary object",
    pattern: /\b(primary object|object|record|row|table|item|task|proposal|canvas|node|layer|comment|project|page|file|asset|screen|route|job|selection|selected|объект|строк|запис|таблиц|задач|предлож|канва|слой|файл|экран|выбран)\b/i,
  },
  {
    name: "state",
    pattern: /\b(state|status|selected|pending|error|failed|failure|loading|success|stale|disconnected|verification|sample|empty|approved|applied|blocked|warning|состоян|статус|выбран|ошиб|загруз|успех|провер|заблок)\b/i,
  },
  {
    name: "next action",
    pattern: /\b(next action|action|approve|revise|retry|export|open|select|filter|save|apply|reject|connect|review|inspect|clear|действ|кноп|выбрать|одобр|экспорт|откры|сохран|повтор|провер)\b/i,
  },
  {
    name: "recovery",
    pattern: /\b(recovery|recover|retry|rollback|undo|reopen|clear|reset|restore|history|ledger|audit|fallback|восстанов|откат|повтор|очист|истор|реестр|журнал)\b/i,
  },
  {
    name: "evidence",
    pattern: /\b(evidence|source|proof|verified|verification|screenshot|artifact|ledger|freshness|path|checklist|command|manual|sample|доказ|источник|провер|скрин|артефакт|путь)\b/i,
  },
];

const topDesignStopWords = new Set([
  "about",
  "action",
  "agent",
  "also",
  "and",
  "avoid",
  "brief",
  "checked",
  "design",
  "details",
  "done",
  "fixed",
  "from",
  "good",
  "improved",
  "into",
  "make",
  "must",
  "next",
  "product",
  "ready",
  "risk",
  "risks",
  "screen",
  "state",
  "states",
  "surface",
  "target",
  "that",
  "this",
  "with",
  "without",
  "специф",
  "детал",
  "дизайн",
  "продукт",
  "риск",
  "состояние",
]);

function extractMeaningfulTerms(value) {
  const matches = value.toLowerCase().match(/[\p{L}\p{N}][\p{L}\p{N}-]{3,}/gu) ?? [];
  return [...new Set(matches)]
    .map((term) => term.replace(/^[-_]+|[-_]+$/g, ""))
    .filter((term) => term.length >= 4)
    .filter((term) => !topDesignStopWords.has(term))
    .slice(0, 24);
}

function findTermOverlap(requiredTerms, value) {
  const normalizedValue = value.toLowerCase();
  const finalTerms = new Set(extractMeaningfulTerms(value));
  return requiredTerms.filter((term) => finalTerms.has(term) || normalizedValue.includes(term));
}

function inspectTopDesignEvidence(targetPath, finalReportText) {
  const briefText = existsTarget(targetPath, ".design-agent/working-brief.md")
    ? readTarget(targetPath, ".design-agent/working-brief.md")
    : "";
  const benchmarkValue = extractLabelValue(finalReportText, "Top-design benchmark checked");
  const fiveSecondValue = extractLabelValue(finalReportText, "Five-second test");
  const risksFixedValue = extractLabelValue(finalReportText, "Mediocrity risks fixed");
  const productDetailsValue = extractLabelValue(finalReportText, "Product-specific details");
  const weakFields = [];

  if (isWeakGenericEvidence(benchmarkValue)) {
    weakFields.push("Top-design benchmark checked");
  }

  if (isWeakGenericEvidence(fiveSecondValue)) {
    weakFields.push("Five-second test");
  }

  if (isWeakGenericEvidence(risksFixedValue)) {
    weakFields.push("Mediocrity risks fixed");
  }

  if (isWeakGenericEvidence(productDetailsValue)) {
    weakFields.push("Product-specific details");
  }

  const fiveSecondMissingSignals = topDesignSignalChecks
    .filter(({ pattern }) => !pattern.test(fiveSecondValue))
    .map(({ name }) => name);
  const briefRiskTerms = extractMeaningfulTerms(extractLabelValue(briefText, "Mediocrity risks to avoid"));
  const briefDetailTerms = extractMeaningfulTerms(extractLabelValue(briefText, "Product-specific details to make distinctive"));
  const riskTermsMatched = findTermOverlap(briefRiskTerms, risksFixedValue);
  const detailTermsMatched = findTermOverlap(briefDetailTerms, productDetailsValue);
  const riskTermsMissing = briefRiskTerms.length > 0 && riskTermsMatched.length === 0 ? briefRiskTerms : [];
  const detailTermsMissing = briefDetailTerms.length > 0 && detailTermsMatched.length === 0 ? briefDetailTerms : [];

  return {
    benchmarkValue,
    fiveSecondValue,
    risksFixedValue,
    productDetailsValue,
    weakFields,
    fiveSecondMissingSignals,
    briefRiskTerms,
    briefDetailTerms,
    riskTermsMatched,
    detailTermsMatched,
    riskTermsMissing,
    detailTermsMissing,
  };
}

const implementationSliceSignalChecks = [
  {
    name: "route or screen",
    pattern: /\b(route|screen|page|view|workflow|surface|workspace|dashboard|admin|editor|studio|маршрут|экран|страниц|воркспейс|дашборд)\b|\/[A-Za-z0-9._~!$&'()*+,;=:@/%-]+/i,
  },
  {
    name: "primary object",
    pattern: /\b(primary object|object|record|row|table|item|task|proposal|canvas|node|layer|comment|project|page|file|asset|metric|form|selection|selected|объект|строк|запис|таблиц|задач|предлож|канва|слой|файл|метрик|выбран)\b/i,
  },
  {
    name: "workflow or action",
    pattern: /\b(workflow|loop|action|select|filter|edit|save|approve|revise|retry|export|open|review|verify|apply|reject|connect|inspect|действ|сценар|выбрать|фильтр|редакт|сохран|одобр|повтор|экспорт|провер|откры)\b/i,
  },
  {
    name: "data or source truth",
    pattern: /\b(data|source|fixture|sample|demo|mock|api|backend|local|file|truth|real|disconnected|unavailable|database|источник|данн|фикстур|пример|демо|мок|файл|бекенд)\b/i,
  },
  {
    name: "state coverage",
    pattern: /\b(state|states|empty|loading|error|selected|pending|success|retry|rollback|disabled|stale|disconnected|состоян|загруз|ошиб|выбран|успех|повтор|откат)\b/i,
  },
  {
    name: "object model",
    pattern: /\b(object model|entity|record|status|state|lifecycle|field|attribute|property|owner|permission|event|relationship|history|audit|version|модель|сущност|статус|состояни|поле|атрибут|владел|прав|событ|связ|истори)\b/i,
  },
];

function collectBriefTerms(markdown, labels) {
  return [...new Set(labels.flatMap((label) => extractMeaningfulTerms(extractLabelValue(markdown, label))))];
}

function inspectImplementationSliceEvidence(targetPath, finalReportText) {
  const briefText = existsTarget(targetPath, ".design-agent/working-brief.md")
    ? readTarget(targetPath, ".design-agent/working-brief.md")
    : "";
  const productReadValue = extractLabelValue(finalReportText, "Product read");
  const workflowValue = extractLabelValue(finalReportText, "Workflow improved");
  const objectModelValue = extractLabelValue(finalReportText, "Object model checked");
  const visualSystemValue = extractLabelValue(finalReportText, "Visual system checked");
  const implementationSliceValue = extractLabelValue(finalReportText, "Implementation slice contract");
  const combinedFinalValue = [productReadValue, workflowValue, objectModelValue, visualSystemValue, implementationSliceValue].join("; ");
  const weakFields = [];

  if (isWeakGenericEvidence(productReadValue)) {
    weakFields.push("Product read");
  }

  if (isWeakGenericEvidence(workflowValue)) {
    weakFields.push("Workflow improved");
  }

  if (isWeakGenericEvidence(objectModelValue)) {
    weakFields.push("Object model checked");
  }

  if (isWeakGenericEvidence(visualSystemValue)) {
    weakFields.push("Visual system checked");
  }

  if (isWeakGenericEvidence(implementationSliceValue)) {
    weakFields.push("Implementation slice contract");
  }

  const missingSignals = implementationSliceSignalChecks
    .filter(({ pattern }) => !pattern.test(implementationSliceValue))
    .map(({ name }) => name);
  const briefObjectTerms = collectBriefTerms(briefText, ["Primary object", "Product object model"]);
  const briefWorkflowTerms = collectBriefTerms(briefText, ["Primary job", "Core loop", "Actions"]);
  const briefDataTerms = collectBriefTerms(briefText, ["Data/fixture truth"]);
  const objectTermsMatched = findTermOverlap(briefObjectTerms, combinedFinalValue);
  const workflowTermsMatched = findTermOverlap(briefWorkflowTerms, combinedFinalValue);
  const dataTermsMatched = findTermOverlap(briefDataTerms, combinedFinalValue);
  const objectTermsMissing = briefObjectTerms.length > 0 && objectTermsMatched.length === 0 ? briefObjectTerms : [];
  const workflowTermsMissing = briefWorkflowTerms.length > 0 && workflowTermsMatched.length === 0 ? briefWorkflowTerms : [];
  const dataTermsMissing = briefDataTerms.length > 0 && dataTermsMatched.length === 0 ? briefDataTerms : [];

  return {
    productReadValue,
    workflowValue,
    objectModelValue,
    visualSystemValue,
    implementationSliceValue,
    weakFields,
    missingSignals,
    briefObjectTerms,
    briefWorkflowTerms,
    briefDataTerms,
    objectTermsMatched,
    workflowTermsMatched,
    dataTermsMatched,
    objectTermsMissing,
    workflowTermsMissing,
    dataTermsMissing,
  };
}

function inspectFinalAiDesignAppEvidence(targetPath, finalReportText) {
  const briefText = existsTarget(targetPath, ".design-agent/working-brief.md")
    ? readTarget(targetPath, ".design-agent/working-brief.md")
    : "";
  const isAiDesignApp = isAiDesignAppBrief(briefText);
  const operationalValue = extractLabelValue(finalReportText, "Operational pattern checked");
  const trustedVerticalValue = extractLabelValue(finalReportText, "Trusted vertical checked");
  const sourceTruthValue = extractLabelValue(finalReportText, "AI source-of-truth/false-state risks checked");
  const combined = [
    trustedVerticalValue,
    sourceTruthValue,
    operationalValue,
    extractLabelValue(finalReportText, "Workflow improved"),
    extractLabelValue(finalReportText, "Implementation slice contract"),
  ].join("; ");
  const weakFields = [];

  if (isAiDesignApp && isWeakGenericEvidence(operationalValue)) {
    weakFields.push("Operational pattern checked");
  }

  if (isAiDesignApp && isWeakGenericEvidence(trustedVerticalValue)) {
    weakFields.push("Trusted vertical checked");
  }

  if (isAiDesignApp && isWeakGenericEvidence(sourceTruthValue)) {
    weakFields.push("AI source-of-truth/false-state risks checked");
  }

  const missingSignals = isAiDesignApp
    ? aiInvariantSignalChecks.filter(({ pattern }) => !pattern.test(combined)).map(({ name }) => name)
    : [];

  return {
    isAiDesignApp,
    operationalValue,
    trustedVerticalValue,
    sourceTruthValue,
    weakFields,
    missingSignals,
  };
}

function inspectComponentStateEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Component state evidence checked");
  return {
    value,
    missingSignals: componentStateEvidenceMissingSignals(value),
  };
}

function inspectVisualSystemEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Visual system checked");
  return {
    value,
    missingSignals: visualSystemEvidenceMissingSignals(value),
  };
}

function inspectInformationArchitectureEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Information architecture checked");
  return {
    value,
    missingSignals: informationArchitectureMissingSignals(value),
  };
}

function inspectInteractionModelEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Interaction model checked");
  return {
    value,
    missingSignals: interactionModelMissingSignals(value),
  };
}

function inspectCopyStatusLanguageEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Copy/status language checked");
  return {
    value,
    missingSignals: copyStatusLanguageMissingSignals(value),
  };
}

function inspectDecisionReviewCockpitEvidence(finalReportText) {
  const value = extractLabelValue(finalReportText, "Decision/review cockpit checked");
  return {
    value,
    missingSignals: decisionReviewCockpitMissingSignals(value),
  };
}

function normalizeChoice(value, allowedValues) {
  const normalized = value.trim().toUpperCase();
  if (normalized.includes(" / ")) {
    return "";
  }

  const sortedAllowedValues = [...allowedValues].sort((left, right) => right.length - left.length);
  return sortedAllowedValues.find(
    (allowedValue) =>
      normalized === allowedValue ||
      normalized.startsWith(`${allowedValue}:`) ||
      normalized.startsWith(`${allowedValue} -`) ||
      normalized.startsWith(`${allowedValue};`) ||
      normalized.startsWith(`${allowedValue},`),
  ) ?? "";
}

function statusLabel(ok, warn = false) {
  if (ok) {
    return "PASS";
  }
  return warn ? "WARN" : "FAIL";
}

function inspectPackage(targetPath) {
  const packagePath = targetFile(targetPath, "package.json");
  if (!existsSync(packagePath)) {
    return {
      found: false,
      stack: "package.json not found",
      scripts: [],
    };
  }

  try {
    const pkg = JSON.parse(readText(packagePath));
    const deps = { ...(pkg.dependencies ?? {}), ...(pkg.devDependencies ?? {}) };
    const stack = [
      deps.next ? `Next ${deps.next}` : "",
      deps.react ? `React ${deps.react}` : "",
      deps.tailwindcss ? `Tailwind ${deps.tailwindcss}` : "",
      deps.three ? `Three ${deps.three}` : "",
    ].filter(Boolean);

    return {
      found: true,
      stack: stack.length > 0 ? stack.join(", ") : "package.json found, stack not recognized",
      scripts: Object.keys(pkg.scripts ?? {}),
    };
  } catch (error) {
    return {
      found: true,
      stack: `package.json invalid: ${error.message}`,
      scripts: [],
    };
  }
}

function inspectPacket(targetPath) {
  const missing = packetFiles.filter((file) => !existsTarget(targetPath, file));
  let promptMode = "";
  let knowledgeBasePath = "";

  if (missing.length === 0) {
    try {
      const manifest = JSON.parse(readTarget(targetPath, ".design-agent/manifest.json"));
      promptMode = manifest.promptMode ?? "";
      knowledgeBasePath = manifest.knowledgeBasePath ?? "";
    } catch {
      missing.push(".design-agent/manifest.json valid JSON");
    }
  }

  return {
    ok: missing.length === 0,
    missing,
    promptMode,
    knowledgeBasePath,
  };
}

function inspectAgentRules(targetPath) {
  if (!existsTarget(targetPath, "AGENTS.md")) {
    return {
      ok: false,
      found: false,
      installed: false,
    };
  }

  const text = readTarget(targetPath, "AGENTS.md");
  return {
    ok: text.includes("<!-- BEGIN:design-agent-packet -->") && text.includes("<!-- END:design-agent-packet -->"),
    found: true,
    installed: text.includes("<!-- BEGIN:design-agent-packet -->"),
  };
}

function inspectBrief(targetPath) {
  if (!existsTarget(targetPath, ".design-agent/working-brief.md")) {
    return {
      ok: false,
      missing: ["file missing"],
      substance: {
        weakFields: [],
        missingSignals: [],
        isAiDesignApp: false,
        weakAiInvariantFields: [],
        missingAiInvariantSignals: [],
      },
    };
  }

  const text = readTarget(targetPath, ".design-agent/working-brief.md");
  const missing = missingFilledLabels(text, briefRequiredLabels);
  const substance = inspectBriefSubstance(text);
  return {
    ok:
      missing.length === 0 &&
      substance.weakFields.length === 0 &&
      substance.missingSignals.length === 0 &&
      substance.weakAiInvariantFields.length === 0 &&
      substance.missingAiInvariantSignals.length === 0,
    missing,
    substance,
  };
}

function inspectFinal(targetPath) {
  if (!existsTarget(targetPath, ".design-agent/final-report-template.md")) {
    return {
      ok: false,
      missing: ["file missing"],
      verdict: "",
      evidenceReady: false,
      evidenceArtifacts: {
        artifacts: [],
        existing: [],
        missing: [],
        validVisual: [],
        invalidVisual: [],
        validManual: [],
        invalidManual: [],
      },
      commandArtifacts: { artifacts: [], existing: [], missing: [], validCommand: [], invalidCommand: [] },
      changedFiles: { files: [], existing: [], missing: [], outsideTarget: [], notFiles: [] },
      routeConsistency: { briefRoutes: [], finalRoutes: [], missingFromFinal: [] },
      stateConsistency: { briefStates: [], finalStates: [], missingFromFinal: [] },
      rubricScore: { value: "", score: null, max: null, normalizedScore: null, blockingCategories: "", zeroCategories: [] },
      implementationSliceEvidence: {
        productReadValue: "",
        workflowValue: "",
        objectModelValue: "",
        visualSystemValue: "",
        implementationSliceValue: "",
        weakFields: [],
        missingSignals: [],
        briefObjectTerms: [],
        briefWorkflowTerms: [],
        briefDataTerms: [],
        objectTermsMatched: [],
        workflowTermsMatched: [],
        dataTermsMatched: [],
        objectTermsMissing: [],
        workflowTermsMissing: [],
        dataTermsMissing: [],
      },
      topDesignEvidence: {
        benchmarkValue: "",
        fiveSecondValue: "",
        risksFixedValue: "",
        productDetailsValue: "",
        weakFields: [],
        fiveSecondMissingSignals: [],
        briefRiskTerms: [],
        briefDetailTerms: [],
        riskTermsMatched: [],
        detailTermsMatched: [],
        riskTermsMissing: [],
        detailTermsMissing: [],
      },
      aiDesignAppEvidence: {
        isAiDesignApp: false,
        operationalValue: "",
        trustedVerticalValue: "",
        sourceTruthValue: "",
        weakFields: [],
        missingSignals: [],
      },
      componentStateEvidence: {
        value: "",
        missingSignals: [],
      },
      visualSystemEvidence: {
        value: "",
        missingSignals: [],
      },
      informationArchitectureEvidence: {
        value: "",
        missingSignals: [],
      },
      interactionModelEvidence: {
        value: "",
        missingSignals: [],
      },
      copyStatusLanguageEvidence: {
        value: "",
        missingSignals: [],
      },
      decisionReviewCockpitEvidence: {
        value: "",
        missingSignals: [],
      },
      evidenceWeaknesses: ["final report missing"],
    };
  }

  const text = readTarget(targetPath, ".design-agent/final-report-template.md");
  const missing = missingFilledLabels(text, finalRequiredLabels);
  const verdict = extractLabelValue(text, "PASS / PASS WITH RISKS / FAIL").toUpperCase();
  const projectCommandEvidence = extractLabelValue(text, "Project command evidence");
  const visualEvidenceVerdict = extractLabelValue(text, "Visual evidence verdict");
  const evidenceArtifacts = inspectEvidenceArtifacts(targetPath, text);
  const commandArtifacts = inspectCommandArtifacts(targetPath, text);
  const changedFiles = inspectChangedFiles(targetPath, text);
  const routeConsistency = inspectRouteConsistency(targetPath, text);
  const stateConsistency = inspectStateConsistency(targetPath, text);
  const rubricScore = inspectRubricScore(text);
  const implementationSliceEvidence = inspectImplementationSliceEvidence(targetPath, text);
  const topDesignEvidence = inspectTopDesignEvidence(targetPath, text);
  const aiDesignAppEvidence = inspectFinalAiDesignAppEvidence(targetPath, text);
  const informationArchitectureEvidence = inspectInformationArchitectureEvidence(text);
  const interactionModelEvidence = inspectInteractionModelEvidence(text);
  const copyStatusLanguageEvidence = inspectCopyStatusLanguageEvidence(text);
  const decisionReviewCockpitEvidence = inspectDecisionReviewCockpitEvidence(text);
  const componentStateEvidence = inspectComponentStateEvidence(text);
  const visualSystemEvidence = inspectVisualSystemEvidence(text);
  const normalizedVerdict = normalizeChoice(verdict, ["PASS", "PASS WITH RISKS", "FAIL"]);
  const normalizedProjectCommandEvidence = normalizeChoice(projectCommandEvidence, [
    "REAL_PROJECT_COMMANDS",
    "NOT_RUN_WITH_RISK",
  ]);
  const normalizedVisualEvidenceVerdict = normalizeChoice(visualEvidenceVerdict, [
    "REAL_BROWSER_SCREENSHOTS",
    "USER_SCREENSHOTS",
    "MANUAL_BROWSER_INSPECTION",
    "NOT_RUN_WITH_RISK",
  ]);
  const evidenceWeaknesses = [];

  if (!normalizedVerdict) {
    evidenceWeaknesses.push("final verdict is not PASS, PASS WITH RISKS, or FAIL");
  }

  if (normalizedVerdict === "FAIL") {
    evidenceWeaknesses.push("final report verdict is FAIL");
  }

  if (changedFiles.files.length === 0) {
    evidenceWeaknesses.push("final report lists no checkable changed file paths");
  }

  if (changedFiles.files.length > 0 && changedFiles.existing.length === 0) {
    evidenceWeaknesses.push("final report has no existing changed files in the target project");
  }

  if (changedFiles.missing.length > 0) {
    evidenceWeaknesses.push(`missing changed files: ${changedFiles.missing.join(", ")}`);
  }

  if (changedFiles.outsideTarget.length > 0) {
    evidenceWeaknesses.push(`changed files outside target project: ${changedFiles.outsideTarget.join(", ")}`);
  }

  if (changedFiles.notFiles.length > 0) {
    evidenceWeaknesses.push(`changed file paths are not files: ${changedFiles.notFiles.join(", ")}`);
  }

  if (routeConsistency.briefRoutes.length > 0 && routeConsistency.finalRoutes.length === 0) {
    evidenceWeaknesses.push("final report lists no checkable browser route paths");
  }

  if (routeConsistency.missingFromFinal.length > 0) {
    evidenceWeaknesses.push(`brief routes not checked in final report: ${routeConsistency.missingFromFinal.join(", ")}`);
  }

  if (stateConsistency.briefStates.length > 0 && stateConsistency.finalStates.length === 0) {
    evidenceWeaknesses.push("final report lists no checkable state coverage");
  }

  if (stateConsistency.missingFromFinal.length > 0) {
    evidenceWeaknesses.push(`brief included states not checked in final report: ${stateConsistency.missingFromFinal.join(", ")}`);
  }

  if (rubricScore.normalizedScore === null || Number.isNaN(rubricScore.normalizedScore)) {
    evidenceWeaknesses.push("rubric score is not numeric");
  } else {
    if (normalizedVerdict === "PASS" && rubricScore.normalizedScore < 26) {
      evidenceWeaknesses.push(`PASS verdict requires rubric score 26+/30, got ${rubricScore.normalizedScore.toFixed(1)}/30`);
    }
    if (rubricScore.normalizedScore < 18) {
      evidenceWeaknesses.push(`rubric score below PASS WITH RISKS threshold: ${rubricScore.normalizedScore.toFixed(1)}/30`);
    }
  }

  if (rubricScore.blockingCategories) {
    evidenceWeaknesses.push(`rubric blocking categories reported: ${rubricScore.blockingCategories}`);
  }

  if (rubricScore.zeroCategories.length > 0) {
    evidenceWeaknesses.push(`rubric categories scored 0: ${rubricScore.zeroCategories.join(", ")}`);
  }

  if (implementationSliceEvidence.weakFields.length > 0) {
    evidenceWeaknesses.push(`weak implementation-slice fields: ${implementationSliceEvidence.weakFields.join(", ")}`);
  }

  if (implementationSliceEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`implementation slice missing signals: ${implementationSliceEvidence.missingSignals.join(", ")}`);
  }

  if (implementationSliceEvidence.objectTermsMissing.length > 0) {
    evidenceWeaknesses.push(
      `implementation slice does not reference brief primary object: ${implementationSliceEvidence.objectTermsMissing.join(", ")}`,
    );
  }

  if (implementationSliceEvidence.workflowTermsMissing.length > 0) {
    evidenceWeaknesses.push(
      `implementation slice does not reference brief workflow/actions: ${implementationSliceEvidence.workflowTermsMissing.join(", ")}`,
    );
  }

  if (implementationSliceEvidence.dataTermsMissing.length > 0) {
    evidenceWeaknesses.push(
      `implementation slice does not reference brief data/source truth: ${implementationSliceEvidence.dataTermsMissing.join(", ")}`,
    );
  }

  if (topDesignEvidence.weakFields.length > 0) {
    evidenceWeaknesses.push(`weak top-design fields: ${topDesignEvidence.weakFields.join(", ")}`);
  }

  if (topDesignEvidence.fiveSecondMissingSignals.length > 0) {
    evidenceWeaknesses.push(`five-second test missing signals: ${topDesignEvidence.fiveSecondMissingSignals.join(", ")}`);
  }

  if (topDesignEvidence.riskTermsMissing.length > 0) {
    evidenceWeaknesses.push(
      `mediocrity risks fixed do not reference brief risks: ${topDesignEvidence.riskTermsMissing.join(", ")}`,
    );
  }

  if (topDesignEvidence.detailTermsMissing.length > 0) {
    evidenceWeaknesses.push(
      `product-specific details do not reference brief details: ${topDesignEvidence.detailTermsMissing.join(", ")}`,
    );
  }

  if (aiDesignAppEvidence.weakFields.length > 0) {
    evidenceWeaknesses.push(`weak AI design app final fields: ${aiDesignAppEvidence.weakFields.join(", ")}`);
  }

  if (aiDesignAppEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`AI design app operational pattern missing signals: ${aiDesignAppEvidence.missingSignals.join(", ")}`);
  }

  if (informationArchitectureEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`information architecture missing signals: ${informationArchitectureEvidence.missingSignals.join(", ")}`);
  }

  if (interactionModelEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`interaction model missing signals: ${interactionModelEvidence.missingSignals.join(", ")}`);
  }

  if (copyStatusLanguageEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`copy/status language missing signals: ${copyStatusLanguageEvidence.missingSignals.join(", ")}`);
  }

  if (decisionReviewCockpitEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`decision/review cockpit missing signals: ${decisionReviewCockpitEvidence.missingSignals.join(", ")}`);
  }

  if (visualSystemEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`visual system missing signals: ${visualSystemEvidence.missingSignals.join(", ")}`);
  }

  if (componentStateEvidence.missingSignals.length > 0) {
    evidenceWeaknesses.push(`component state evidence missing signals: ${componentStateEvidence.missingSignals.join(", ")}`);
  }

  if (normalizedProjectCommandEvidence !== "REAL_PROJECT_COMMANDS") {
    evidenceWeaknesses.push("project command evidence is not REAL_PROJECT_COMMANDS");
  }

  if (normalizedProjectCommandEvidence === "REAL_PROJECT_COMMANDS") {
    if (commandArtifacts.validCommand.length === 0) {
      evidenceWeaknesses.push("real project command evidence has no valid command log artifact file in the target project");
    }
    if (commandArtifacts.missing.length > 0) {
      evidenceWeaknesses.push(`missing command artifact files: ${commandArtifacts.missing.join(", ")}`);
    }
    if (commandArtifacts.invalidCommand.length > 0) {
      evidenceWeaknesses.push(`invalid command artifact files: ${commandArtifacts.invalidCommand.join(", ")}`);
    }
  }

  if (!["REAL_BROWSER_SCREENSHOTS", "USER_SCREENSHOTS", "MANUAL_BROWSER_INSPECTION"].includes(normalizedVisualEvidenceVerdict)) {
    evidenceWeaknesses.push("visual evidence is not real browser/user/manual screenshot inspection");
  }

  if (["REAL_BROWSER_SCREENSHOTS", "USER_SCREENSHOTS"].includes(normalizedVisualEvidenceVerdict)) {
    if (evidenceArtifacts.validVisual.length === 0) {
      evidenceWeaknesses.push("real screenshot evidence has no valid image/video artifact files in the target project");
    }
    if (evidenceArtifacts.missing.length > 0) {
      evidenceWeaknesses.push(`missing evidence artifact files: ${evidenceArtifacts.missing.join(", ")}`);
    }
    if (evidenceArtifacts.invalidVisual.length > 0) {
      evidenceWeaknesses.push(`invalid visual artifact files: ${evidenceArtifacts.invalidVisual.join(", ")}`);
    }
  }

  if (normalizedVisualEvidenceVerdict === "MANUAL_BROWSER_INSPECTION") {
    if (evidenceArtifacts.validManual.length === 0) {
      evidenceWeaknesses.push("manual browser inspection has no valid notes artifact file in the target project");
    }
    if (evidenceArtifacts.missing.length > 0) {
      evidenceWeaknesses.push(`missing evidence artifact files: ${evidenceArtifacts.missing.join(", ")}`);
    }
    if (evidenceArtifacts.invalidManual.length > 0) {
      evidenceWeaknesses.push(
        `invalid manual inspection artifact files: ${evidenceArtifacts.invalidManual.join(", ")} (notes must mention a route/screen, viewport/size, and visual/layout/focus/overlap check)`,
      );
    }
  }

  return {
    ok: missing.length === 0,
    missing,
    verdict,
    projectCommandEvidence,
    visualEvidenceVerdict,
    evidenceArtifacts,
    commandArtifacts,
    changedFiles,
    routeConsistency,
    stateConsistency,
    rubricScore,
    implementationSliceEvidence,
    topDesignEvidence,
    aiDesignAppEvidence,
    informationArchitectureEvidence,
    interactionModelEvidence,
    copyStatusLanguageEvidence,
    decisionReviewCockpitEvidence,
    visualSystemEvidence,
    componentStateEvidence,
    evidenceReady: missing.length === 0 && evidenceWeaknesses.length === 0,
    evidenceWeaknesses,
  };
}

function buildReport({ targetPath, packageInfo, packet, agentRules, brief, final }) {
  const lines = [
    "# Design Target Audit",
    "",
    `Target: ${targetPath}`,
    `Generated: ${new Date().toISOString()}`,
    "",
    "## Summary",
    "",
    `- Target package: ${statusLabel(packageInfo.found, true)} - ${packageInfo.stack}`,
    `- Packet: ${statusLabel(packet.ok)}${packet.promptMode ? ` - mode ${packet.promptMode}` : ""}`,
    `- Target AGENTS.md block: ${statusLabel(agentRules.ok, true)}`,
    `- Working brief ready: ${statusLabel(brief.ok)}`,
    `- Final report ready: ${statusLabel(final.ok, true)}`,
    `- Final evidence ready: ${statusLabel(final.evidenceReady, true)}`,
    "",
    "## Details",
    "",
    `- Package scripts: ${packageInfo.scripts.length > 0 ? packageInfo.scripts.join(", ") : "none detected"}`,
    `- Knowledge base: ${packet.knowledgeBasePath || "not detected"}`,
    `- Missing packet files: ${packet.missing.length > 0 ? packet.missing.join(", ") : "none"}`,
    `- Missing working brief fields: ${brief.missing.length > 0 ? brief.missing.join(", ") : "none"}`,
    `- Weak working brief fields: ${brief.substance.weakFields.length > 0 ? brief.substance.weakFields.join(", ") : "none"}`,
    `- Working brief missing substance signals: ${brief.substance.missingSignals.length > 0 ? brief.substance.missingSignals.join(", ") : "none"}`,
    `- AI design app detected: ${brief.substance.isAiDesignApp ? "yes" : "no"}`,
    `- Weak AI design app invariant fields: ${brief.substance.weakAiInvariantFields.length > 0 ? brief.substance.weakAiInvariantFields.join(", ") : "none"}`,
    `- AI design app invariant missing signals: ${brief.substance.missingAiInvariantSignals.length > 0 ? brief.substance.missingAiInvariantSignals.join(", ") : "none"}`,
    `- Missing final report fields: ${final.missing.length > 0 ? final.missing.join(", ") : "none"}`,
    `- Final report verdict: ${final.verdict || "not detected"}`,
    `- Changed files found: ${final.changedFiles.existing.length > 0 ? final.changedFiles.existing.join(", ") : "none"}`,
    `- Changed files missing: ${final.changedFiles.missing.length > 0 ? final.changedFiles.missing.join(", ") : "none"}`,
    `- Changed files outside target: ${final.changedFiles.outsideTarget.length > 0 ? final.changedFiles.outsideTarget.join(", ") : "none"}`,
    `- Changed file paths that are not files: ${final.changedFiles.notFiles.length > 0 ? final.changedFiles.notFiles.join(", ") : "none"}`,
    `- Brief route paths: ${final.routeConsistency.briefRoutes.length > 0 ? final.routeConsistency.briefRoutes.join(", ") : "none"}`,
    `- Final checked route paths: ${final.routeConsistency.finalRoutes.length > 0 ? final.routeConsistency.finalRoutes.join(", ") : "none"}`,
    `- Brief route paths missing from final checks: ${final.routeConsistency.missingFromFinal.length > 0 ? final.routeConsistency.missingFromFinal.join(", ") : "none"}`,
    `- Brief included states: ${final.stateConsistency.briefStates.length > 0 ? final.stateConsistency.briefStates.join(", ") : "none"}`,
    `- Final checked states: ${final.stateConsistency.finalStates.length > 0 ? final.stateConsistency.finalStates.join(", ") : "none"}`,
    `- Brief included states missing from final checks: ${final.stateConsistency.missingFromFinal.length > 0 ? final.stateConsistency.missingFromFinal.join(", ") : "none"}`,
    `- Rubric score: ${final.rubricScore.value || "not detected"}`,
    `- Rubric normalized score: ${final.rubricScore.normalizedScore === null || Number.isNaN(final.rubricScore.normalizedScore) ? "not detected" : `${final.rubricScore.normalizedScore.toFixed(1)}/30`}`,
    `- Rubric blocking categories: ${final.rubricScore.blockingCategories || "none"}`,
    `- Rubric zero categories: ${final.rubricScore.zeroCategories.length > 0 ? final.rubricScore.zeroCategories.join(", ") : "none"}`,
    `- Implementation slice missing signals: ${final.implementationSliceEvidence.missingSignals.length > 0 ? final.implementationSliceEvidence.missingSignals.join(", ") : "none"}`,
    `- Weak implementation-slice fields: ${final.implementationSliceEvidence.weakFields.length > 0 ? final.implementationSliceEvidence.weakFields.join(", ") : "none"}`,
    `- Brief primary-object terms matched: ${final.implementationSliceEvidence.objectTermsMatched.length > 0 ? final.implementationSliceEvidence.objectTermsMatched.join(", ") : "none"}`,
    `- Brief primary-object terms missing from final: ${final.implementationSliceEvidence.objectTermsMissing.length > 0 ? final.implementationSliceEvidence.objectTermsMissing.join(", ") : "none"}`,
    `- Brief workflow/action terms matched: ${final.implementationSliceEvidence.workflowTermsMatched.length > 0 ? final.implementationSliceEvidence.workflowTermsMatched.join(", ") : "none"}`,
    `- Brief workflow/action terms missing from final: ${final.implementationSliceEvidence.workflowTermsMissing.length > 0 ? final.implementationSliceEvidence.workflowTermsMissing.join(", ") : "none"}`,
    `- Brief data/source terms matched: ${final.implementationSliceEvidence.dataTermsMatched.length > 0 ? final.implementationSliceEvidence.dataTermsMatched.join(", ") : "none"}`,
    `- Brief data/source terms missing from final: ${final.implementationSliceEvidence.dataTermsMissing.length > 0 ? final.implementationSliceEvidence.dataTermsMissing.join(", ") : "none"}`,
    `- Five-second test missing signals: ${final.topDesignEvidence.fiveSecondMissingSignals.length > 0 ? final.topDesignEvidence.fiveSecondMissingSignals.join(", ") : "none"}`,
    `- Weak top-design fields: ${final.topDesignEvidence.weakFields.length > 0 ? final.topDesignEvidence.weakFields.join(", ") : "none"}`,
    `- Brief mediocrity risk terms matched: ${final.topDesignEvidence.riskTermsMatched.length > 0 ? final.topDesignEvidence.riskTermsMatched.join(", ") : "none"}`,
    `- Brief mediocrity risk terms missing from final: ${final.topDesignEvidence.riskTermsMissing.length > 0 ? final.topDesignEvidence.riskTermsMissing.join(", ") : "none"}`,
    `- Brief product-detail terms matched: ${final.topDesignEvidence.detailTermsMatched.length > 0 ? final.topDesignEvidence.detailTermsMatched.join(", ") : "none"}`,
    `- Brief product-detail terms missing from final: ${final.topDesignEvidence.detailTermsMissing.length > 0 ? final.topDesignEvidence.detailTermsMissing.join(", ") : "none"}`,
    `- AI design app final weak fields: ${final.aiDesignAppEvidence.weakFields.length > 0 ? final.aiDesignAppEvidence.weakFields.join(", ") : "none"}`,
    `- AI design app final missing operational signals: ${final.aiDesignAppEvidence.missingSignals.length > 0 ? final.aiDesignAppEvidence.missingSignals.join(", ") : "none"}`,
    `- Information architecture evidence: ${final.informationArchitectureEvidence.value || "not detected"}`,
    `- Information architecture missing signals: ${final.informationArchitectureEvidence.missingSignals.length > 0 ? final.informationArchitectureEvidence.missingSignals.join(", ") : "none"}`,
    `- Interaction model evidence: ${final.interactionModelEvidence.value || "not detected"}`,
    `- Interaction model missing signals: ${final.interactionModelEvidence.missingSignals.length > 0 ? final.interactionModelEvidence.missingSignals.join(", ") : "none"}`,
    `- Copy/status language evidence: ${final.copyStatusLanguageEvidence.value || "not detected"}`,
    `- Copy/status language missing signals: ${final.copyStatusLanguageEvidence.missingSignals.length > 0 ? final.copyStatusLanguageEvidence.missingSignals.join(", ") : "none"}`,
    `- Decision/review cockpit evidence: ${final.decisionReviewCockpitEvidence.value || "not detected"}`,
    `- Decision/review cockpit missing signals: ${final.decisionReviewCockpitEvidence.missingSignals.length > 0 ? final.decisionReviewCockpitEvidence.missingSignals.join(", ") : "none"}`,
    `- Visual system evidence: ${final.visualSystemEvidence.value || "not detected"}`,
    `- Visual system missing signals: ${final.visualSystemEvidence.missingSignals.length > 0 ? final.visualSystemEvidence.missingSignals.join(", ") : "none"}`,
    `- Component state evidence: ${final.componentStateEvidence.value || "not detected"}`,
    `- Component state evidence missing signals: ${final.componentStateEvidence.missingSignals.length > 0 ? final.componentStateEvidence.missingSignals.join(", ") : "none"}`,
    `- Project command evidence: ${final.projectCommandEvidence || "not detected"}`,
    `- Command artifact files found: ${final.commandArtifacts.existing.length > 0 ? final.commandArtifacts.existing.join(", ") : "none"}`,
    `- Command artifact files missing: ${final.commandArtifacts.missing.length > 0 ? final.commandArtifacts.missing.join(", ") : "none"}`,
    `- Valid command artifact files: ${final.commandArtifacts.validCommand.length > 0 ? final.commandArtifacts.validCommand.join(", ") : "none"}`,
    `- Invalid command artifact files: ${final.commandArtifacts.invalidCommand.length > 0 ? final.commandArtifacts.invalidCommand.join(", ") : "none"}`,
    `- Visual evidence verdict: ${final.visualEvidenceVerdict || "not detected"}`,
    `- Evidence artifact files found: ${final.evidenceArtifacts.existing.length > 0 ? final.evidenceArtifacts.existing.join(", ") : "none"}`,
    `- Evidence artifact files missing: ${final.evidenceArtifacts.missing.length > 0 ? final.evidenceArtifacts.missing.join(", ") : "none"}`,
    `- Valid visual artifact files: ${final.evidenceArtifacts.validVisual.length > 0 ? final.evidenceArtifacts.validVisual.join(", ") : "none"}`,
    `- Invalid visual artifact files: ${final.evidenceArtifacts.invalidVisual.length > 0 ? final.evidenceArtifacts.invalidVisual.join(", ") : "none"}`,
    `- Valid manual inspection artifact files: ${final.evidenceArtifacts.validManual.length > 0 ? final.evidenceArtifacts.validManual.join(", ") : "none"}`,
    `- Invalid manual inspection artifact files: ${final.evidenceArtifacts.invalidManual.length > 0 ? final.evidenceArtifacts.invalidManual.join(", ") : "none"}`,
    `- Evidence weaknesses: ${final.evidenceWeaknesses.length > 0 ? final.evidenceWeaknesses.join("; ") : "none"}`,
    "",
    "## Next Commands",
    "",
  ];

  if (!packet.ok) {
    lines.push(`- Run: \`npm run design:install-agent-rules -- "${targetPath}"\``);
  }

  if (!agentRules.ok) {
    lines.push(`- Run: \`npm run design:install-agent-rules -- "${targetPath}"\``);
  }

  lines.push(`- Run: \`npm run design:packet-check -- "${targetPath}"\``);

  if (!brief.ok) {
    lines.push("- Fill `.design-agent/working-brief.md` before coding.");
  }
  lines.push(`- Run: \`npm run design:brief-check -- "${targetPath}"\``);

  if (!final.ok) {
    lines.push("- Fill `.design-agent/final-report-template.md` before final handoff.");
  }
  lines.push(`- Run: \`npm run design:final-check -- "${targetPath}"\``);
  lines.push(`- Refresh this report: \`npm run design:target-audit -- "${targetPath}" --write\``);

  lines.push("");
  lines.push("## Verdict");
  lines.push("");
  if (!packet.ok || !brief.ok) {
    lines.push("NOT READY FOR CODING");
  } else if (!final.ok || !final.evidenceReady) {
    lines.push("READY FOR CODING, NOT READY FOR FINAL HANDOFF");
  } else {
    lines.push("READY FOR FINAL HANDOFF");
  }

  return `${lines.join("\n")}\n`;
}

const { help, targetPath, write } = parseArgs(process.argv.slice(2));
if (help) {
  usage();
  process.exit(0);
}

if (!targetPath) {
  usage();
  process.exit(1);
}

if (!existsSync(targetPath) || !statSync(targetPath).isDirectory()) {
  console.error(`Target path is not a directory: ${targetPath}`);
  process.exit(1);
}

const report = buildReport({
  targetPath,
  packageInfo: inspectPackage(targetPath),
  packet: inspectPacket(targetPath),
  agentRules: inspectAgentRules(targetPath),
  brief: inspectBrief(targetPath),
  final: inspectFinal(targetPath),
});

if (write) {
  const reportPath = targetFile(targetPath, ".design-agent/readiness-report.md");
  mkdirSync(path.dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, report, "utf8");
  console.log(`Wrote design target audit: ${reportPath}`);
  console.log("");
}

console.log(report);

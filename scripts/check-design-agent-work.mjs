#!/usr/bin/env node

import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

const phases = new Set(["brief", "final", "all"]);

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

const failures = [];

function usage() {
  console.log(`Usage: node scripts/check-design-agent-work.mjs <target-project-path> [--phase brief|final|all]

Examples:
  node scripts/check-design-agent-work.mjs C:\\path\\to\\target --phase brief
  node scripts/check-design-agent-work.mjs --phase final C:\\path\\to\\target`);
}

function fail(message) {
  failures.push(message);
}

function parseArgs(argv) {
  let targetPath = "";
  let phase = "all";

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      return { help: true, targetPath, phase };
    }

    if (arg === "--phase") {
      phase = argv[index + 1] ?? "";
      index += 1;
      continue;
    }

    if (arg.startsWith("--phase=")) {
      phase = arg.slice("--phase=".length);
      continue;
    }

    if (!targetPath) {
      targetPath = arg;
    }
  }

  return { help: false, targetPath, phase };
}

function targetFile(targetRoot, relativePath) {
  return path.join(targetRoot, ...relativePath.split("/"));
}

function readTarget(targetRoot, relativePath) {
  return readFileSync(targetFile(targetRoot, relativePath), "utf8");
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

function extractRouteCandidates(value) {
  const routes = [];
  const regex = /(?:^|[\s"'`(])((?:https?:\/\/[^/\s"'`),;]+)?\/[A-Za-z0-9._~!$&'()*+,;=:@/%-]*)(?=[\s"'`),;.]|$)/g;
  let match = regex.exec(value);

  while (match) {
    routes.push(match[1]);
    match = regex.exec(value);
  }

  return [...new Set(routes)];
}

function extractMeaningfulTerms(value) {
  const matches = value.toLowerCase().match(/[\p{L}\p{N}][\p{L}\p{N}-]{3,}/gu) ?? [];
  return [...new Set(matches)]
    .filter((term) => !["design", "done", "good", "better", "improved", "checked", "product"].includes(term))
    .slice(0, 20);
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

function requireSubstantiveBrief(markdown, fileLabel) {
  for (const label of substantiveBriefLabels) {
    const value = extractLabelValue(markdown, label);
    if (!isSubstantiveBriefValue(label, value)) {
      fail(`${fileLabel} has weak product brief field: ${label}`);
    }
  }

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

  for (const { name, pattern } of briefSignalChecks) {
    if (!pattern.test(combined)) {
      fail(`${fileLabel} is missing product brief substance signal: ${name}`);
    }
  }

  if (isAiDesignAppBrief(markdown)) {
    const invariantCombined = aiInvariantLabels.map((label) => extractLabelValue(markdown, label)).join("; ");
    for (const label of aiInvariantLabels) {
      if (!isSubstantiveAiInvariantValue(label, extractLabelValue(markdown, label))) {
        fail(`${fileLabel} has weak AI design app invariant: ${label}`);
      }
    }

    for (const { name, pattern } of aiInvariantSignalChecks) {
      if (!pattern.test(invariantCombined)) {
        fail(`${fileLabel} is missing AI design app invariant signal: ${name}`);
      }
    }
  }
}

function requireFinalAiDesignAppEvidence(briefMarkdown, finalMarkdown, fileLabel) {
  if (!isAiDesignAppBrief(briefMarkdown)) {
    return;
  }

  const operationalValue = extractLabelValue(finalMarkdown, "Operational pattern checked");
  if (isWeakGenericEvidence(operationalValue)) {
    fail(`${fileLabel} has weak AI design app final field: Operational pattern checked`);
  }

  const combined = [
    extractLabelValue(finalMarkdown, "Trusted vertical checked"),
    extractLabelValue(finalMarkdown, "AI source-of-truth/false-state risks checked"),
    operationalValue,
    extractLabelValue(finalMarkdown, "Workflow improved"),
    extractLabelValue(finalMarkdown, "Implementation slice contract"),
  ].join("; ");

  for (const { name, pattern } of aiInvariantSignalChecks) {
    if (!pattern.test(combined)) {
      fail(`${fileLabel} is missing final AI design app operational signal: ${name}`);
    }
  }
}

function requireFilledLabels(markdown, labels, fileLabel) {
  for (const label of labels) {
    const value = extractLabelValue(markdown, label);
    if (isUnfilled(value)) {
      fail(`${fileLabel} has empty or placeholder field: ${label}`);
    }
  }
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

function requireOneOf(markdown, label, allowedValues, fileLabel) {
  const value = extractLabelValue(markdown, label);
  if (!normalizeChoice(value, allowedValues)) {
    fail(`${fileLabel} has invalid ${label}. Use one of: ${allowedValues.join(", ")}`);
  }
}

function requireIncludes(markdown, patterns, fileLabel) {
  for (const pattern of patterns) {
    if (!markdown.includes(pattern)) {
      fail(`${fileLabel} missing anchor: ${pattern}`);
    }
  }
}

function checkTarget(targetPath) {
  if (!targetPath) {
    fail("Missing target project path.");
    return;
  }

  if (!existsSync(targetPath)) {
    fail(`Target path does not exist: ${targetPath}`);
    return;
  }

  if (!statSync(targetPath).isDirectory()) {
    fail(`Target path is not a directory: ${targetPath}`);
  }
}

function checkBrief(targetPath) {
  const relativePath = ".design-agent/working-brief.md";
  const filePath = targetFile(targetPath, relativePath);
  if (!existsSync(filePath)) {
    fail(`Missing ${relativePath}`);
    return;
  }

  const markdown = readTarget(targetPath, relativePath);
  requireIncludes(
    markdown,
    [
      "## Surface Classification",
      "## Product Read",
      "## Implementation Slice Contract",
      "## Verification Plan",
    ],
    relativePath,
  );
  requireFilledLabels(markdown, briefRequiredLabels, relativePath);
  requireSubstantiveBrief(markdown, relativePath);
}

function checkFinal(targetPath) {
  const relativePath = ".design-agent/final-report-template.md";
  const filePath = targetFile(targetPath, relativePath);
  if (!existsSync(filePath)) {
    fail(`Missing ${relativePath}`);
    return;
  }

  const markdown = readTarget(targetPath, relativePath);
  requireIncludes(
    markdown,
    [
      "## Verdict",
      "## Product UI Checks",
      "## Evidence",
      "## Quality Result",
    ],
    relativePath,
  );
  requireFilledLabels(markdown, finalRequiredLabels, relativePath);
  if (isWeakGenericEvidence(extractLabelValue(markdown, "Object model checked"))) {
    fail(`${relativePath} has weak final field: Object model checked`);
  }
  const missingVisualSystemEvidenceSignals = visualSystemEvidenceMissingSignals(
    extractLabelValue(markdown, "Visual system checked"),
  );
  if (missingVisualSystemEvidenceSignals.length > 0) {
    fail(`${relativePath} has weak final field: Visual system checked; missing ${missingVisualSystemEvidenceSignals.join(", ")}`);
  }
  const missingInformationArchitectureSignals = informationArchitectureMissingSignals(
    extractLabelValue(markdown, "Information architecture checked"),
  );
  if (missingInformationArchitectureSignals.length > 0) {
    fail(`${relativePath} has weak final field: Information architecture checked; missing ${missingInformationArchitectureSignals.join(", ")}`);
  }
  const missingInteractionModelSignals = interactionModelMissingSignals(
    extractLabelValue(markdown, "Interaction model checked"),
  );
  if (missingInteractionModelSignals.length > 0) {
    fail(`${relativePath} has weak final field: Interaction model checked; missing ${missingInteractionModelSignals.join(", ")}`);
  }
  const missingCopyStatusLanguageSignals = copyStatusLanguageMissingSignals(
    extractLabelValue(markdown, "Copy/status language checked"),
  );
  if (missingCopyStatusLanguageSignals.length > 0) {
    fail(`${relativePath} has weak final field: Copy/status language checked; missing ${missingCopyStatusLanguageSignals.join(", ")}`);
  }
  const missingDecisionReviewCockpitSignals = decisionReviewCockpitMissingSignals(
    extractLabelValue(markdown, "Decision/review cockpit checked"),
  );
  if (missingDecisionReviewCockpitSignals.length > 0) {
    fail(`${relativePath} has weak final field: Decision/review cockpit checked; missing ${missingDecisionReviewCockpitSignals.join(", ")}`);
  }
  const missingComponentStateEvidenceSignals = componentStateEvidenceMissingSignals(
    extractLabelValue(markdown, "Component state evidence checked"),
  );
  if (missingComponentStateEvidenceSignals.length > 0) {
    fail(`${relativePath} has weak final field: Component state evidence checked; missing ${missingComponentStateEvidenceSignals.join(", ")}`);
  }
  requireOneOf(markdown, "PASS / PASS WITH RISKS / FAIL", ["PASS", "PASS WITH RISKS", "FAIL"], relativePath);
  requireOneOf(markdown, "Project command evidence", ["REAL_PROJECT_COMMANDS", "NOT_RUN_WITH_RISK"], relativePath);
  requireOneOf(
    markdown,
    "Visual evidence verdict",
    ["REAL_BROWSER_SCREENSHOTS", "USER_SCREENSHOTS", "MANUAL_BROWSER_INSPECTION", "NOT_RUN_WITH_RISK"],
    relativePath,
  );
  const briefPath = targetFile(targetPath, ".design-agent/working-brief.md");
  if (existsSync(briefPath)) {
    requireFinalAiDesignAppEvidence(readFileSync(briefPath, "utf8"), markdown, relativePath);
  }
}

const { help, targetPath, phase } = parseArgs(process.argv.slice(2));
if (help) {
  usage();
  process.exit(0);
}

if (!phases.has(phase)) {
  fail(`Unknown phase "${phase}". Use brief, final, or all.`);
}

checkTarget(targetPath);

if (failures.length === 0 && (phase === "brief" || phase === "all")) {
  checkBrief(targetPath);
}

if (failures.length === 0 && (phase === "final" || phase === "all")) {
  checkFinal(targetPath);
}

if (failures.length > 0) {
  console.error("Design agent work check failed:");
  for (const message of failures) {
    console.error(`- ${message}`);
  }
  process.exit(1);
}

console.log(`Design agent work check passed for phase: ${phase}.`);

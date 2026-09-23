#!/usr/bin/env python3
"""Build a resumable per-source review queue for the 3D SHVYREV corpus."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path("docs/research/youtube-lessons/3d-shvyrev")
CATALOG_PATH = BASE_DIR / "channel_catalog.json"
TECHNIQUES_PATH = BASE_DIR / "techniques.jsonl"
FINDINGS_PATH = BASE_DIR / "source_findings.jsonl"
QUEUE_JSON = BASE_DIR / "source_reviews.json"
QUEUE_MD = BASE_DIR / "source_reviews.md"


def load_jsonl(path: Path) -> list[dict[str, object]]:
  if not path.exists():
    return []
  records: list[dict[str, object]] = []
  for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
      continue
    try:
      records.append(json.loads(line))
    except json.JSONDecodeError as error:
      raise RuntimeError(f"{path}:{line_number}: {error}") from error
  return records


def load_existing_decisions() -> dict[str, dict[str, object]]:
  if not QUEUE_JSON.exists():
    return {}
  payload = json.loads(QUEUE_JSON.read_text(encoding="utf-8"))
  return {
    str(record["video_id"]): record
    for record in payload.get("records", [])
    if record.get("video_id")
  }


def main() -> int:
  catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
  techniques = load_jsonl(TECHNIQUES_PATH)
  findings = load_jsonl(FINDINGS_PATH)
  existing = load_existing_decisions()
  findings_by_video = {
    str(finding["video_id"]): finding
    for finding in findings
    if finding.get("video_id")
  }
  technique_ids_by_video: dict[str, list[str]] = defaultdict(list)
  for technique in techniques:
    source = technique.get("source")
    if not isinstance(source, dict):
      continue
    video_id = str(source.get("video_id") or "")
    technique_id = str(technique.get("id") or "")
    if video_id and technique_id:
      technique_ids_by_video[video_id].append(technique_id)

  records: list[dict[str, object]] = []
  for entry in catalog["entries"]:
    video_id = str(entry["video_id"])
    source_dir = BASE_DIR / "sources" / video_id
    caption_files = sorted(path.name for path in source_dir.glob("*.vtt"))
    info_files = sorted(path.name for path in source_dir.glob("*.info.json"))
    thumbnail_files = sorted(
      path.name
      for path in source_dir.iterdir()
      if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ) if source_dir.exists() else []
    transcript_path = source_dir / "transcript.json"
    transcript_ready = transcript_path.exists()
    transcript_characters = 0
    if transcript_ready:
      transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
      transcript_characters = int(transcript.get("character_count") or 0)

    prior = existing.get(video_id, {})
    finding = findings_by_video.get(video_id)
    finding_techniques = finding.get("canonical_technique_ids", []) if finding else []
    technique_ids = sorted({
      *technique_ids_by_video.get(video_id, []),
      *(str(item) for item in finding_techniques),
    })
    if finding:
      default_status = str(finding["review_status"])
    else:
      default_status = "EXTRACTED" if technique_ids else "PENDING"
    prior_disposition = prior.get("disposition")
    if finding:
      disposition = str(finding["disposition"])
    elif technique_ids and prior_disposition in {None, "pending"}:
      disposition = "improvements_extracted"
    else:
      disposition = prior_disposition or "pending"
    record = {
      "video_id": video_id,
      "source_kind": entry["source_kind"],
      "position": entry["position"],
      "title": entry["title"],
      "url": entry["url"],
      "duration_seconds": entry["duration_seconds"],
      "evidence": {
        "metadata_ready": bool(info_files),
        "caption_ready": bool(caption_files),
        "transcript_ready": transcript_ready,
        "transcript_characters": transcript_characters,
        "thumbnail_ready": bool(thumbnail_files),
      },
      "review_status": default_status if finding else prior.get("review_status", default_status),
      "disposition": disposition,
      "canonical_technique_ids": technique_ids,
      "candidate_topics": finding.get("candidate_topics", []) if finding else [],
      "addon_mentions": finding.get("addon_mentions", []) if finding else [],
      "review_notes": finding.get("notes", "") if finding else prior.get("review_notes", ""),
    }
    records.append(record)

  counts = Counter(str(record["review_status"]) for record in records)
  dispositions = Counter(str(record["disposition"]) for record in records)
  payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "channel": catalog["channel"],
    "counts": {
      "total": len(records),
      "videos": sum(record["source_kind"] == "video" for record in records),
      "shorts": sum(record["source_kind"] == "short" for record in records),
      "transcript_ready": sum(bool(record["evidence"]["transcript_ready"]) for record in records),
      "review_status": dict(sorted(counts.items())),
      "disposition": dict(sorted(dispositions.items())),
      "techniques": len(techniques),
      "findings": len(findings),
      "addon_mentions": sum(len(record["addon_mentions"]) for record in records),
    },
    "records": records,
  }
  QUEUE_JSON.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )

  lines = [
    "# 3D SHVYREV — очередь разбора",
    "",
    f"- Обновлено: {payload['generated_at']}",
    f"- Источников: {payload['counts']['total']}",
    f"- Транскрипт готов: {payload['counts']['transcript_ready']}",
    f"- Извлечено техник: {payload['counts']['techniques']}",
    f"- Проверено источников: {payload['counts']['findings']}",
    f"- Упоминаний аддонов: {payload['counts']['addon_mentions']}",
    "",
    "| Тип | № | Источник | Транскрипт | Статус | Решение | Техники |",
    "|---|---:|---|:---:|---|---|---|",
  ]
  for record in records:
    safe_title = str(record["title"]).replace("|", "\\|")
    evidence = record["evidence"]
    technique_list = ", ".join(record["canonical_technique_ids"]) or "—"
    lines.append(
      f"| {record['source_kind']} | {record['position']} | "
      f"[{safe_title}]({record['url']}) | "
      f"{'да' if evidence['transcript_ready'] else 'нет'} | "
      f"{record['review_status']} | {record['disposition']} | {technique_list} |"
    )
  QUEUE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
  print(
    f"Review queue: {len(records)} sources; "
    f"{payload['counts']['transcript_ready']} transcripts; "
    f"{len(techniques)} techniques"
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

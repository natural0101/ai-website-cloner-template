"""Merge validated sub-agent review batches into the 3D SHVYREV database."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "research" / "youtube-lessons" / "3d-shvyrev"
FINDINGS_PATH = BASE / "source_findings.jsonl"
TECHNIQUES_PATH = BASE / "techniques.jsonl"
CATALOG_PATH = BASE / "channel_catalog.json"
AGENT_DIR = BASE / "agent-findings"
AGENT_BATCHES = [
    AGENT_DIR / "shorts-131-155.jsonl",
    AGENT_DIR / "shorts-156-180.jsonl",
    AGENT_DIR / "shorts-181-197.jsonl",
    AGENT_DIR / "videos-12-25.jsonl",
    AGENT_DIR / "videos-26-40.jsonl",
    AGENT_DIR / "visual-missing-resolved.jsonl",
    AGENT_DIR / "visual-missing-classified.jsonl",
]
AGENT_MISSING = [
    AGENT_DIR / "visual-missing-unresolved.json",
]


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: {error}") from error
    return records


catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
entries = catalog["entries"]
catalog_ids = [entry["video_id"] for entry in entries]
catalog_order = {video_id: index for index, video_id in enumerate(catalog_ids)}
technique_ids = {record["id"] for record in read_jsonl(TECHNIQUES_PATH)}

merged: dict[str, dict] = {}
sources_by_batch: dict[str, int] = {}
for path in [FINDINGS_PATH, *AGENT_BATCHES]:
    batch = read_jsonl(path)
    sources_by_batch[path.name] = len(batch)
    for record in batch:
        video_id = record["video_id"]
        if video_id not in catalog_order:
            raise ValueError(f"Unknown catalog video_id in {path}: {video_id}")
        unknown_techniques = sorted(
            set(record.get("canonical_technique_ids", [])) - technique_ids
        )
        if unknown_techniques:
            raise ValueError(
                f"Unknown canonical technique IDs for {video_id}: {unknown_techniques}"
            )
        if video_id in merged and merged[video_id] != record:
            raise ValueError(f"Conflicting duplicate finding for {video_id}")
        merged[video_id] = record

ordered_records = sorted(merged.values(), key=lambda record: catalog_order[record["video_id"]])
FINDINGS_PATH.write_text(
    "\n".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        for record in ordered_records
    )
    + "\n",
    encoding="utf-8",
)

missing_records = []
for path in AGENT_MISSING:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        items = payload
    elif "missing_visual_or_audio" in payload:
        value = payload["missing_visual_or_audio"]
        items = value if isinstance(value, list) else [value]
    else:
        items = [payload]
    missing_records.extend(items)

catalog_meta = {entry["video_id"]: entry for entry in entries}
normalized_missing = {}
for record in missing_records:
    video_id = record["video_id"]
    meta = catalog_meta[video_id]
    normalized_missing[video_id] = {
        "video_id": video_id,
        "source_kind": meta["source_kind"],
        "position": meta["position"],
        "title": meta["title"],
        "reason": record["reason"],
        "storyboard_available": True,
    }
missing_output = sorted(
    normalized_missing.values(), key=lambda record: catalog_order[record["video_id"]]
)
(BASE / "missing_visual_or_audio.json").write_text(
    json.dumps(missing_output, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

pending_ids = [video_id for video_id in catalog_ids if video_id not in merged]
report = {
    "catalog_total": len(catalog_ids),
    "findings_total": len(ordered_records),
    "findings_unique": len(merged),
    "pending_total": len(pending_ids),
    "missing_visual_or_audio_total": len(missing_output),
    "batch_input_counts": sources_by_batch,
    "expected_after_merge": 237,
    "passes_expected_count": len(ordered_records) == 237,
}
(BASE / "agent_merge_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(json.dumps(report, ensure_ascii=False))

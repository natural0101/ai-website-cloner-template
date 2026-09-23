"""Build a deterministic source-to-technique coverage audit for 3D SHVYREV."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any


APPLICABLE_DISPOSITIONS = {"new_improvement", "mixed"}
EXCLUDED_DISPOSITIONS = {"addon_inventory", "showcase_only", "not_applicable"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    base = (
        repo
        / "docs"
        / "research"
        / "youtube-lessons"
        / "3d-shvyrev"
    ).resolve()
    base.relative_to(repo)

    catalog = json.loads((base / "channel_catalog.json").read_text(encoding="utf-8"))
    findings = load_jsonl(base / "source_findings.jsonl")
    techniques = load_jsonl(base / "techniques.jsonl")
    topic_resolution_path = base / "topic_resolutions.jsonl"
    topic_resolutions = (
        load_jsonl(topic_resolution_path)
        if topic_resolution_path.exists()
        else []
    )
    evidence_gaps = json.loads(
        (base / "missing_visual_or_audio.json").read_text(encoding="utf-8")
    )

    catalog_items = (
        catalog.get("entries", catalog.get("items", []))
        if isinstance(catalog, dict)
        else catalog
    )
    catalog_ids = {item["video_id"] for item in catalog_items}
    finding_ids = {finding["video_id"] for finding in findings}
    technique_ids = {technique["id"] for technique in techniques}
    invalid_links = sorted(
        {
            technique_id
            for finding in findings
            for technique_id in finding.get("canonical_technique_ids", [])
            if technique_id not in technique_ids
        }
    )
    all_topic_pairs = {
        (finding["video_id"], topic)
        for finding in findings
        for topic in finding.get("candidate_topics", [])
    }
    applicable_topic_pairs = {
        (finding["video_id"], topic)
        for finding in findings
        if finding["disposition"] in APPLICABLE_DISPOSITIONS
        for topic in finding.get("candidate_topics", [])
    }
    supporting_topic_pairs = {
        (finding["video_id"], topic)
        for finding in findings
        if finding["disposition"] == "duplicate_or_supporting_source"
        for topic in finding.get("candidate_topics", [])
    }
    resolution_pairs = {
        (row["video_id"], row["candidate_topic"])
        for row in topic_resolutions
    }
    invalid_resolution_links = sorted(
        {
            technique_id
            for row in topic_resolutions
            for technique_id in row.get("technique_ids", [])
            if technique_id not in technique_ids
        }
    )
    resolution_counts = collections.Counter(
        row["resolution"] for row in topic_resolutions
    )

    source_rows: list[dict[str, Any]] = []
    applicable_topics = 0
    applicable_source_ids: list[str] = []
    source_linked_applicable_ids: list[str] = []
    source_unlinked_applicable_ids: list[str] = []
    for finding in findings:
        disposition = finding["disposition"]
        canonical_ids = finding.get("canonical_technique_ids", [])
        topics = finding.get("candidate_topics", [])
        topic_pairs = {
            (finding["video_id"], topic)
            for topic in topics
        }
        if disposition in APPLICABLE_DISPOSITIONS:
            applicable_source_ids.append(finding["video_id"])
            applicable_topics += len(topics)
            if canonical_ids:
                source_linked_applicable_ids.append(finding["video_id"])
            else:
                source_unlinked_applicable_ids.append(finding["video_id"])
            resolution = (
                "TOPICS_EXPLICITLY_RESOLVED"
                if topic_pairs <= resolution_pairs
                else "TOPIC_MAPPING_REQUIRED"
            )
        elif disposition == "duplicate_or_supporting_source":
            resolution = (
                "SUPPORTING_TOPICS_EXPLICITLY_RESOLVED"
                if topic_pairs <= resolution_pairs
                else "SUPPORTING_TOPIC_MAPPING_REQUIRED"
            )
        elif disposition in EXCLUDED_DISPOSITIONS:
            resolution = disposition.upper()
        else:
            resolution = "UNKNOWN"
        source_rows.append(
            {
                "video_id": finding["video_id"],
                "review_status": finding["review_status"],
                "disposition": disposition,
                "resolution": resolution,
                "canonical_technique_ids": canonical_ids,
                "candidate_topics": topics,
                "addon_mentions": len(finding.get("addon_mentions", [])),
                "notes": finding.get("notes", ""),
            }
        )

    technique_source_counts = collections.Counter(
        technique["source"]["video_id"] for technique in techniques
    )
    status_counts = collections.Counter(
        finding["review_status"] for finding in findings
    )
    disposition_counts = collections.Counter(
        finding["disposition"] for finding in findings
    )
    technique_status_counts = collections.Counter(
        technique["status"] for technique in techniques
    )
    category_counts = collections.Counter(
        technique["category"] for technique in techniques
    )

    runtime_probe_path = (
        repo
        / "blender-workbench"
        / "artifacts"
        / "reports"
        / "shvyrev_blender_5_1_runtime_capability_probe.json"
    )
    runtime_fixture_path = (
        repo
        / "blender-workbench"
        / "artifacts"
        / "reports"
        / "shvyrev_blender_5_1_builtin_runtime_test.json"
    )
    runtime_fixture = (
        json.loads(runtime_fixture_path.read_text(encoding="utf-8"))
        if runtime_fixture_path.exists()
        else {}
    )
    gates = {
        "catalog_and_findings_match": catalog_ids == finding_ids,
        "catalog_count_is_237": len(catalog_ids) == 237,
        "all_sources_reviewed": len(findings) == len(catalog_ids)
        and all(
            finding["review_status"]
            in {"TRANSCRIPT_REVIEWED", "VISUALLY_REVIEWED"}
            for finding in findings
        ),
        "all_canonical_links_exist": not invalid_links,
        "all_applicable_topics_have_explicit_resolution": (
            applicable_topic_pairs <= resolution_pairs
        ),
        "all_supporting_topics_have_explicit_resolution": (
            supporting_topic_pairs <= resolution_pairs
        ),
        "all_candidate_topics_accounted": all_topic_pairs == resolution_pairs,
        "all_resolution_links_exist": not invalid_resolution_links,
        "runtime_capability_probe_saved": runtime_probe_path.exists(),
        "runtime_builtin_fixture_saved": runtime_fixture_path.exists(),
        "runtime_fixture_cleanup_passed": bool(
            runtime_fixture.get("cleanup", {}).get("passed")
        ),
        "version_runtime_deferrals_are_explicit": all(
            row.get("reason")
            for row in topic_resolutions
            if row.get("resolution") == "defer_version_runtime"
        ),
    }
    audit = {
        "schema_version": "1.0",
        "scope": {
            "channel": "3D SHVYREV",
            "channel_id": "UCv12mUx2DahFIxs9nZLDKNw",
            "catalog_sources": len(catalog_ids),
            "reviewed_findings": len(findings),
            "canonical_techniques": len(techniques),
            "applicable_sources": len(applicable_source_ids),
            "applicable_candidate_topics": applicable_topics,
        },
        "counts": {
            "review_status": dict(sorted(status_counts.items())),
            "dispositions": dict(sorted(disposition_counts.items())),
            "technique_status": dict(sorted(technique_status_counts.items())),
            "technique_categories": dict(sorted(category_counts.items())),
            "applicable_sources_with_source_link": len(source_linked_applicable_ids),
            "applicable_sources_without_source_link": len(
                source_unlinked_applicable_ids
            ),
            "canonical_primary_source_videos": len(technique_source_counts),
            "evidence_gap_sources": len(evidence_gaps),
            "topic_resolutions": len(topic_resolutions),
            "topic_resolution_counts": dict(sorted(resolution_counts.items())),
            "applicable_topics_explicitly_resolved": len(
                applicable_topic_pairs & resolution_pairs
            ),
        },
        "gates": gates,
        "invalid_canonical_links": invalid_links,
        "invalid_topic_resolution_links": invalid_resolution_links,
        "missing_topic_resolutions": sorted(
            [
                {"video_id": video_id, "candidate_topic": topic}
                for video_id, topic in all_topic_pairs - resolution_pairs
            ],
            key=lambda row: (row["video_id"], row["candidate_topic"]),
        ),
        "extra_topic_resolutions": sorted(
            [
                {"video_id": video_id, "candidate_topic": topic}
                for video_id, topic in resolution_pairs - all_topic_pairs
            ],
            key=lambda row: (row["video_id"], row["candidate_topic"]),
        ),
        "missing_catalog_findings": sorted(catalog_ids - finding_ids),
        "findings_outside_catalog": sorted(finding_ids - catalog_ids),
        "source_unlinked_applicable_video_ids": sorted(
            source_unlinked_applicable_ids
        ),
        "evidence_gap_video_ids": sorted(
            item.get("video_id", "") for item in evidence_gaps
        ),
        "sources": sorted(source_rows, key=lambda row: row["video_id"]),
    }
    write_json(base / "technique_coverage_audit.json", audit)

    failed_gates = [name for name, passed in gates.items() if not passed]
    markdown = [
        "# Аудит покрытия техник 3D SHVYREV",
        "",
        "Детерминированный аудит связывает полный каталог источников с канонической базой техник.",
        "",
        "## Сводка",
        "",
        f"- Каталог и source findings: **{len(catalog_ids)}/{len(findings)}**.",
        f"- Канонические техники: **{len(techniques)}**.",
        f"- Применимые источники (`new_improvement` + `mixed`): **{len(applicable_source_ids)}**.",
        f"- Кандидатные темы в применимых источниках: **{applicable_topics}**.",
        f"- Применимые источники с хотя бы одной source-level связью: **{len(source_linked_applicable_ids)}**.",
        f"- Применимые источники без source-level связи: **{len(source_unlinked_applicable_ids)}**.",
        f"- Topic-level решений: **{len(topic_resolutions)}/{len(all_topic_pairs)}**.",
        f"- Применимых тем с явным решением: **{len(applicable_topic_pairs & resolution_pairs)}/{len(applicable_topic_pairs)}**.",
        "",
        "Source-level link не обязателен, если все темы источника явно отклонены "
        "или отложены с причиной. Полноту доказывает `topic_resolutions.jsonl`.",
        "",
        "## Незакрытые гейты",
        "",
    ]
    markdown.extend(f"- `{gate}`" for gate in failed_gates)
    if not failed_gates:
        markdown.append("- Нет.")
    markdown.extend(
        [
            "",
            "## Применимые источники без канонической связи",
            "",
        ]
    )
    for row in source_rows:
        if row["video_id"] not in source_unlinked_applicable_ids:
            continue
        topics = "; ".join(row["candidate_topics"]) or "темы не перечислены"
        markdown.append(
            f"- `{row['video_id']}` — темы разрешены как reject/defer без "
            f"искусственной канонизации: {topics}"
        )
    markdown.extend(
        [
            "",
            "## Источники с неполным визуальным/аудио-доказательством",
            "",
        ]
    )
    for item in evidence_gaps:
        markdown.append(
            f"- `{item.get('video_id', '')}` — "
            f"{item.get('reason') or item.get('notes') or 'нет точного доказательства техники'}"
        )
    markdown.append("")
    (base / "technique_coverage_audit.md").write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "catalog": len(catalog_ids),
                "findings": len(findings),
                "techniques": len(techniques),
                "applicable_sources": len(applicable_source_ids),
                "applicable_topics": applicable_topics,
                "source_unlinked_applicable": len(source_unlinked_applicable_ids),
                "failed_gates": failed_gates,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

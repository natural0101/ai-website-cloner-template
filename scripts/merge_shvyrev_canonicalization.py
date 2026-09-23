"""Merge reviewed topic decisions and canonical technique proposals."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

import jsonschema


AGENT_PREFIXES = ("modeling_materials", "camera_render", "workflow_addons")
DECISION_PRECEDENCE = {
    "reject_noncanonical": 1,
    "defer_version_runtime": 2,
    "duplicate_supporting": 3,
    "map_existing": 4,
    "propose_new": 5,
}
ALIASES = {
    "shvyrev_polygon_budget_scene_preflight": "shvyrev_polygon_budget_preflight",
    "shvyrev_backend_performance_benchmark": "shvyrev_render_backend_benchmark",
    "shvyrev_cross_app_tracking_interchange_contract": "shvyrev_tracking_interchange_preflight",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def canonical_id(technique_id: str) -> str:
    while technique_id in ALIASES:
        technique_id = ALIASES[technique_id]
    return technique_id


def merge_proposals(records: list[dict[str, Any]]) -> dict[str, Any]:
    canonical = canonical_id(records[0]["id"])
    preferred = next(
        (record for record in records if record["id"] == canonical),
        records[0],
    )
    merged = json.loads(json.dumps(preferred, ensure_ascii=False))
    merged["id"] = canonical
    for field in (
        "blender_versions",
        "prerequisites",
        "actions",
        "validation",
        "failure_fixes",
    ):
        merged[field] = unique_strings(
            [
                value
                for record in records
                for value in record.get(field, [])
            ]
        )
    parameters = dict(merged.get("parameters", {}))
    for record in records:
        for key, value in record.get("parameters", {}).items():
            if key not in parameters:
                parameters[key] = value
            elif parameters[key] != value:
                parameters[f"{record['id']}__{key}"] = value
    merged["parameters"] = parameters
    adoption = merged["project_adoption"]
    adoption["targets"] = unique_strings(
        [
            target
            for record in records
            for target in record["project_adoption"].get("targets", [])
        ]
    )
    reasons = unique_strings(
        [
            record["project_adoption"].get("reason", "")
            for record in records
            if record["project_adoption"].get("reason")
        ]
    )
    if reasons:
        adoption["reason"] = " ".join(reasons)
    decisions = [
        record["project_adoption"]["decision"]
        for record in records
    ]
    adoption["decision"] = (
        "adopt"
        if "adopt" in decisions
        else "adapt"
        if "adapt" in decisions
        else "pending"
        if "pending" in decisions
        else "reject"
    )
    merged["status"] = "EXTRACTED"
    return merged


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
    canonical_dir = (base / "agent-findings" / "canonicalization").resolve()
    base.relative_to(repo)
    canonical_dir.relative_to(repo)

    findings = load_jsonl(base / "source_findings.jsonl")
    existing = load_jsonl(base / "techniques.jsonl")
    technique_schema = json.loads(
        (base / "technique.schema.json").read_text(encoding="utf-8")
    )
    finding_schema = json.loads(
        (base / "source_finding.schema.json").read_text(encoding="utf-8")
    )

    audit_rows: list[dict[str, Any]] = []
    proposal_rows: list[dict[str, Any]] = []
    audit_source_by_identity: dict[int, str] = {}
    for prefix in AGENT_PREFIXES:
        rows = load_jsonl(canonical_dir / f"{prefix}.audit.jsonl")
        audit_rows.extend(rows)
        for row in rows:
            audit_source_by_identity[id(row)] = prefix
        proposal_rows.extend(
            load_jsonl(canonical_dir / f"{prefix}.proposed-techniques.jsonl")
        )
    parent_rows = load_jsonl(canonical_dir / "parent_resolutions.audit.jsonl")
    audit_rows.extend(parent_rows)
    for row in parent_rows:
        audit_source_by_identity[id(row)] = "parent_resolutions"

    existing_by_id = {row["id"]: row for row in existing}
    if len(existing_by_id) != len(existing):
        raise RuntimeError("Existing techniques contain duplicate IDs")
    proposal_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for proposal in proposal_rows:
        proposal_groups[canonical_id(proposal["id"])].append(proposal)
    merged_proposals = [
        merge_proposals(records)
        for _, records in sorted(proposal_groups.items())
    ]
    for proposal in merged_proposals:
        if proposal["id"] in existing_by_id:
            raise RuntimeError(f"Proposal collides with existing ID: {proposal['id']}")
        jsonschema.validate(proposal, technique_schema)
    final_techniques = existing + merged_proposals
    final_by_id = {row["id"]: row for row in final_techniques}
    if len(final_by_id) != len(final_techniques):
        raise RuntimeError("Final techniques contain duplicate IDs")
    for technique in final_techniques:
        jsonschema.validate(technique, technique_schema)

    grouped_decisions: dict[
        tuple[str, str], list[tuple[dict[str, Any], str]]
    ] = collections.defaultdict(list)
    for row in audit_rows:
        source = audit_source_by_identity[id(row)]
        grouped_decisions[(row["video_id"], row["candidate_topic"])].append(
            (row, source)
        )

    applicable_pairs = {
        (finding["video_id"], topic)
        for finding in findings
        if finding["disposition"] in {"new_improvement", "mixed"}
        for topic in finding["candidate_topics"]
    }
    unknown_pairs = sorted(set(grouped_decisions) - applicable_pairs)
    missing_pairs = sorted(applicable_pairs - set(grouped_decisions))
    if unknown_pairs or missing_pairs:
        raise RuntimeError(
            f"Topic decision mismatch: unknown={len(unknown_pairs)} "
            f"missing={len(missing_pairs)}"
        )

    resolutions: list[dict[str, Any]] = []
    resolution_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    conflict_count = 0
    for finding in findings:
        disposition = finding["disposition"]
        for topic in finding["candidate_topics"]:
            pair = (finding["video_id"], topic)
            if disposition in {"new_improvement", "mixed"}:
                candidates = grouped_decisions[pair]
                decisions = {row["decision"] for row, _ in candidates}
                if len(decisions) > 1:
                    conflict_count += 1
                selected = max(
                    decisions,
                    key=lambda decision: DECISION_PRECEDENCE[decision],
                )
                technique_ids = sorted(
                    {
                        canonical_id(technique_id)
                        for row, _ in candidates
                        for technique_id in row.get("technique_ids", [])
                    }
                )
                if selected == "reject_noncanonical":
                    technique_ids = []
                unknown_ids = [
                    technique_id
                    for technique_id in technique_ids
                    if technique_id not in final_by_id
                ]
                if unknown_ids:
                    raise RuntimeError(
                        f"Unknown technique IDs for {pair}: {unknown_ids}"
                    )
                reason = " ".join(
                    unique_strings(
                        [
                            row.get("reason", "")
                            for row, _ in candidates
                            if row.get("reason")
                        ]
                    )
                )
                evidence_from = sorted({source for _, source in candidates})
                addon_treatment = (
                    "inventory"
                    if any(
                        row.get("addon_treatment") == "inventory"
                        for row, _ in candidates
                    )
                    else "not_applicable"
                )
                resolution = selected
            elif disposition == "duplicate_or_supporting_source":
                technique_ids = sorted(
                    canonical_id(technique_id)
                    for technique_id in finding["canonical_technique_ids"]
                )
                if technique_ids:
                    resolution = "duplicate_supporting"
                    reason = (
                        "Источник поддерживает уже канонизированную технику; "
                        "отдельный канон не создаётся."
                    )
                else:
                    resolution = "defer_version_runtime"
                    reason = (
                        "Supporting source не содержит достаточной связи с "
                        "существующим каноном; требуется version/runtime evidence."
                    )
                evidence_from = ["source_findings"]
                addon_treatment = "not_applicable"
            elif disposition == "addon_inventory":
                resolution = "inventory_only"
                technique_ids = []
                reason = (
                    "Упоминание сохранено в addon inventory; установка и adoption "
                    "не разрешены без vendor/license/security/runtime gate."
                )
                evidence_from = ["source_findings", "addon_inventory"]
                addon_treatment = "inventory"
            elif disposition == "showcase_only":
                resolution = "excluded_showcase"
                technique_ids = []
                reason = "В источнике нет воспроизводимого технического процесса."
                evidence_from = ["source_findings"]
                addon_treatment = "not_applicable"
            elif disposition == "not_applicable":
                resolution = "excluded_not_applicable"
                technique_ids = []
                reason = "Тема не является применимым Blender-улучшением проекта."
                evidence_from = ["source_findings"]
                addon_treatment = "not_applicable"
            else:
                raise RuntimeError(f"Unsupported disposition: {disposition}")
            record = {
                "video_id": finding["video_id"],
                "candidate_topic": topic,
                "source_disposition": disposition,
                "resolution": resolution,
                "technique_ids": technique_ids,
                "addon_treatment": addon_treatment,
                "reason": reason,
                "evidence_from": evidence_from,
            }
            resolutions.append(record)
            resolution_by_pair[pair] = record

    updated_findings = []
    for finding in findings:
        linked = set(
            canonical_id(technique_id)
            for technique_id in finding["canonical_technique_ids"]
        )
        for topic in finding["candidate_topics"]:
            linked.update(
                resolution_by_pair[(finding["video_id"], topic)]["technique_ids"]
            )
        updated = dict(finding)
        updated["canonical_technique_ids"] = sorted(linked)
        jsonschema.validate(updated, finding_schema)
        updated_findings.append(updated)

    backup_techniques = canonical_dir / "premerge_techniques.jsonl"
    backup_findings = canonical_dir / "premerge_source_findings.jsonl"
    if not backup_techniques.exists():
        write_jsonl(backup_techniques, existing)
    if not backup_findings.exists():
        write_jsonl(backup_findings, findings)
    write_jsonl(base / "techniques.jsonl", final_techniques)
    write_jsonl(base / "source_findings.jsonl", updated_findings)
    write_jsonl(base / "topic_resolutions.jsonl", resolutions)
    alias_report = {
        "schema_version": "1.0",
        "aliases": ALIASES,
        "policy": "Alias records were merged into the canonical target; audit links were rewritten.",
    }
    (base / "canonical_technique_aliases.json").write_text(
        json.dumps(alias_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    resolution_counts = collections.Counter(
        row["resolution"] for row in resolutions
    )
    report = {
        "schema_version": "1.0",
        "existing_techniques": len(existing),
        "raw_proposals": len(proposal_rows),
        "merged_new_techniques": len(merged_proposals),
        "final_techniques": len(final_techniques),
        "alias_count": len(ALIASES),
        "applicable_topics": len(applicable_pairs),
        "applicable_topics_resolved": len(applicable_pairs),
        "all_candidate_topics": len(resolutions),
        "decision_conflicts_resolved_by_precedence": conflict_count,
        "resolution_counts": dict(sorted(resolution_counts.items())),
        "invalid_links": [],
        "missing_applicable_topics": [],
        "validation": {
            "technique_schema_errors": 0,
            "source_finding_schema_errors": 0,
            "duplicate_technique_ids": 0,
        },
    }
    (base / "canonicalization_merge_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

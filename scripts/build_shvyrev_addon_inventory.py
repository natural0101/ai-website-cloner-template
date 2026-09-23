"""Aggregate every 3D SHVYREV addon mention without treating claims as adoption."""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


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
    findings = load_jsonl(base / "source_findings.jsonl")

    grouped: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for finding in findings:
        for mention in finding.get("addon_mentions", []):
            grouped[normalize_name(mention["name"])].append(
                {
                    "video_id": finding["video_id"],
                    "name": mention["name"].strip(),
                    "claim": mention["claim"].strip(),
                    "verification": mention["verification"],
                }
            )

    entries = []
    for key, mentions in grouped.items():
        name_counts = collections.Counter(mention["name"] for mention in mentions)
        display_name = sorted(
            name_counts,
            key=lambda name: (-name_counts[name], name.casefold(), name),
        )[0]
        verification = collections.Counter(
            mention["verification"] for mention in mentions
        )
        entries.append(
            {
                "normalized_name": key,
                "name": display_name,
                "aliases": sorted(name_counts),
                "source_count": len({mention["video_id"] for mention in mentions}),
                "mention_count": len(mentions),
                "verification_counts": dict(sorted(verification.items())),
                "adoption": "inventory_only",
                "adoption_gate": [
                    "official vendor or repository identity confirmed",
                    "license and cost confirmed",
                    "Blender 5.1 compatibility confirmed",
                    "permissions and network behavior reviewed",
                    "runtime test completed in an isolated copy",
                ],
                "mentions": sorted(
                    mentions,
                    key=lambda mention: (
                        mention["video_id"],
                        mention["claim"],
                    ),
                ),
            }
        )
    entries.sort(key=lambda entry: (entry["name"].casefold(), entry["name"]))

    total_mentions = sum(entry["mention_count"] for entry in entries)
    report = {
        "schema_version": "1.0",
        "policy": "Inventory is evidence, not approval. No addon is installed or adopted from caption claims alone.",
        "counts": {
            "unique_normalized_addons": len(entries),
            "mentions": total_mentions,
            "source_findings": len(findings),
        },
        "gates": {
            "all_source_mentions_accounted": total_mentions
            == sum(
                len(finding.get("addon_mentions", []))
                for finding in findings
            ),
            "automatic_adoptions": 0,
        },
        "addons": entries,
    }
    (base / "addon_inventory.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    markdown = [
        "# Инвентарь аддонов 3D SHVYREV",
        "",
        "Это доказательный каталог упоминаний, а не список разрешённых установок.",
        "",
        f"- Уникальных нормализованных названий: **{len(entries)}**.",
        f"- Упоминаний: **{total_mentions}**.",
        "- Автоматически принятых аддонов: **0**.",
        "",
        "| Аддон | Источники | Упоминания | Статусы |",
        "|---|---:|---:|---|",
    ]
    for entry in entries:
        statuses = ", ".join(
            f"{status}: {count}"
            for status, count in entry["verification_counts"].items()
        )
        markdown.append(
            f"| {entry['name']} | {entry['source_count']} | "
            f"{entry['mention_count']} | {statuses} |"
        )
    markdown.extend(
        [
            "",
            "Перед установкой любого аддона обязательны проверка официального "
            "источника, лицензии, Blender 5.1, разрешений и isolated runtime test.",
            "",
        ]
    )
    (base / "addon_inventory.md").write_text(
        "\n".join(markdown),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "unique_addons": len(entries),
                "mentions": total_mentions,
                "accounted": report["gates"]["all_source_mentions_accounted"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a traceable catalog and caption corpus for the 3D SHVYREV channel."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


SourceKind = Literal["video", "short"]

CHANNEL_URLS: tuple[tuple[SourceKind, str], ...] = (
  ("video", "https://www.youtube.com/@3D_SHVYREV/videos"),
  ("short", "https://www.youtube.com/@3D_SHVYREV/shorts"),
)


@dataclass(frozen=True)
class CatalogEntry:
  position: int
  source_kind: SourceKind
  video_id: str
  title: str
  url: str
  duration: float


def require_executable(name: str) -> str:
  executable = shutil.which(name)
  if not executable:
    raise RuntimeError(f"Missing executable in PATH: {name}")
  return executable


def run_command(args: list[str], capture: bool = False) -> str:
  process = subprocess.run(
    args,
    check=False,
    text=True,
    encoding="utf-8",
    errors="replace",
    stdout=subprocess.PIPE if capture else None,
    stderr=subprocess.PIPE if capture else None,
  )
  if process.returncode != 0:
    details = (process.stderr or process.stdout or "").strip()
    raise RuntimeError(f"Command failed ({process.returncode}): {' '.join(args)}\n{details}")
  return process.stdout if capture and process.stdout else ""


def format_duration(seconds: float) -> str:
  rounded = max(0, int(round(seconds)))
  hours, remainder = divmod(rounded, 3600)
  minutes, secs = divmod(remainder, 60)
  if hours:
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
  return f"{minutes:02d}:{secs:02d}"


def collect_catalog(yt_dlp: str) -> list[CatalogEntry]:
  entries: list[CatalogEntry] = []
  seen_ids: set[str] = set()

  for source_kind, url in CHANNEL_URLS:
    output = run_command(
      [
        yt_dlp,
        "--flat-playlist",
        "--dump-single-json",
        "--skip-download",
        "--no-warnings",
        "--extractor-args",
        "youtube:lang=ru",
        url,
      ],
      capture=True,
    )
    playlist = json.loads(output)
    for position, raw_entry in enumerate(playlist.get("entries", []), start=1):
      video_id = str(raw_entry.get("id") or "").strip()
      if not video_id or video_id in seen_ids:
        continue
      seen_ids.add(video_id)
      entries.append(
        CatalogEntry(
          position=position,
          source_kind=source_kind,
          video_id=video_id,
          title=str(raw_entry.get("title") or video_id).strip(),
          url=f"https://www.youtube.com/watch?v={video_id}",
          duration=float(raw_entry.get("duration") or 0.0),
        )
      )

  return entries


def entry_to_dict(entry: CatalogEntry) -> dict[str, object]:
  return {
    "position": entry.position,
    "source_kind": entry.source_kind,
    "video_id": entry.video_id,
    "title": entry.title,
    "url": entry.url,
    "duration_seconds": entry.duration,
    "duration": format_duration(entry.duration),
  }


def write_catalog(output_dir: Path, entries: list[CatalogEntry]) -> None:
  output_dir.mkdir(parents=True, exist_ok=True)
  generated_at = datetime.now(timezone.utc).isoformat()

  payload = {
    "channel": {
      "name": "3D SHVYREV",
      "handle": "@3D_SHVYREV",
      "channel_id": "UCv12mUx2DahFIxs9nZLDKNw",
      "url": "https://www.youtube.com/@3D_SHVYREV",
    },
    "generated_at": generated_at,
    "counts": {
      "total": len(entries),
      "videos": sum(entry.source_kind == "video" for entry in entries),
      "shorts": sum(entry.source_kind == "short" for entry in entries),
    },
    "entries": [entry_to_dict(entry) for entry in entries],
  }
  (output_dir / "channel_catalog.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )

  with (output_dir / "channel_catalog.csv").open("w", encoding="utf-8-sig", newline="") as csv_file:
    writer = csv.DictWriter(
      csv_file,
      fieldnames=[
        "position",
        "source_kind",
        "video_id",
        "title",
        "url",
        "duration_seconds",
        "duration",
      ],
    )
    writer.writeheader()
    writer.writerows(entry_to_dict(entry) for entry in entries)

  lines = [
    "# 3D SHVYREV — полный каталог",
    "",
    f"- Канал: https://www.youtube.com/@3D_SHVYREV",
    f"- Собрано: {generated_at}",
    f"- Всего: {len(entries)}",
    f"- Обычные видео: {sum(entry.source_kind == 'video' for entry in entries)}",
    f"- Shorts: {sum(entry.source_kind == 'short' for entry in entries)}",
    "",
    "| Тип | № | ID | Длительность | Название |",
    "|---|---:|---|---:|---|",
  ]
  for entry in entries:
    safe_title = entry.title.replace("|", "\\|")
    lines.append(
      f"| {entry.source_kind} | {entry.position} | "
      f"[{entry.video_id}]({entry.url}) | {format_duration(entry.duration)} | {safe_title} |"
    )
  (output_dir / "channel_catalog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def download_caption_corpus(
  yt_dlp: str,
  output_dir: Path,
  sleep_requests: float,
  sleep_subtitles: float,
  subtitle_languages: str,
) -> None:
  source_root = output_dir / "sources"
  source_root.mkdir(parents=True, exist_ok=True)

  for _, url in CHANNEL_URLS:
    run_command(
      [
        yt_dlp,
        "--ignore-errors",
        "--continue",
        "--no-overwrites",
        "--skip-download",
        "--write-info-json",
        "--write-thumbnail",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        subtitle_languages,
        "--sub-format",
        "vtt",
        "--extractor-args",
        "youtube:lang=ru",
        "--sleep-requests",
        str(sleep_requests),
        "--sleep-subtitles",
        str(sleep_subtitles),
        "--paths",
        str(source_root),
        "-o",
        "%(id)s/%(id)s.%(ext)s",
        url,
      ]
    )


def scan_coverage(output_dir: Path, entries: list[CatalogEntry]) -> dict[str, object]:
  records: list[dict[str, object]] = []
  source_root = output_dir / "sources"

  for entry in entries:
    entry_dir = source_root / entry.video_id
    caption_files = sorted(
      path.name
      for path in entry_dir.glob("*.vtt")
      if path.is_file()
    )
    info_files = sorted(path.name for path in entry_dir.glob("*.info.json") if path.is_file())
    thumbnail_files = sorted(
      path.name
      for path in entry_dir.iterdir()
      if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ) if entry_dir.exists() else []
    records.append(
      {
        "video_id": entry.video_id,
        "source_kind": entry.source_kind,
        "title": entry.title,
        "captions": caption_files,
        "info": info_files,
        "thumbnails": thumbnail_files,
        "caption_ready": bool(caption_files),
        "metadata_ready": bool(info_files),
        "visual_ready": bool(thumbnail_files),
      }
    )

  counts = {
    "total": len(records),
    "caption_ready": sum(bool(record["caption_ready"]) for record in records),
    "metadata_ready": sum(bool(record["metadata_ready"]) for record in records),
    "visual_ready": sum(bool(record["visual_ready"]) for record in records),
  }
  payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "counts": counts,
    "records": records,
  }
  (output_dir / "coverage.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )

  lines = [
    "# Покрытие источников 3D SHVYREV",
    "",
    f"- Всего: {counts['total']}",
    f"- С субтитрами: {counts['caption_ready']}",
    f"- С полной метаинформацией: {counts['metadata_ready']}",
    f"- С визуальным превью: {counts['visual_ready']}",
    "",
    "| ID | Тип | Субтитры | Метаданные | Превью | Название |",
    "|---|---|---:|---:|---:|---|",
  ]
  for record in records:
    title = str(record["title"]).replace("|", "\\|")
    lines.append(
      f"| {record['video_id']} | {record['source_kind']} | "
      f"{'да' if record['caption_ready'] else 'нет'} | "
      f"{'да' if record['metadata_ready'] else 'нет'} | "
      f"{'да' if record['visual_ready'] else 'нет'} | {title} |"
    )
  (output_dir / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
  return payload


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--out",
    type=Path,
    default=Path("docs/research/youtube-lessons/3d-shvyrev"),
    help="Output directory for the channel knowledge corpus",
  )
  parser.add_argument(
    "--download-captions",
    action="store_true",
    help="Download metadata, thumbnails and available authored/automatic subtitles",
  )
  parser.add_argument("--sleep-requests", type=float, default=0.75)
  parser.add_argument("--sleep-subtitles", type=float, default=1.0)
  parser.add_argument(
    "--subtitle-languages",
    default="ru.*",
    help="yt-dlp subtitle language selector; Russian is sufficient for this channel",
  )
  return parser


def main() -> int:
  args = build_arg_parser().parse_args()
  yt_dlp = require_executable("yt-dlp")
  entries = collect_catalog(yt_dlp)
  write_catalog(args.out, entries)

  if args.download_captions:
    download_caption_corpus(
      yt_dlp,
      args.out,
      args.sleep_requests,
      args.sleep_subtitles,
      args.subtitle_languages,
    )

  coverage = scan_coverage(args.out, entries)
  counts = coverage["counts"]
  print(
    "Catalog ready: "
    f"{len(entries)} total; "
    f"{counts['caption_ready']} captions; "
    f"{counts['metadata_ready']} metadata; "
    f"{counts['visual_ready']} previews"
  )
  return 0


if __name__ == "__main__":
  try:
    raise SystemExit(main())
  except KeyboardInterrupt:
    raise SystemExit(130)
  except Exception as error:
    print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

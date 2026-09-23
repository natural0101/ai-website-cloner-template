#!/usr/bin/env python3
"""Download and extract compact YouTube storyboard evidence for 3D SHVYREV."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from pathlib import Path


BASE_DIR = Path("docs/research/youtube-lessons/3d-shvyrev")
SOURCE_DIR = BASE_DIR / "sources"
CATALOG_PATH = BASE_DIR / "channel_catalog.json"
CHANNEL_URLS = (
  "https://www.youtube.com/@3D_SHVYREV/videos",
  "https://www.youtube.com/@3D_SHVYREV/shorts",
)


def run_download() -> None:
  yt_dlp = shutil.which("yt-dlp")
  if not yt_dlp:
    raise RuntimeError("yt-dlp is not available in PATH")
  SOURCE_DIR.mkdir(parents=True, exist_ok=True)
  for channel_url in CHANNEL_URLS:
    command = [
      yt_dlp,
      "--ignore-errors",
      "--continue",
      "--no-overwrites",
      "--skip-unavailable-fragments",
      "--extractor-args",
      "youtube:lang=ru",
      "--sleep-requests",
      "0.5",
      "-f",
      "sb0",
      "--paths",
      str(SOURCE_DIR),
      "-o",
      "%(id)s/%(id)s.storyboard.%(ext)s",
      channel_url,
    ]
    process = subprocess.run(command, check=False)
    if process.returncode != 0:
      raise RuntimeError(f"yt-dlp storyboard download failed: {process.returncode}")


def extract_storyboard(mhtml_path: Path) -> int:
  output_dir = mhtml_path.parent / "visual_frames"
  output_dir.mkdir(parents=True, exist_ok=True)
  message = BytesParser(policy=policy.default).parsebytes(mhtml_path.read_bytes())
  image_parts = [
    part
    for part in message.walk()
    if part.get_content_maintype() == "image"
  ]
  for index, part in enumerate(image_parts, start=1):
    payload = part.get_payload(decode=True)
    if not payload:
      continue
    subtype = part.get_content_subtype().lower()
    extension = ".jpg" if subtype in {"jpeg", "jpg"} else f".{subtype}"
    target = output_dir / f"storyboard_{index:04d}{extension}"
    if not target.exists():
      target.write_bytes(payload)
  return len(list(output_dir.glob("storyboard_*")))


def build_coverage() -> dict[str, object]:
  catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
  records: list[dict[str, object]] = []
  for entry in catalog["entries"]:
    video_id = str(entry["video_id"])
    source_dir = SOURCE_DIR / video_id
    mhtml_files = sorted(source_dir.glob("*.storyboard.mhtml"))
    page_count = 0
    if mhtml_files:
      page_count = extract_storyboard(mhtml_files[0])
    records.append(
      {
        "video_id": video_id,
        "source_kind": entry["source_kind"],
        "position": entry["position"],
        "title": entry["title"],
        "storyboard_ready": bool(mhtml_files),
        "storyboard_pages": page_count,
        "visually_reviewed": False,
      }
    )
  payload = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "counts": {
      "total": len(records),
      "storyboard_ready": sum(bool(record["storyboard_ready"]) for record in records),
      "storyboard_pages": sum(int(record["storyboard_pages"]) for record in records),
      "visually_reviewed": sum(bool(record["visually_reviewed"]) for record in records),
    },
    "records": records,
  }
  (BASE_DIR / "visual_coverage.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
  )
  return payload


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--download",
    action="store_true",
    help="Download sb0 storyboard MHTML for both channel tabs before extraction",
  )
  return parser


def main() -> int:
  args = build_arg_parser().parse_args()
  if args.download:
    run_download()
  payload = build_coverage()
  counts = payload["counts"]
  print(
    f"Visual corpus: {counts['storyboard_ready']}/{counts['total']} sources; "
    f"{counts['storyboard_pages']} storyboard pages"
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

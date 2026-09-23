#!/usr/bin/env python3
"""Normalize downloaded 3D SHVYREV WebVTT captions into reviewable transcripts."""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


TIMING_RE = re.compile(
  r"^(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+"
  r"(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})"
)
TAG_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"[\wёЁ]+(?:[-'][\wёЁ]+)*|[^\w\s]", flags=re.UNICODE)
NO_SPACE_BEFORE = set(".,!?;:%)]}»")
NO_SPACE_AFTER = set("([{«")


@dataclass(frozen=True)
class Cue:
  start: float
  end: float
  text: str


def parse_timecode(value: str) -> float:
  hours, minutes, seconds = value.split(":")
  return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_time(seconds: float) -> str:
  rounded = max(0, int(seconds))
  hours, remainder = divmod(rounded, 3600)
  minutes, secs = divmod(remainder, 60)
  if hours:
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
  return f"{minutes:02d}:{secs:02d}"


def clean_caption_text(lines: list[str]) -> str:
  text = " ".join(line.strip() for line in lines if line.strip())
  text = TAG_RE.sub("", text)
  text = html.unescape(text)
  return re.sub(r"\s+", " ", text).strip()


def parse_vtt(path: Path) -> list[Cue]:
  content = path.read_text(encoding="utf-8-sig", errors="replace")
  blocks = re.split(r"\r?\n\r?\n+", content)
  cues: list[Cue] = []

  for block in blocks:
    lines = block.splitlines()
    timing_index = next(
      (index for index, line in enumerate(lines) if TIMING_RE.match(line.strip())),
      None,
    )
    if timing_index is None:
      continue
    match = TIMING_RE.match(lines[timing_index].strip())
    if match is None:
      continue
    text = clean_caption_text(lines[timing_index + 1 :])
    if not text:
      continue
    cues.append(
      Cue(
        start=parse_timecode(match.group("start")),
        end=parse_timecode(match.group("end")),
        text=text,
      )
    )

  return cues


def token_key(token: str) -> str:
  return token.casefold()


def untokenize(tokens: list[str]) -> str:
  result = ""
  for token in tokens:
    if not result:
      result = token
    elif token in NO_SPACE_BEFORE or result[-1] in NO_SPACE_AFTER:
      result += token
    else:
      result += " " + token
  return result


def append_non_overlapping(existing: list[str], incoming: list[str]) -> list[str]:
  max_overlap = min(len(existing), len(incoming))
  for overlap in range(max_overlap, 0, -1):
    existing_tail = [token_key(token) for token in existing[-overlap:]]
    incoming_head = [token_key(token) for token in incoming[:overlap]]
    if existing_tail == incoming_head:
      return incoming[overlap:]
  return incoming


def reconstruct(cues: list[Cue]) -> tuple[list[dict[str, object]], str]:
  accumulated: list[str] = []
  segments: list[dict[str, object]] = []

  for cue in cues:
    incoming = TOKEN_RE.findall(cue.text)
    appended = append_non_overlapping(accumulated, incoming)
    if not appended:
      continue
    accumulated.extend(appended)
    segments.append(
      {
        "start": cue.start,
        "end": cue.end,
        "timecode": f"{format_time(cue.start)}-{format_time(cue.end)}",
        "text": untokenize(appended),
      }
    )

  return segments, untokenize(accumulated)


def select_caption(entry_dir: Path, video_id: str) -> Path | None:
  preferred_suffixes = (
    "ru-orig.vtt",
    "ru.vtt",
    "en-orig.vtt",
    "en.vtt",
  )
  for suffix in preferred_suffixes:
    candidate = entry_dir / f"{video_id}.{suffix}"
    if candidate.exists():
      return candidate

  candidates = sorted(entry_dir.glob("*.vtt"))
  return candidates[0] if candidates else None


def chunk_segments(
  segments: list[dict[str, object]],
  chunk_seconds: int,
) -> list[dict[str, object]]:
  chunks: list[dict[str, object]] = []
  grouped: dict[int, list[dict[str, object]]] = {}
  for segment in segments:
    start = float(segment["start"])
    bucket = int(start // chunk_seconds) * chunk_seconds
    grouped.setdefault(bucket, []).append(segment)

  for bucket in sorted(grouped):
    bucket_segments = grouped[bucket]
    chunks.append(
      {
        "start": bucket,
        "end": bucket + chunk_seconds,
        "timecode": f"{format_time(bucket)}-{format_time(bucket + chunk_seconds)}",
        "text": " ".join(str(segment["text"]) for segment in bucket_segments).strip(),
      }
    )
  return chunks


def write_transcript(
  entry: dict[str, object],
  caption_path: Path,
  chunk_seconds: int,
) -> dict[str, object]:
  cues = parse_vtt(caption_path)
  segments, full_text = reconstruct(cues)
  chunks = chunk_segments(segments, chunk_seconds)
  entry_dir = caption_path.parent
  generated_at = datetime.now(timezone.utc).isoformat()

  payload = {
    "source": {
      "video_id": entry["video_id"],
      "source_kind": entry["source_kind"],
      "title": entry["title"],
      "url": entry["url"],
      "caption_file": caption_path.name,
    },
    "generated_at": generated_at,
    "cue_count": len(cues),
    "segment_count": len(segments),
    "character_count": len(full_text),
    "full_text": full_text,
    "segments": segments,
    "chunks": chunks,
  }
  (entry_dir / "transcript.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )

  lines = [
    f"# {entry['title']}",
    "",
    f"- Source: {entry['url']}",
    f"- Kind: {entry['source_kind']}",
    f"- Caption: `{caption_path.name}`",
    f"- Generated: {generated_at}",
    "",
    "## Транскрипт",
    "",
  ]
  for chunk in chunks:
    lines.extend(
      [
        f"### {chunk['timecode']}",
        "",
        str(chunk["text"]),
        "",
      ]
    )
  (entry_dir / "transcript.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

  return {
    "video_id": entry["video_id"],
    "source_kind": entry["source_kind"],
    "title": entry["title"],
    "caption_file": caption_path.name,
    "cue_count": len(cues),
    "segment_count": len(segments),
    "character_count": len(full_text),
    "transcript_ready": bool(full_text),
  }


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
    "--root",
    type=Path,
    default=Path("docs/research/youtube-lessons/3d-shvyrev"),
  )
  parser.add_argument("--chunk-seconds", type=int, default=30)
  return parser


def main() -> int:
  args = build_arg_parser().parse_args()
  catalog = json.loads((args.root / "channel_catalog.json").read_text(encoding="utf-8"))
  records: list[dict[str, object]] = []

  for entry in catalog["entries"]:
    video_id = str(entry["video_id"])
    entry_dir = args.root / "sources" / video_id
    caption_path = select_caption(entry_dir, video_id) if entry_dir.exists() else None
    if caption_path is None:
      records.append(
        {
          "video_id": video_id,
          "source_kind": entry["source_kind"],
          "title": entry["title"],
          "transcript_ready": False,
        }
      )
      continue
    records.append(write_transcript(entry, caption_path, args.chunk_seconds))

  counts = {
    "total": len(records),
    "transcript_ready": sum(bool(record["transcript_ready"]) for record in records),
    "missing": sum(not bool(record["transcript_ready"]) for record in records),
  }
  coverage = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "counts": counts,
    "records": records,
  }
  (args.root / "transcript_coverage.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  print(
    f"Transcripts ready: {counts['transcript_ready']}/{counts['total']}; "
    f"missing: {counts['missing']}"
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())

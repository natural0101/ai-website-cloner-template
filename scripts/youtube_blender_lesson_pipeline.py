#!/usr/bin/env python3
"""
Turn a YouTube Blender lesson into agent-ready Markdown and JSON.

MVP:
  1. Download video/audio with yt-dlp.
  2. Transcribe audio with faster-whisper.
  3. Extract screenshots with ffmpeg.
  4. Optionally analyze frames with OpenAI vision.
  5. Write lesson.json and lesson.md.

Example:
  python scripts/youtube_blender_lesson_pipeline.py "https://youtube.com/watch?v=..." --vision-provider openai
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


VisionProvider = Literal["none", "openai"]


@dataclass(frozen=True)
class TranscriptSegment:
  start: float
  end: float
  text: str
  words: list[dict[str, object]]


@dataclass(frozen=True)
class FrameRecord:
  time: float
  timecode: str
  path: Path
  analysis: dict[str, object] | None = None


def run_command(args: list[str], cwd: Path | None = None, capture: bool = False) -> str:
  process = subprocess.run(
    args,
    cwd=str(cwd) if cwd else None,
    check=False,
    text=True,
    stdout=subprocess.PIPE if capture else None,
    stderr=subprocess.PIPE if capture else None,
  )
  if process.returncode != 0:
    stderr = process.stderr.strip() if process.stderr else ""
    stdout = process.stdout.strip() if process.stdout else ""
    details = stderr or stdout or f"exit code {process.returncode}"
    raise RuntimeError(f"Command failed: {' '.join(args)}\n{details}")
  return process.stdout if capture and process.stdout else ""


def require_executable(name: str) -> str:
  path = shutil.which(name)
  if not path:
    raise RuntimeError(f"Missing executable in PATH: {name}")
  return path


def slugify(value: str, fallback: str) -> str:
  value = value.strip().lower()
  value = re.sub(r"https?://", "", value)
  value = re.sub(r"[^a-z0-9а-яё]+", "-", value, flags=re.IGNORECASE)
  value = re.sub(r"-+", "-", value).strip("-")
  return value[:90] or fallback


def format_time(seconds: float) -> str:
  seconds_int = max(0, int(round(seconds)))
  hours = seconds_int // 3600
  minutes = (seconds_int % 3600) // 60
  secs = seconds_int % 60
  if hours:
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
  return f"{minutes:02d}:{secs:02d}"


def load_json(path: Path) -> dict[str, object]:
  return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
  path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def probe_duration(video_path: Path) -> float:
  output = run_command(
    [
      "ffprobe",
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-of",
      "default=noprint_wrappers=1:nokey=1",
      str(video_path),
    ],
    capture=True,
  ).strip()
  return float(output)


def get_video_info(url: str) -> dict[str, object]:
  output = run_command(["yt-dlp", "--dump-json", "--no-playlist", url], capture=True)
  return json.loads(output)


def download_sources(
  url: str,
  source_dir: Path,
  video_format: str,
  sub_langs: str,
  cookies_from_browser: str | None,
) -> tuple[Path, Path, list[Path]]:
  source_dir.mkdir(parents=True, exist_ok=True)

  common_args = ["yt-dlp", "--no-playlist"]
  if cookies_from_browser:
    common_args.extend(["--cookies-from-browser", cookies_from_browser])

  audio_path = source_dir / "audio.mp3"
  if not audio_path.exists():
    run_command(
      [
        *common_args,
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        str(source_dir / "audio.%(ext)s"),
        url,
      ]
    )

  video_path = source_dir / "video.mp4"
  if not video_path.exists():
    run_command(
      [
        *common_args,
        "-f",
        video_format,
        "--merge-output-format",
        "mp4",
        "-o",
        str(source_dir / "video.%(ext)s"),
        url,
      ]
    )

  run_command(
    [
      *common_args,
      "--skip-download",
      "--write-subs",
      "--write-auto-subs",
      "--sub-langs",
      sub_langs,
      "--convert-subs",
      "srt",
      "-o",
      str(source_dir / "captions.%(ext)s"),
      url,
    ],
    capture=True,
  )

  caption_paths = sorted(source_dir.glob("captions*.srt"))
  return audio_path, video_path, caption_paths


def transcribe_audio(
  audio_path: Path,
  model_name: str,
  language: str | None,
  device: str,
  compute_type: str,
  word_timestamps: bool,
) -> tuple[list[TranscriptSegment], dict[str, object]]:
  try:
    from faster_whisper import WhisperModel
  except ImportError as exc:
    raise RuntimeError(
      "Install faster-whisper first: python -m pip install faster-whisper"
    ) from exc

  model = WhisperModel(model_name, device=device, compute_type=compute_type)
  raw_segments, info = model.transcribe(
    str(audio_path),
    language=language,
    beam_size=5,
    vad_filter=True,
    word_timestamps=word_timestamps,
  )

  segments: list[TranscriptSegment] = []
  for segment in raw_segments:
    words: list[dict[str, object]] = []
    if getattr(segment, "words", None):
      words = [
        {
          "start": float(word.start),
          "end": float(word.end),
          "word": word.word,
          "probability": float(word.probability),
        }
        for word in segment.words
      ]
    segments.append(
      TranscriptSegment(
        start=float(segment.start),
        end=float(segment.end),
        text=segment.text.strip(),
        words=words,
      )
    )

  info_dict = {
    "language": getattr(info, "language", None),
    "language_probability": getattr(info, "language_probability", None),
    "duration": getattr(info, "duration", None),
    "duration_after_vad": getattr(info, "duration_after_vad", None),
  }
  return segments, info_dict


def extract_frames(
  video_path: Path,
  frames_dir: Path,
  duration: float,
  frame_interval: int,
  max_frames: int,
  height: int,
) -> list[FrameRecord]:
  frames_dir.mkdir(parents=True, exist_ok=True)
  if duration <= 0:
    duration = probe_duration(video_path)

  total = min(max_frames, math.floor(duration / frame_interval) + 1)
  records: list[FrameRecord] = []

  for index in range(total):
    seconds = min(index * frame_interval, duration)
    frame_path = frames_dir / f"frame_{int(seconds):06d}.jpg"
    if not frame_path.exists():
      run_command(
        [
          "ffmpeg",
          "-hide_banner",
          "-loglevel",
          "error",
          "-ss",
          str(seconds),
          "-i",
          str(video_path),
          "-frames:v",
          "1",
          "-vf",
          f"scale=-2:{height}",
          "-q:v",
          "3",
          str(frame_path),
        ]
      )
    records.append(FrameRecord(time=seconds, timecode=format_time(seconds), path=frame_path))

  return records


def image_to_data_url(path: Path) -> str:
  data = base64.b64encode(path.read_bytes()).decode("ascii")
  return f"data:image/jpeg;base64,{data}"


def parse_json_object(text: str) -> dict[str, object]:
  stripped = text.strip()
  if stripped.startswith("```"):
    stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
    stripped = re.sub(r"```$", "", stripped).strip()
  try:
    value = json.loads(stripped)
    if isinstance(value, dict):
      return value
  except json.JSONDecodeError:
    pass
  return {"raw": text}


def analyze_frame_openai(frame: FrameRecord, model: str) -> dict[str, object]:
  try:
    from openai import OpenAI
  except ImportError as exc:
    raise RuntimeError("Install openai first: python -m pip install openai") from exc

  client = OpenAI()
  prompt = (
    "You are analyzing a screenshot from a Blender tutorial. "
    "Return only compact JSON with these keys: visible_context, likely_action, "
    "hotkeys_or_tools, parameters_values, objects, materials_lighting_render, "
    "uncertainties. Focus on actionable details for a Blender agent."
  )
  response = client.responses.create(
    model=model,
    input=[
      {
        "role": "user",
        "content": [
          {"type": "input_text", "text": f"Timestamp: {frame.timecode}. {prompt}"},
          {"type": "input_image", "image_url": image_to_data_url(frame.path), "detail": "high"},
        ],
      }
    ],
  )
  text = getattr(response, "output_text", str(response))
  result = parse_json_object(text)
  result["provider"] = "openai"
  result["model"] = model
  return result


def analyze_frames(
  frames: list[FrameRecord],
  provider: VisionProvider,
  model: str,
  cache_path: Path,
) -> list[FrameRecord]:
  cached: dict[str, dict[str, object]] = {}
  if cache_path.exists():
    raw_cache = load_json(cache_path)
    cached = {
      str(item.get("timecode")): item
      for item in raw_cache.get("frames", [])
      if isinstance(item, dict)
    }

  analyzed: list[FrameRecord] = []
  for frame in frames:
    analysis = cached.get(frame.timecode)
    if provider == "openai" and analysis is None:
      analysis = analyze_frame_openai(frame, model)
    analyzed.append(
      FrameRecord(
        time=frame.time,
        timecode=frame.timecode,
        path=frame.path,
        analysis=analysis,
      )
    )

  if provider != "none":
    write_json(
      cache_path,
      {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frames": [frame_to_json(frame, cache_path.parent.parent) for frame in analyzed],
      },
    )

  return analyzed


def segment_to_json(segment: TranscriptSegment) -> dict[str, object]:
  return {
    "start": segment.start,
    "end": segment.end,
    "timecode": f"{format_time(segment.start)}-{format_time(segment.end)}",
    "text": segment.text,
    "words": segment.words,
  }


def frame_to_json(frame: FrameRecord, base_dir: Path) -> dict[str, object]:
  try:
    rel_path = frame.path.relative_to(base_dir)
  except ValueError:
    rel_path = frame.path
  return {
    "time": frame.time,
    "timecode": frame.timecode,
    "file": rel_path.as_posix(),
    "analysis": frame.analysis,
  }


def chunk_segments(
  segments: list[TranscriptSegment],
  frames: list[FrameRecord],
  chunk_seconds: int,
) -> list[dict[str, object]]:
  if not segments:
    return []

  start = math.floor(segments[0].start / chunk_seconds) * chunk_seconds
  end = math.ceil(max(segment.end for segment in segments) / chunk_seconds) * chunk_seconds
  chunks: list[dict[str, object]] = []

  cursor = start
  while cursor < end:
    next_cursor = cursor + chunk_seconds
    chunk_transcript = [
      segment_to_json(segment)
      for segment in segments
      if segment.start < next_cursor and segment.end >= cursor
    ]
    chunk_frames = [
      frame_to_json(frame, frame.path.parents[1])
      for frame in frames
      if cursor <= frame.time < next_cursor
    ]
    if chunk_transcript or chunk_frames:
      chunks.append(
        {
          "start": cursor,
          "end": next_cursor,
          "timecode": f"{format_time(cursor)}-{format_time(next_cursor)}",
          "transcript": chunk_transcript,
          "frames": chunk_frames,
        }
      )
    cursor = next_cursor

  return chunks


def build_markdown(
  info: dict[str, object],
  url: str,
  segments: list[TranscriptSegment],
  frames: list[FrameRecord],
  caption_paths: list[Path],
  chunks: list[dict[str, object]],
) -> str:
  title = str(info.get("title") or "YouTube Blender lesson")
  channel = str(info.get("channel") or info.get("uploader") or "Unknown channel")
  duration = float(info.get("duration") or 0)

  lines = [
    f"# {title}",
    "",
    f"- Source: {url}",
    f"- Channel: {channel}",
    f"- Duration: {format_time(duration)}",
    f"- Generated: {datetime.now(timezone.utc).isoformat()}",
    f"- Captions downloaded: {len(caption_paths)}",
    f"- Transcript segments: {len(segments)}",
    f"- Frames: {len(frames)}",
    "",
    "## Agent Instruction Pack",
    "",
    "Use this as a factual reconstruction of the tutorial. Prefer exact transcript and visible UI evidence over guesses. Treat uncertain frame observations as hypotheses.",
    "",
  ]

  for chunk in chunks:
    lines.append(f"### {chunk['timecode']}")
    lines.append("")

    frame_items = chunk.get("frames", [])
    if frame_items:
      lines.append("Screen observations:")
      for frame_item in frame_items:
        analysis = frame_item.get("analysis") if isinstance(frame_item, dict) else None
        if isinstance(analysis, dict) and analysis:
          likely_action = analysis.get("likely_action") or analysis.get("raw") or "visual note"
          lines.append(f"- {frame_item.get('timecode')}: {likely_action}")
        elif isinstance(frame_item, dict):
          lines.append(f"- {frame_item.get('timecode')}: screenshot saved at `{frame_item.get('file')}`")
      lines.append("")

    transcript_items = chunk.get("transcript", [])
    if transcript_items:
      lines.append("Speech:")
      for item in transcript_items:
        if isinstance(item, dict):
          lines.append(f"- {item.get('timecode')}: {item.get('text')}")
      lines.append("")

  return "\n".join(lines).strip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("url", help="YouTube video URL")
  parser.add_argument(
    "--out",
    type=Path,
    default=Path("docs/research/youtube-lessons"),
    help="Output root directory",
  )
  parser.add_argument("--whisper-model", default="medium", help="tiny/base/small/medium/large-v3")
  parser.add_argument("--language", default=None, help="Optional language hint, e.g. en or ru")
  parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Whisper device")
  parser.add_argument("--compute-type", default="int8", help="Whisper compute type")
  parser.add_argument("--word-timestamps", action="store_true", help="Include word-level timestamps")
  parser.add_argument("--frame-interval", type=int, default=30, help="Seconds between screenshots")
  parser.add_argument("--max-frames", type=int, default=120, help="Maximum screenshots")
  parser.add_argument("--frame-height", type=int, default=720, help="Screenshot height")
  parser.add_argument("--chunk-seconds", type=int, default=180, help="Markdown grouping size")
  parser.add_argument(
    "--video-format",
    default="bv*[height<=1080]+ba/b[height<=1080]/b",
    help="yt-dlp format selector",
  )
  parser.add_argument(
    "--sub-langs",
    default="en.*,ru.*",
    help="yt-dlp subtitle language selector",
  )
  parser.add_argument(
    "--cookies-from-browser",
    default=None,
    help="Browser name for yt-dlp cookies, e.g. chrome, edge, firefox",
  )
  parser.add_argument(
    "--vision-provider",
    default="none",
    choices=["none", "openai"],
    help="Optional frame analysis provider",
  )
  parser.add_argument(
    "--vision-model",
    default="gpt-4.1-mini",
    help="OpenAI vision-capable model",
  )
  return parser


def main() -> int:
  parser = build_arg_parser()
  args = parser.parse_args()

  require_executable("yt-dlp")
  require_executable("ffmpeg")
  require_executable("ffprobe")

  info = get_video_info(args.url)
  video_id = str(info.get("id") or "video")
  title_slug = slugify(str(info.get("title") or video_id), video_id)
  output_dir = args.out / f"{title_slug}-{video_id}"
  source_dir = output_dir / "source"
  frames_dir = output_dir / "frames"
  output_dir.mkdir(parents=True, exist_ok=True)

  write_json(output_dir / "source_info.json", info)

  print(f"[1/5] Downloading sources into {output_dir}")
  audio_path, video_path, caption_paths = download_sources(
    args.url,
    source_dir,
    args.video_format,
    args.sub_langs,
    args.cookies_from_browser,
  )

  print("[2/5] Transcribing audio")
  transcript_path = output_dir / "transcript.json"
  if transcript_path.exists():
    transcript_raw = load_json(transcript_path)
    segments = [
      TranscriptSegment(
        start=float(item["start"]),
        end=float(item["end"]),
        text=str(item["text"]),
        words=list(item.get("words", [])),
      )
      for item in transcript_raw.get("segments", [])
      if isinstance(item, dict)
    ]
    transcription_info = dict(transcript_raw.get("info", {}))
  else:
    segments, transcription_info = transcribe_audio(
      audio_path,
      args.whisper_model,
      args.language,
      args.device,
      args.compute_type,
      args.word_timestamps,
    )
    write_json(
      transcript_path,
      {
        "info": transcription_info,
        "segments": [segment_to_json(segment) for segment in segments],
      },
    )

  print("[3/5] Extracting frames")
  duration = float(info.get("duration") or transcription_info.get("duration") or 0)
  frames = extract_frames(
    video_path,
    frames_dir,
    duration,
    args.frame_interval,
    args.max_frames,
    args.frame_height,
  )

  print("[4/5] Analyzing frames" if args.vision_provider != "none" else "[4/5] Skipping frame analysis")
  analyzed_frames = analyze_frames(
    frames,
    args.vision_provider,
    args.vision_model,
    output_dir / "frame_analysis.json",
  )

  print("[5/5] Writing lesson.json and lesson.md")
  chunks = chunk_segments(segments, analyzed_frames, args.chunk_seconds)
  lesson = {
    "source": {
      "url": args.url,
      "title": info.get("title"),
      "channel": info.get("channel") or info.get("uploader"),
      "id": video_id,
      "duration": duration,
    },
    "pipeline": {
      "generated_at": datetime.now(timezone.utc).isoformat(),
      "transcriber": "faster-whisper",
      "whisper_model": args.whisper_model,
      "vision_provider": args.vision_provider,
      "vision_model": args.vision_model if args.vision_provider != "none" else None,
    },
    "captions": [path.name for path in caption_paths],
    "transcript": [segment_to_json(segment) for segment in segments],
    "frames": [frame_to_json(frame, output_dir) for frame in analyzed_frames],
    "chunks": chunks,
  }
  write_json(output_dir / "lesson.json", lesson)
  (output_dir / "lesson.md").write_text(
    build_markdown(info, args.url, segments, analyzed_frames, caption_paths, chunks),
    encoding="utf-8",
  )

  print(f"Done: {output_dir / 'lesson.md'}")
  return 0


if __name__ == "__main__":
  try:
    raise SystemExit(main())
  except KeyboardInterrupt:
    raise SystemExit(130)
  except Exception as error:
    print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

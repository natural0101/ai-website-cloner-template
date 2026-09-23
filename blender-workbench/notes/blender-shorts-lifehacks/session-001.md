# Session 001 - 2026-06-25

User request: continue watching roughly 1000 Blender Shorts in order, learn lifehacks, and record them.

## What Changed

- Created `blender-workbench/notes/blender-shorts-lifehacks/`.
- Seeded the queue with the 10 Shorts already used for `jojo_anime_playing_cards_v1`.
- Added sources `011-100` from Blender Shorts search results.
- Distilled 40 reusable lifehacks into `lifehacks.md`.

## Tool Notes

- `yt-dlp` is installed: version `2026.06.09`.
- YouTube search through `yt-dlp ytsearch` hit repeated `ConnectionResetError 10054`, so the first expansion used web search results and direct YouTube URLs.
- Because several Shorts only exposed titles/snippets in search, they are marked `queued` or `metadata-reviewed` instead of falsely marked as fully watched.

## Current Counters

| Counter | Value |
|---|---:|
| Target sources | ~1000 |
| Sources queued | 100 |
| Sources applied in real Blender scene | 10 |
| Lifehacks distilled | 40 |
| Next checkpoint | 150 queued sources |

## Next Batch Plan

1. Search by category: modeling, animation, lighting, materials, camera, geometry nodes, web export.
2. Prefer Shorts with visible tutorial intent over promo-only videos.
3. Try direct metadata/caption extraction per URL instead of global `ytsearch`.
4. For every 50 Shorts, add at least 10 concrete lifehacks or mark the source as weak.
5. Every 100 Shorts, run a small Blender test scene that applies 5-10 new tricks.

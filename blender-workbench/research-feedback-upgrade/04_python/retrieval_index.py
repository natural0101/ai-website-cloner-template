"""Small dependency-free BM25-style retrieval for verified Blender examples."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import math
from pathlib import Path
import re
from typing import Iterable

TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9_]+")


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in TOKEN_RE.finditer(text)]


@dataclass(frozen=True)
class SearchResult:
    score: float
    record: dict


class ExampleIndex:
    def __init__(self, records: Iterable[dict]):
        self.records = list(records)
        if not self.records:
            raise ValueError("At least one example record is required")
        self.docs = [self._record_tokens(r) for r in self.records]
        self.lengths = [len(d) for d in self.docs]
        self.avg_len = sum(self.lengths) / len(self.lengths)
        self.df: Counter[str] = Counter()
        for doc in self.docs:
            self.df.update(set(doc))

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "ExampleIndex":
        records: list[dict] = []
        with Path(path).open('r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at line {line_no}: {exc}") from exc
        return cls(records)

    def search(self, query: str, top_k: int = 5, required_tags: set[str] | None = None) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        required = {t.casefold() for t in (required_tags or set())}
        results: list[SearchResult] = []
        n = len(self.records)
        k1, b = 1.5, 0.75
        for record, doc, doc_len in zip(self.records, self.docs, self.lengths):
            tags = {str(t).casefold() for t in record.get('tags', [])}
            if required and not required.issubset(tags):
                continue
            tf = Counter(doc)
            score = 0.0
            for term in q_tokens:
                df = self.df.get(term, 0)
                idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
                freq = tf.get(term, 0)
                denom = freq + k1 * (1 - b + b * doc_len / max(self.avg_len, 1.0))
                if denom:
                    score += idf * (freq * (k1 + 1)) / denom
            if score > 0:
                results.append(SearchResult(score=score, record=record))
        results.sort(key=lambda x: (-x.score, x.record.get('id', '')))
        return results[:top_k]

    @staticmethod
    def _record_tokens(record: dict) -> list[str]:
        fields = [
            record.get('title', ''), record.get('task', ''), record.get('representation', ''),
            ' '.join(record.get('tags', [])), ' '.join(record.get('workflow', [])),
            ' '.join(record.get('success_criteria', [])), ' '.join(record.get('known_failures', [])),
        ]
        return tokenize(' '.join(map(str, fields)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonl')
    parser.add_argument('query')
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--tag', action='append', default=[])
    args = parser.parse_args()
    index = ExampleIndex.from_jsonl(args.jsonl)
    results = index.search(args.query, top_k=args.top_k, required_tags=set(args.tag))
    print(json.dumps([{'score': round(r.score, 4), **r.record} for r in results], ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

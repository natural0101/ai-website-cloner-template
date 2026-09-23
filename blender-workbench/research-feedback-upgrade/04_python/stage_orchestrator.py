"""Dependency-free state machine for staged Blender work.

This module does not call Blender. It keeps stage scope, attempt history,
checkpoints, error classes and a bounded memory window deterministic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any


class Stage(str, Enum):
    INTAKE = "INTAKE"
    INITIALIZATION = "INITIALIZATION"
    GEOMETRY = "GEOMETRY"
    MATERIAL = "MATERIAL"
    COMPOSITION = "COMPOSITION"
    LIGHTING = "LIGHTING"
    EXPORT_QA = "EXPORT_QA"
    DONE = "DONE"


STAGE_ORDER = list(Stage)
STAGE_BUDGETS = {
    Stage.INTAKE: 1,
    Stage.INITIALIZATION: 2,
    Stage.GEOMETRY: 5,
    Stage.MATERIAL: 3,
    Stage.COMPOSITION: 3,
    Stage.LIGHTING: 2,
    Stage.EXPORT_QA: 2,
    Stage.DONE: 0,
}
STAGE_SCOPES = {
    Stage.INTAKE: {"spec", "reference", "acceptance"},
    Stage.INITIALIZATION: {"units", "collections", "names", "camera_scaffold", "reference_plane"},
    Stage.GEOMETRY: {"mesh", "curve", "modifiers", "part_transforms", "connections"},
    Stage.MATERIAL: {"materials", "shader_nodes", "textures", "uv"},
    Stage.COMPOSITION: {"object_transforms", "parenting", "camera"},
    Stage.LIGHTING: {"lights", "world", "exposure", "color_management"},
    Stage.EXPORT_QA: {"validation", "export_copy", "triangulation", "decimation"},
    Stage.DONE: set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Attempt:
    attempt_id: str
    stage: str
    action: str
    changed_scope: list[str]
    render_paths: list[str] = field(default_factory=list)
    audit_path: str | None = None
    approved: bool | None = None
    dominant_mismatch: str | None = None
    next_edit: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    created_at: str = field(default_factory=now_iso)


@dataclass
class StageRecord:
    status: str = "PENDING"
    attempts: int = 0
    approved_attempt_id: str | None = None
    checkpoint: str | None = None
    checklist: list[str] = field(default_factory=list)


@dataclass
class ProjectState:
    schema_version: str
    project_id: str
    goal: str
    active_stage: str
    stages: dict[str, StageRecord]
    attempts: list[Attempt] = field(default_factory=list)
    authoritative_state: str | None = None
    unresolved: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=now_iso)


class StageError(RuntimeError):
    pass


class ScopeViolation(StageError):
    pass


class BudgetExceeded(StageError):
    pass


class StageOrchestrator:
    def __init__(self, state: ProjectState, memory_limit: int = 5):
        if memory_limit < 1:
            raise ValueError("memory_limit must be >= 1")
        self.state = state
        self.memory_limit = memory_limit

    @classmethod
    def create(cls, project_id: str, goal: str, memory_limit: int = 5) -> "StageOrchestrator":
        stages = {stage.value: StageRecord() for stage in Stage}
        stages[Stage.INTAKE.value].status = "ACTIVE"
        state = ProjectState(
            schema_version="1.0",
            project_id=project_id,
            goal=goal,
            active_stage=Stage.INTAKE.value,
            stages=stages,
        )
        return cls(state, memory_limit=memory_limit)

    @property
    def active_stage(self) -> Stage:
        return Stage(self.state.active_stage)

    def allowed_scope(self) -> set[str]:
        return set(STAGE_SCOPES[self.active_stage])

    def validate_scope(self, changed_scope: list[str]) -> None:
        unexpected = set(changed_scope) - self.allowed_scope()
        if unexpected:
            raise ScopeViolation(
                f"Stage {self.active_stage.value} forbids scopes: {sorted(unexpected)}; "
                f"allowed: {sorted(self.allowed_scope())}"
            )

    def record_attempt(
        self,
        attempt_id: str,
        action: str,
        changed_scope: list[str],
        render_paths: list[str] | None = None,
        audit_path: str | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> Attempt:
        stage = self.active_stage
        if stage is Stage.DONE:
            raise StageError("Project is already DONE")
        record = self.state.stages[stage.value]
        if record.attempts >= STAGE_BUDGETS[stage]:
            raise BudgetExceeded(f"Attempt budget exhausted for {stage.value}")
        self.validate_scope(changed_scope)
        if any(a.attempt_id == attempt_id for a in self.state.attempts):
            raise StageError(f"Duplicate attempt_id: {attempt_id}")
        attempt = Attempt(
            attempt_id=attempt_id,
            stage=stage.value,
            action=action,
            changed_scope=changed_scope,
            render_paths=render_paths or [],
            audit_path=audit_path,
            error_type=error_type,
            error_message=error_message,
        )
        self.state.attempts.append(attempt)
        record.attempts += 1
        self._touch()
        return attempt

    def review_attempt(
        self,
        attempt_id: str,
        approved: bool,
        dominant_mismatch: str | None = None,
        next_edit: str | None = None,
        checklist: list[str] | None = None,
    ) -> Attempt:
        attempt = self._get_attempt(attempt_id)
        if attempt.stage != self.active_stage.value:
            raise StageError("Can only review an attempt in the active stage")
        attempt.approved = approved
        attempt.dominant_mismatch = dominant_mismatch
        attempt.next_edit = next_edit
        if checklist is not None:
            self.state.stages[self.active_stage.value].checklist = list(checklist)
            self.state.unresolved = list(checklist)
        self._touch()
        return attempt

    def approve_stage(self, attempt_id: str, checkpoint: str) -> None:
        attempt = self._get_attempt(attempt_id)
        if attempt.stage != self.active_stage.value or attempt.approved is not True:
            raise StageError("Stage can be approved only from an approved active-stage attempt")
        record = self.state.stages[self.active_stage.value]
        record.status = "APPROVED"
        record.approved_attempt_id = attempt_id
        record.checkpoint = checkpoint
        self.state.authoritative_state = checkpoint
        self.state.unresolved = []
        idx = STAGE_ORDER.index(self.active_stage)
        next_stage = STAGE_ORDER[idx + 1]
        self.state.active_stage = next_stage.value
        self.state.stages[next_stage.value].status = "ACTIVE" if next_stage is not Stage.DONE else "APPROVED"
        self._touch()

    def rollback_active_stage(self) -> str | None:
        checkpoint = self.state.authoritative_state
        record = self.state.stages[self.active_stage.value]
        record.status = "ACTIVE"
        record.checklist = []
        self.state.unresolved = []
        self._touch()
        return checkpoint

    def memory_window(self) -> dict[str, Any]:
        return {
            "goal": self.state.goal,
            "active_stage": self.state.active_stage,
            "authoritative_state": self.state.authoritative_state,
            "unresolved": self.state.unresolved,
            "allowed_scope": sorted(self.allowed_scope()),
            "last_attempts": [asdict(a) for a in self.state.attempts[-self.memory_limit:]],
        }

    def save(self, path: str | Path) -> Path:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self.state)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path, memory_limit: int = 5) -> "StageOrchestrator":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        payload["stages"] = {k: StageRecord(**v) for k, v in payload["stages"].items()}
        payload["attempts"] = [Attempt(**v) for v in payload.get("attempts", [])]
        return cls(ProjectState(**payload), memory_limit=memory_limit)

    def _get_attempt(self, attempt_id: str) -> Attempt:
        for attempt in self.state.attempts:
            if attempt.attempt_id == attempt_id:
                return attempt
        raise StageError(f"Unknown attempt_id: {attempt_id}")

    def _touch(self) -> None:
        self.state.updated_at = now_iso()


if __name__ == "__main__":
    orchestrator = StageOrchestrator.create("demo", "Create an editable stylized mascot")
    print(json.dumps(orchestrator.memory_window(), ensure_ascii=False, indent=2))

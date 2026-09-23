#!/usr/bin/env python3
"""Reference preprocessing and silhouette QA for Blender shape reconstruction.

Run outside Blender in a normal Python virtual environment. The script never
modifies Blender files. It creates deterministic masks, contour JSON, overlays,
and metric reports that the Blender agent can consume.

Commands:
    extract   binary mask -> contour JSON while preserving holes
    compare   reference mask vs Blender silhouette render
    info      inspect a mask before using it

The default behavior is intentionally conservative. It does not pretend that a
small RGB image contains true depth and it does not silently segment by color.
Provide a clean mask or an image with alpha whenever possible.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import numpy as np


class ReferenceToolError(RuntimeError):
    """Raised for invalid inputs rather than producing a misleading result."""


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_image(path: str | Path) -> np.ndarray:
    source = Path(path)
    if not source.is_file():
        raise ReferenceToolError(f"File not found: {source}")
    image = cv2.imdecode(np.fromfile(str(source), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ReferenceToolError(f"OpenCV could not read: {source}")
    return image


def load_mask(
    path: str | Path,
    *,
    threshold: int = 127,
    invert: bool = False,
    prefer_alpha: bool = True,
) -> tuple[np.ndarray, dict]:
    """Load an image as a uint8 mask containing only 0 and 255.

    Alpha is used only when it contains actual transparency. Otherwise the image
    is converted to grayscale and thresholded. Automatic foreground guessing is
    deliberately avoided; use ``invert=True`` when the object is dark.
    """
    image = _read_image(path)
    channel_name = "grayscale"

    if image.ndim == 2:
        channel = image
    elif image.ndim == 3 and image.shape[2] == 4:
        alpha = image[:, :, 3]
        has_transparency = int(alpha.min()) < 250
        if prefer_alpha and has_transparency:
            channel = alpha
            channel_name = "alpha"
        else:
            channel = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)
    elif image.ndim == 3 and image.shape[2] >= 3:
        channel = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)
    else:
        raise ReferenceToolError(f"Unsupported image shape: {image.shape}")

    threshold = int(np.clip(threshold, 0, 255))
    mask = np.where(channel >= threshold, 255, 0).astype(np.uint8)
    if invert:
        mask = cv2.bitwise_not(mask)

    foreground = int(np.count_nonzero(mask))
    if foreground == 0:
        raise ReferenceToolError("Mask is empty. Check threshold/invert/alpha.")
    if foreground == mask.size:
        raise ReferenceToolError("Mask is completely filled. Check threshold/invert/alpha.")

    metadata = {
        "source": str(Path(path).resolve()),
        "width": int(mask.shape[1]),
        "height": int(mask.shape[0]),
        "channel": channel_name,
        "threshold": threshold,
        "invert": bool(invert),
        "foreground_pixels": foreground,
        "foreground_ratio": foreground / float(mask.size),
    }
    return mask, metadata


def _ellipse_kernel(radius: int) -> np.ndarray:
    radius = max(0, int(radius))
    size = radius * 2 + 1
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))


def clean_mask(
    mask: np.ndarray,
    *,
    close_radius: int = 0,
    open_radius: int = 0,
    min_component_area: int = 0,
) -> np.ndarray:
    cleaned = mask.copy()
    if close_radius > 0:
        cleaned = cv2.morphologyEx(
            cleaned, cv2.MORPH_CLOSE, _ellipse_kernel(close_radius)
        )
    if open_radius > 0:
        cleaned = cv2.morphologyEx(
            cleaned, cv2.MORPH_OPEN, _ellipse_kernel(open_radius)
        )

    min_component_area = max(0, int(min_component_area))
    if min_component_area > 0:
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            (cleaned > 0).astype(np.uint8), connectivity=8
        )
        filtered = np.zeros_like(cleaned)
        for index in range(1, count):
            if int(stats[index, cv2.CC_STAT_AREA]) >= min_component_area:
                filtered[labels == index] = 255
        cleaned = filtered

    if not np.any(cleaned):
        raise ReferenceToolError("Mask cleanup removed all foreground pixels.")
    return cleaned


def binary_iou(a: np.ndarray, b: np.ndarray) -> float:
    aa = a > 0
    bb = b > 0
    union = int(np.count_nonzero(aa | bb))
    if union == 0:
        return 1.0
    return int(np.count_nonzero(aa & bb)) / float(union)


def _contour_depths(hierarchy: np.ndarray) -> list[int]:
    depths: list[int] = []
    for index in range(len(hierarchy)):
        depth = 0
        parent = int(hierarchy[index][3])
        guard = 0
        while parent >= 0:
            depth += 1
            parent = int(hierarchy[parent][3])
            guard += 1
            if guard > len(hierarchy):
                raise ReferenceToolError("Invalid cyclic contour hierarchy.")
        depths.append(depth)
    return depths


def _signed_area(points: Sequence[Sequence[float]]) -> float:
    area = 0.0
    for index, point in enumerate(points):
        nxt = points[(index + 1) % len(points)]
        area += float(point[0]) * float(nxt[1]) - float(nxt[0]) * float(point[1])
    return area * 0.5


def _deduplicate_closed(points: np.ndarray) -> np.ndarray:
    if len(points) <= 1:
        return points
    kept = [points[0]]
    for point in points[1:]:
        if not np.array_equal(point, kept[-1]):
            kept.append(point)
    result = np.asarray(kept, dtype=np.float64)
    if len(result) > 2 and np.array_equal(result[0], result[-1]):
        result = result[:-1]
    return result


def _approximate_contours(
    contours: Sequence[np.ndarray], epsilon_ratio: float
) -> list[np.ndarray]:
    approximated: list[np.ndarray] = []
    for contour in contours:
        perimeter = max(float(cv2.arcLength(contour, True)), 1.0)
        epsilon = max(0.0, float(epsilon_ratio)) * perimeter
        candidate = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
        candidate = _deduplicate_closed(candidate)
        if len(candidate) < 3:
            candidate = _deduplicate_closed(contour.reshape(-1, 2))
        approximated.append(candidate.astype(np.float64))
    return approximated


def _reconstruct_from_contours(
    shape: tuple[int, int], contours: Sequence[np.ndarray], depths: Sequence[int]
) -> np.ndarray:
    canvas = np.zeros(shape, dtype=np.uint8)
    ordered = sorted(range(len(contours)), key=lambda index: depths[index])
    for index in ordered:
        contour = np.rint(contours[index]).astype(np.int32).reshape(-1, 1, 2)
        color = 255 if depths[index] % 2 == 0 else 0
        cv2.drawContours(canvas, [contour], -1, int(color), thickness=cv2.FILLED)
    return canvas


def extract_contours(
    mask: np.ndarray,
    *,
    epsilon_ratio: float = 0.002,
    minimum_reconstruction_iou: float = 0.985,
) -> tuple[list[np.ndarray], np.ndarray, list[int], float, float]:
    contours, hierarchy_raw = cv2.findContours(
        mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
    )
    if not contours or hierarchy_raw is None:
        raise ReferenceToolError("No contours found in mask.")
    hierarchy = hierarchy_raw[0].astype(np.int32)
    depths = _contour_depths(hierarchy)

    requested = max(0.0, float(epsilon_ratio))
    candidates = []
    current = requested
    for _ in range(8):
        candidates.append(current)
        current *= 0.5
    candidates.append(0.0)

    minimum_reconstruction_iou = float(
        np.clip(minimum_reconstruction_iou, 0.0, 1.0)
    )
    best: tuple[list[np.ndarray], float, float] | None = None
    for ratio in candidates:
        simplified = _approximate_contours(contours, ratio)
        reconstructed = _reconstruct_from_contours(mask.shape, simplified, depths)
        score = binary_iou(mask, reconstructed)
        best = (simplified, score, ratio)
        if score >= minimum_reconstruction_iou:
            break

    assert best is not None
    return best[0], hierarchy, depths, best[1], best[2]


def _bbox(mask: np.ndarray) -> Box:
    ys, xs = np.nonzero(mask > 0)
    if len(xs) == 0:
        raise ReferenceToolError("Cannot compute bounding box of empty mask.")
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    return Box(x0, y0, x1 - x0 + 1, y1 - y0 + 1)


def _centroid(mask: np.ndarray) -> tuple[float, float]:
    moments = cv2.moments((mask > 0).astype(np.uint8), binaryImage=True)
    if moments["m00"] == 0:
        raise ReferenceToolError("Cannot compute centroid of empty mask.")
    return (
        float(moments["m10"] / moments["m00"]),
        float(moments["m01"] / moments["m00"]),
    )


def _hole_count(mask: np.ndarray) -> int:
    _, hierarchy_raw = cv2.findContours(
        mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    if hierarchy_raw is None:
        return 0
    hierarchy = hierarchy_raw[0]
    return sum(depth % 2 for depth in _contour_depths(hierarchy))


def _world_points(points_px: np.ndarray, width: int, height: int) -> list[list[float]]:
    result: list[list[float]] = []
    for x, y in points_px:
        result.append(
            [
                (float(x) - width / 2.0) / float(height),
                (height / 2.0 - float(y)) / float(height),
            ]
        )
    return result


def contour_document(
    mask: np.ndarray,
    source_metadata: dict,
    *,
    epsilon_ratio: float,
    minimum_reconstruction_iou: float,
) -> tuple[dict, np.ndarray]:
    contours, hierarchy, depths, reconstruction_iou, used_ratio = extract_contours(
        mask,
        epsilon_ratio=epsilon_ratio,
        minimum_reconstruction_iou=minimum_reconstruction_iou,
    )
    height, width = mask.shape
    loops: list[dict] = []
    for index, points in enumerate(contours):
        world = _world_points(points, width, height)
        is_hole = bool(depths[index] % 2)
        area = _signed_area(world)

        # Blender 2D curves use winding for holes. Keep outer loops CCW and holes CW
        # in the y-up coordinate system used by this document.
        wants_positive = not is_hole
        if (area > 0) != wants_positive:
            points = points[::-1].copy()
            world = list(reversed(world))
            area = -area

        loops.append(
            {
                "index": index,
                "parent": int(hierarchy[index][3]),
                "first_child": int(hierarchy[index][2]),
                "next": int(hierarchy[index][0]),
                "previous": int(hierarchy[index][1]),
                "depth": int(depths[index]),
                "is_hole": is_hole,
                "point_count": int(len(points)),
                "source_area_px": float(abs(cv2.contourArea(points.astype(np.float32)))),
                "signed_area_world": float(area),
                "winding_world": "CCW" if area > 0 else "CW",
                "points_px": [[float(x), float(y)] for x, y in points],
                "points_world": world,
            }
        )

    reconstructed = _reconstruct_from_contours(mask.shape, contours, depths)
    document = {
        "schema": "ai-blender-contours/v1",
        "created_utc": _utc_now(),
        "source": source_metadata,
        "coordinate_system": {
            "normalization": "height_unit_centered_y_up",
            "world_height": 1.0,
            "world_width": width / float(height),
            "blender_mapping": "points_world[x,y] -> local curve [X,Y,0], then rotate +90deg around X to face camera on -Y",
        },
        "extraction": {
            "requested_epsilon_ratio": float(epsilon_ratio),
            "used_epsilon_ratio": float(used_ratio),
            "minimum_reconstruction_iou": float(minimum_reconstruction_iou),
            "reconstruction_iou": float(reconstruction_iou),
            "loop_count": len(loops),
            "hole_count": sum(1 for loop in loops if loop["is_hole"]),
            "foreground_bbox_px": asdict(_bbox(mask)),
        },
        "loops": loops,
    }
    return document, reconstructed


def _resize_like(mask: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    if mask.shape == shape:
        return mask
    return cv2.resize(mask, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)


def align_mask_bbox(
    moving: np.ndarray, fixed: np.ndarray, *, uniform: bool
) -> tuple[np.ndarray, np.ndarray]:
    moving_box = _bbox(moving)
    fixed_box = _bbox(fixed)
    sx = fixed_box.width / max(1.0, float(moving_box.width))
    sy = fixed_box.height / max(1.0, float(moving_box.height))
    if uniform:
        scale = min(sx, sy)
        sx = sy = scale

    moving_center = moving_box.center
    fixed_center = fixed_box.center
    matrix = np.array(
        [
            [sx, 0.0, fixed_center[0] - sx * moving_center[0]],
            [0.0, sy, fixed_center[1] - sy * moving_center[1]],
        ],
        dtype=np.float32,
    )
    aligned = cv2.warpAffine(
        moving,
        matrix,
        (fixed.shape[1], fixed.shape[0]),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    return aligned, matrix


def _edge(mask: np.ndarray) -> np.ndarray:
    return cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, _ellipse_kernel(1)) > 0


def _distance_to_edges(edge: np.ndarray) -> np.ndarray:
    # distanceTransform returns distance to the nearest zero. Invert so edge pixels
    # are zero and every other pixel gets its distance to the nearest edge.
    inverse = np.where(edge, 0, 1).astype(np.uint8)
    return cv2.distanceTransform(inverse, cv2.DIST_L2, 3)


def boundary_metrics(
    reference: np.ndarray, candidate: np.ndarray, *, tolerance_px: float
) -> dict:
    ref_edge = _edge(reference)
    cand_edge = _edge(candidate)
    ref_count = int(np.count_nonzero(ref_edge))
    cand_count = int(np.count_nonzero(cand_edge))
    if ref_count == 0 or cand_count == 0:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "symmetric_chamfer_px": float("inf"),
            "symmetric_chamfer_normalized": float("inf"),
        }

    dist_to_ref = _distance_to_edges(ref_edge)
    dist_to_cand = _distance_to_edges(cand_edge)
    cand_distances = dist_to_ref[cand_edge]
    ref_distances = dist_to_cand[ref_edge]

    tolerance_px = max(0.0, float(tolerance_px))
    precision = float(np.mean(cand_distances <= tolerance_px))
    recall = float(np.mean(ref_distances <= tolerance_px))
    f1 = 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)
    chamfer_px = float((cand_distances.mean() + ref_distances.mean()) * 0.5)
    diagonal = math.hypot(reference.shape[1], reference.shape[0])
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "symmetric_chamfer_px": chamfer_px,
        "symmetric_chamfer_normalized": chamfer_px / max(diagonal, 1.0),
    }


def compare_masks(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    alignment: str = "none",
    tolerance_px: float = 3.0,
    world_height: float = 1.0,
    gate_iou: float = 0.85,
    gate_boundary_f1: float = 0.90,
) -> tuple[dict, np.ndarray, np.ndarray]:
    candidate = _resize_like(candidate, reference.shape)
    transform = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
    if alignment == "bbox-uniform":
        candidate, transform = align_mask_bbox(candidate, reference, uniform=True)
    elif alignment == "bbox-nonuniform":
        candidate, transform = align_mask_bbox(candidate, reference, uniform=False)
    elif alignment != "none":
        raise ReferenceToolError(f"Unknown alignment mode: {alignment}")

    ref = reference > 0
    cand = candidate > 0
    intersection = int(np.count_nonzero(ref & cand))
    union = int(np.count_nonzero(ref | cand))
    ref_area = int(np.count_nonzero(ref))
    cand_area = int(np.count_nonzero(cand))
    iou = intersection / float(union) if union else 1.0
    dice = 2.0 * intersection / float(ref_area + cand_area) if ref_area + cand_area else 1.0

    ref_box = _bbox(reference)
    cand_box = _bbox(candidate)
    ref_centroid = _centroid(reference)
    cand_centroid = _centroid(candidate)
    height, width = reference.shape
    dx_px = ref_centroid[0] - cand_centroid[0]
    dy_px = ref_centroid[1] - cand_centroid[1]
    boundary = boundary_metrics(reference, candidate, tolerance_px=tolerance_px)

    ref_holes = _hole_count(reference)
    cand_holes = _hole_count(candidate)
    scale_x = ref_box.width / max(float(cand_box.width), 1.0)
    scale_z = ref_box.height / max(float(cand_box.height), 1.0)

    suggestions: list[str] = []
    if abs(dx_px) > 1.0 or abs(dy_px) > 1.0:
        suggestions.append(
            f"Translate screen-space group by dx={dx_px:.2f}px, dy={dy_px:.2f}px before changing local shape."
        )
    if abs(scale_x - 1.0) > 0.02 or abs(scale_z - 1.0) > 0.02:
        suggestions.append(
            f"Check camera/object scale first: suggested screen scale X={scale_x:.4f}, Z={scale_z:.4f}."
        )
    if ref_holes != cand_holes:
        suggestions.append(
            f"Negative-space mismatch: reference holes={ref_holes}, render holes={cand_holes}. Do not smooth/remesh further until fixed."
        )
    if iou < gate_iou and boundary["f1"] >= gate_boundary_f1:
        suggestions.append("Edges are locally close but filled area differs; inspect layer order, thickness, or missing components.")
    if boundary["f1"] < gate_boundary_f1:
        suggestions.append("Boundary mismatch remains; adjust silhouette landmarks instead of material or lighting.")

    report = {
        "schema": "ai-blender-silhouette-report/v1",
        "created_utc": _utc_now(),
        "resolution": [int(width), int(height)],
        "alignment": {
            "mode": alignment,
            "candidate_to_reference_affine_px": transform.tolist(),
        },
        "metrics": {
            "mask_iou": float(iou),
            "dice": float(dice),
            "boundary": boundary,
            "reference_area_px": ref_area,
            "candidate_area_px": cand_area,
            "area_ratio_candidate_over_reference": cand_area / max(float(ref_area), 1.0),
            "reference_holes": ref_holes,
            "candidate_holes": cand_holes,
            "centroid_distance_normalized": math.hypot(dx_px, dy_px) / max(math.hypot(width, height), 1.0),
        },
        "screen_space": {
            "reference_bbox_px": asdict(ref_box),
            "candidate_bbox_px": asdict(cand_box),
            "reference_centroid_px": list(ref_centroid),
            "candidate_centroid_px": list(cand_centroid),
            "delta_candidate_to_reference_px": [dx_px, dy_px],
            "suggested_scale_x": scale_x,
            "suggested_scale_z": scale_z,
        },
        "blender_world_suggestion": {
            "assumed_orthographic_world_height": float(world_height),
            "translate_x": dx_px / float(height) * float(world_height),
            "translate_z": -dy_px / float(height) * float(world_height),
            "scale_x": scale_x,
            "scale_z": scale_z,
            "note": "Apply only to the common blockout/root after camera resolution and ortho_scale match the reference.",
        },
        "quality_gate": {
            "mask_iou_min": float(gate_iou),
            "boundary_f1_min": float(gate_boundary_f1),
            "pass": bool(iou >= gate_iou and boundary["f1"] >= gate_boundary_f1 and ref_holes == cand_holes),
        },
        "suggestions": suggestions,
    }

    overlay = np.zeros((height, width, 3), dtype=np.uint8)
    overlap = ref & cand
    reference_only = ref & ~cand
    candidate_only = cand & ~ref
    overlay[reference_only] = (60, 200, 60)   # BGR: green
    overlay[candidate_only] = (200, 60, 200)  # BGR: magenta
    overlay[overlap] = (240, 240, 240)

    difference = np.zeros((height, width, 3), dtype=np.uint8)
    difference[reference_only] = (0, 0, 255)   # missing in candidate
    difference[candidate_only] = (255, 0, 0)   # extra in candidate
    difference[overlap] = (80, 80, 80)
    return report, overlay, difference


def save_json(path: str | Path, payload: dict) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def save_image(path: str | Path, image: np.ndarray) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(destination.suffix or ".png", image)
    if not ok:
        raise ReferenceToolError(f"Could not encode image: {destination}")
    encoded.tofile(str(destination))


def command_extract(args: argparse.Namespace) -> None:
    mask, metadata = load_mask(
        args.input,
        threshold=args.threshold,
        invert=args.invert,
        prefer_alpha=not args.ignore_alpha,
    )
    mask = clean_mask(
        mask,
        close_radius=args.close_radius,
        open_radius=args.open_radius,
        min_component_area=args.min_component_area,
    )
    document, reconstructed = contour_document(
        mask,
        metadata,
        epsilon_ratio=args.epsilon_ratio,
        minimum_reconstruction_iou=args.minimum_reconstruction_iou,
    )
    save_json(args.output_json, document)
    if args.output_mask:
        save_image(args.output_mask, mask)
    if args.output_reconstructed:
        save_image(args.output_reconstructed, reconstructed)
    print(json.dumps(document["extraction"], ensure_ascii=False, indent=2))


def command_compare(args: argparse.Namespace) -> None:
    reference, ref_meta = load_mask(
        args.reference,
        threshold=args.reference_threshold,
        invert=args.reference_invert,
        prefer_alpha=not args.reference_ignore_alpha,
    )
    candidate, cand_meta = load_mask(
        args.candidate,
        threshold=args.candidate_threshold,
        invert=args.candidate_invert,
        prefer_alpha=not args.candidate_ignore_alpha,
    )
    report, overlay, difference = compare_masks(
        reference,
        candidate,
        alignment=args.alignment,
        tolerance_px=args.tolerance_px,
        world_height=args.world_height,
        gate_iou=args.gate_iou,
        gate_boundary_f1=args.gate_boundary_f1,
    )
    report["inputs"] = {"reference": ref_meta, "candidate": cand_meta}
    save_json(args.output_json, report)
    if args.overlay:
        save_image(args.overlay, overlay)
    if args.difference:
        save_image(args.difference, difference)
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))


def command_info(args: argparse.Namespace) -> None:
    mask, metadata = load_mask(
        args.input,
        threshold=args.threshold,
        invert=args.invert,
        prefer_alpha=not args.ignore_alpha,
    )
    metadata.update(
        {
            "bbox_px": asdict(_bbox(mask)),
            "centroid_px": list(_centroid(mask)),
            "holes": _hole_count(mask),
        }
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conservative contour extraction and silhouette comparison for Blender."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="Extract hole-preserving contour JSON.")
    extract.add_argument("input")
    extract.add_argument("output_json")
    extract.add_argument("--threshold", type=int, default=127)
    extract.add_argument("--invert", action="store_true")
    extract.add_argument("--ignore-alpha", action="store_true")
    extract.add_argument("--close-radius", type=int, default=0)
    extract.add_argument("--open-radius", type=int, default=0)
    extract.add_argument("--min-component-area", type=int, default=0)
    extract.add_argument("--epsilon-ratio", type=float, default=0.002)
    extract.add_argument("--minimum-reconstruction-iou", type=float, default=0.985)
    extract.add_argument("--output-mask")
    extract.add_argument("--output-reconstructed")
    extract.set_defaults(func=command_extract)

    compare = subparsers.add_parser("compare", help="Compare reference and Blender masks.")
    compare.add_argument("reference")
    compare.add_argument("candidate")
    compare.add_argument("output_json")
    compare.add_argument(
        "--alignment",
        choices=("none", "bbox-uniform", "bbox-nonuniform"),
        default="none",
    )
    compare.add_argument("--reference-threshold", type=int, default=127)
    compare.add_argument("--candidate-threshold", type=int, default=127)
    compare.add_argument("--reference-invert", action="store_true")
    compare.add_argument("--candidate-invert", action="store_true")
    compare.add_argument("--reference-ignore-alpha", action="store_true")
    compare.add_argument("--candidate-ignore-alpha", action="store_true")
    compare.add_argument("--tolerance-px", type=float, default=3.0)
    compare.add_argument("--world-height", type=float, default=1.0)
    compare.add_argument("--gate-iou", type=float, default=0.85)
    compare.add_argument("--gate-boundary-f1", type=float, default=0.90)
    compare.add_argument("--overlay")
    compare.add_argument("--difference")
    compare.set_defaults(func=command_compare)

    info = subparsers.add_parser("info", help="Inspect mask foreground, box, and holes.")
    info.add_argument("input")
    info.add_argument("--threshold", type=int, default=127)
    info.add_argument("--invert", action="store_true")
    info.add_argument("--ignore-alpha", action="store_true")
    info.set_defaults(func=command_info)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ReferenceToolError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .common import read_json, read_jsonl, sha256_bytes, sha256_file


FINAL_MARKER = "FINAL_CANDIDATE_JSON:"
SCORE_RULE = "einstein_arena_official_verifier_v1"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_vector_array(
    value: Any,
    *,
    rows: int | None = None,
    min_rows: int | None = None,
    max_rows: int | None = None,
    columns: int,
    allow_strings: bool = False,
) -> str | None:
    if not isinstance(value, list):
        return "must_be_array"
    if rows is not None and len(value) != rows:
        return f"expected_{rows}_rows_got_{len(value)}"
    if min_rows is not None and len(value) < min_rows:
        return f"expected_at_least_{min_rows}_rows_got_{len(value)}"
    if max_rows is not None and len(value) > max_rows:
        return f"expected_at_most_{max_rows}_rows_got_{len(value)}"
    for row_index, row in enumerate(value):
        if not isinstance(row, list) or len(row) != columns:
            return f"row_{row_index}_expected_{columns}_columns"
        for column_index, item in enumerate(row):
            if not _is_number(item) and not (allow_strings and isinstance(item, str)):
                return f"row_{row_index}_column_{column_index}_not_number"
    return None


def _validate_number_array(
    value: Any,
    *,
    min_items: int,
    max_items: int,
) -> str | None:
    if not isinstance(value, list):
        return "must_be_array"
    if not min_items <= len(value) <= max_items:
        return f"expected_{min_items}_to_{max_items}_items_got_{len(value)}"
    for index, item in enumerate(value):
        if not _is_number(item):
            return f"item_{index}_not_number"
    return None


def candidate_schema_error(slug: str, candidate: dict[str, Any]) -> str | None:
    """Mirror the current website shape checks before running Python verifiers."""

    if slug == "circle-packing":
        return _validate_vector_array(candidate.get("circles"), rows=26, columns=3)
    if slug == "circles-rectangle":
        return _validate_vector_array(candidate.get("circles"), rows=21, columns=3)
    if slug == "difference-bases":
        values = candidate.get("set")
        if not isinstance(values, list):
            return "set:must_be_array"
        if len(values) > 2000:
            return f"set:expected_at_most_2000_items_got_{len(values)}"
        for index, item in enumerate(values):
            if not isinstance(item, int) or isinstance(item, bool) or item < 0:
                return f"set:item_{index}_not_nonnegative_integer"
        return None
    if slug == "edges-vs-triangles":
        error = _validate_vector_array(
            candidate.get("weights"), min_rows=1, max_rows=500, columns=20
        )
        return f"weights:{error}" if error else None
    if slug in {
        "erdos-min-overlap",
        "first-autocorrelation-inequality",
        "third-autocorrelation-inequality",
    }:
        error = _validate_number_array(
            candidate.get("values"), min_items=1, max_items=100_000
        )
        return f"values:{error}" if error else None
    if slug == "second-autocorrelation-inequality":
        error = _validate_number_array(
            candidate.get("values"), min_items=1, max_items=2_000_000
        )
        return f"values:{error}" if error else None
    if slug == "flat-polynomials":
        values = candidate.get("coefficients")
        if not isinstance(values, list) or len(values) != 70:
            length = len(values) if isinstance(values, list) else "non_array"
            return f"coefficients:expected_70_items_got_{length}"
        for index, item in enumerate(values):
            if not isinstance(item, int) or isinstance(item, bool):
                return f"coefficients:item_{index}_not_integer"
        return None
    vector_contracts: dict[str, tuple[str, int, int, bool]] = {
        "heilbronn-triangles": ("points", 11, 2, False),
        "kissing-number-d11-605": ("vectors", 605, 11, True),
        "kissing-number-d12-842": ("vectors", 842, 12, True),
        "min-distance-ratio-2d": ("vectors", 16, 2, False),
        "tammes-problem": ("vectors", 50, 3, False),
        "thomson-problem": ("vectors", 282, 3, False),
    }
    if slug in vector_contracts:
        key, rows, columns, allow_strings = vector_contracts[slug]
        error = _validate_vector_array(
            candidate.get(key),
            rows=rows,
            columns=columns,
            allow_strings=allow_strings,
        )
        return f"{key}:{error}" if error else None
    if slug == "prime-number-theorem":
        value = candidate.get("partial_function")
        if not isinstance(value, dict):
            return "partial_function:must_be_object"
        if len(value) > 2000:
            return f"partial_function:expected_at_most_2000_keys_got_{len(value)}"
        for key, item in value.items():
            if not isinstance(key, str):
                return "partial_function:key_not_string"
            if not _is_number(item):
                return f"partial_function:{key}_not_number"
        return None
    if slug == "uncertainty-principle":
        values = candidate.get("laguerre_double_roots")
        error = _validate_number_array(values, min_items=1, max_items=25)
        if error:
            return f"laguerre_double_roots:{error}"
        assert isinstance(values, list)
        for index, item in enumerate(values):
            if float(item) <= 0 or float(item) > 300:
                return f"laguerre_double_roots:item_{index}_outside_(0,300]"
        return None
    return None


def extract_candidate(
    output: str,
    *,
    marker: str = FINAL_MARKER,
) -> tuple[dict[str, Any] | None, str]:
    marker_index = output.rfind(marker)
    if marker_index < 0:
        return None, "marker_not_found"
    payload = output[marker_index + len(marker) :].strip()
    if not payload:
        return None, "empty_payload"
    status = "ok"
    if payload.startswith("```"):
        opening, separator, fenced_payload = payload.partition("\n")
        if not separator or opening.lower() not in {"```", "```json"}:
            return None, "invalid_json_fence"
        if not fenced_payload.endswith("```"):
            return None, "unterminated_json_fence"
        payload = fenced_payload[:-3].strip()
        status = "ok_json_fence"

    def reject_non_finite(value: str) -> None:
        raise ValueError(f"non_finite_json_constant:{value}")

    decoder = json.JSONDecoder(parse_constant=reject_non_finite)
    try:
        value, end = decoder.raw_decode(payload)
    except json.JSONDecodeError as exc:
        return None, f"invalid_json:{exc.msg}@{exc.pos}"
    except ValueError as exc:
        return None, str(exc)
    if payload[end:].strip():
        return None, "trailing_text_after_json"
    if not isinstance(value, dict):
        return None, "candidate_is_not_object"
    return value, status


class OpenArenaEvaluator:
    def __init__(
        self,
        data_dir: Path,
        *,
        timeout_seconds: float = 120,
        memory_gb: float = 8,
        max_candidate_bytes: int = 32 * 1024 * 1024,
    ):
        self.data_dir = data_dir.resolve()
        self.timeout_seconds = timeout_seconds
        self.memory_gb = memory_gb
        self.max_candidate_bytes = max_candidate_bytes
        self.rows = read_jsonl(self.data_dir / "openarena.jsonl")
        self.by_slug: dict[str, dict[str, Any]] = {}
        for row in self.rows:
            metadata = row.get("metadata")
            if not isinstance(metadata, dict) or not metadata.get("slug"):
                raise ValueError("Dataset row has no metadata.slug")
            slug = str(metadata["slug"])
            if slug in self.by_slug:
                raise ValueError(f"Duplicate dataset slug: {slug}")
            self.by_slug[slug] = row

    def list_problems(self) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for row in self.rows:
            metadata = row["metadata"]
            result.append(
                {
                    "slug": str(metadata["slug"]),
                    "scoring": str(metadata.get("scoring") or ""),
                    "title": str(metadata.get("title") or ""),
                }
            )
        return result

    def item(self, slug: str) -> dict[str, Any]:
        try:
            return self.by_slug[slug]
        except KeyError as exc:
            valid = ", ".join(self.by_slug)
            raise ValueError(f"Unknown slug {slug!r}; available: {valid}") from exc

    def verifier_path(self, slug: str) -> Path:
        item = self.item(slug)
        metadata = item["metadata"]
        relative = str(
            metadata.get("verifier_path")
            or f"problems/{slug}/code/verifier.py"
        )
        path = (self.data_dir / relative).resolve()
        if self.data_dir not in path.parents:
            raise ValueError(f"Verifier path escapes data directory: {relative}")
        return path

    def validate(self) -> dict[str, Any]:
        errors: list[str] = []
        manifest_path = self.data_dir / "manifest.json"
        snapshot_manifest_path = self.data_dir / "official_snapshot" / "manifest.json"
        try:
            manifest = read_json(manifest_path)
        except (OSError, json.JSONDecodeError) as exc:
            manifest = {}
            errors.append(f"invalid dataset manifest: {exc}")
        try:
            snapshot_manifest = read_json(snapshot_manifest_path)
        except (OSError, json.JSONDecodeError) as exc:
            snapshot_manifest = {}
            errors.append(f"invalid official snapshot manifest: {exc}")
        selected = manifest.get("open_problem_slugs", [])
        if selected != list(self.by_slug):
            errors.append("manifest slugs and openarena.jsonl order differ")
        snapshot_slugs = snapshot_manifest.get("problem_slugs", [])
        if snapshot_slugs != list(self.by_slug):
            errors.append("official snapshot slugs and openarena.jsonl order differ")
        snapshot_hashes = snapshot_manifest.get("verifier_hashes", {})
        for slug, row in self.by_slug.items():
            metadata = row["metadata"]
            verifier = self.verifier_path(slug)
            snapshot_path = (
                self.data_dir / "official_snapshot" / "problems" / f"{slug}.json"
            )
            if not verifier.is_file():
                errors.append(f"{slug}: verifier not found")
                continue
            if not snapshot_path.is_file():
                errors.append(f"{slug}: official snapshot not found")
                continue
            snapshot = read_json(snapshot_path)
            source = snapshot.get("verifier")
            if not isinstance(source, str):
                errors.append(f"{slug}: snapshot verifier is invalid")
                continue
            digest = sha256_bytes(source.encode("utf-8"))
            checks = {
                "snapshot problem": snapshot.get("verifier_sha256"),
                "snapshot manifest": snapshot_hashes.get(slug),
                "dataset metadata": metadata.get("verifier_sha256"),
                "localized verifier": sha256_file(verifier),
            }
            for label, actual in checks.items():
                if actual != digest:
                    errors.append(f"{slug}: {label} hash mismatch")
        return {
            "dataset": "openarena",
            "data_dir": str(self.data_dir),
            "snapshot_id": snapshot_manifest.get("snapshot_id"),
            "problems": len(self.by_slug),
            "valid": not errors,
            "errors": errors,
        }

    def _run_verifier(
        self,
        slug: str,
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            encoded = json.dumps(
                candidate, ensure_ascii=False, allow_nan=False
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            return {
                "ok": False,
                "score": None,
                "reason": f"candidate_not_strict_json:{exc}",
                "seconds": 0.0,
            }
        if len(encoded) > self.max_candidate_bytes:
            return {
                "ok": False,
                "score": None,
                "reason": f"candidate_too_large:{len(encoded)}>{self.max_candidate_bytes}",
                "seconds": 0.0,
            }
        started = time.monotonic()
        environment = dict(os.environ)
        environment.setdefault("OPENBLAS_NUM_THREADS", "1")
        environment.setdefault("OMP_NUM_THREADS", "1")
        environment.setdefault("MKL_NUM_THREADS", "1")
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "openarena_eval.verifier_worker",
                    "--verifier",
                    str(self.verifier_path(slug)),
                    "--memory-gb",
                    str(self.memory_gb),
                    "--cpu-seconds",
                    str(max(1, math.ceil(self.timeout_seconds))),
                ],
                input=encoded,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout_seconds,
                check=False,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "score": None,
                "reason": f"verifier_timeout:{self.timeout_seconds}s",
                "seconds": time.monotonic() - started,
            }
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="replace")[-2000:]
            return {
                "ok": False,
                "score": None,
                "reason": f"worker_exit_{completed.returncode}:{stderr}",
                "seconds": time.monotonic() - started,
            }
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            stdout = completed.stdout.decode("utf-8", errors="replace")[-2000:]
            return {
                "ok": False,
                "score": None,
                "reason": f"invalid_worker_output:{stdout}",
                "seconds": time.monotonic() - started,
            }
        result.setdefault("seconds", time.monotonic() - started)
        return result

    def score_candidate(
        self,
        slug: str,
        candidate: dict[str, Any],
        *,
        candidate_id: str | None = None,
        extract_status: str = "direct_json",
    ) -> dict[str, Any]:
        item = self.item(slug)
        metadata = item["metadata"]
        scoring = str(metadata.get("scoring") or "")
        base = {
            "dataset": "openarena",
            "score_rule": SCORE_RULE,
            "slug": slug,
            "candidate_id": candidate_id,
            "scoring": scoring,
            "snapshot_id": metadata.get("verifier_snapshot_id"),
            "verifier_sha256": metadata.get("verifier_sha256"),
            "extract_status": extract_status,
            "candidate": candidate,
        }
        error = candidate_schema_error(slug, candidate)
        if error:
            return {
                **base,
                "valid": False,
                "raw_score": None,
                "directional_score": None,
                "reason": f"schema_error:{error}",
                "verifier_seconds": 0.0,
            }
        verifier_result = self._run_verifier(slug, candidate)
        score = verifier_result.get("score")
        valid = verifier_result.get("ok") is True and _is_number(score)
        directional = None
        if valid:
            directional = float(score) if scoring == "maximize" else -float(score)
        return {
            **base,
            "valid": valid,
            "raw_score": float(score) if valid else None,
            "directional_score": directional,
            "reason": str(verifier_result.get("reason") or "verifier_failed"),
            "verifier_seconds": float(verifier_result.get("seconds") or 0.0),
            "verifier_traceback": verifier_result.get("traceback"),
        }

    def score_model_output(
        self,
        slug: str,
        output: str,
        *,
        candidate_id: str | None = None,
    ) -> dict[str, Any]:
        candidate, status = extract_candidate(output)
        if candidate is None:
            item = self.item(slug)
            metadata = item["metadata"]
            return {
                "dataset": "openarena",
                "score_rule": SCORE_RULE,
                "slug": slug,
                "candidate_id": candidate_id,
                "scoring": metadata.get("scoring"),
                "snapshot_id": metadata.get("verifier_snapshot_id"),
                "verifier_sha256": metadata.get("verifier_sha256"),
                "extract_status": status,
                "candidate": None,
                "valid": False,
                "raw_score": None,
                "directional_score": None,
                "reason": status,
                "verifier_seconds": 0.0,
            }
        return self.score_candidate(
            slug,
            candidate,
            candidate_id=candidate_id,
            extract_status=status,
        )


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_slug: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_slug[str(result.get("slug") or "")].append(result)
    per_problem: dict[str, Any] = {}
    for slug, rows in sorted(by_slug.items()):
        valid = [
            row
            for row in rows
            if row.get("valid") is True
            and _is_number(row.get("directional_score"))
        ]
        best = (
            max(valid, key=lambda row: float(row["directional_score"]))
            if valid
            else None
        )
        per_problem[slug] = {
            "candidates": len(rows),
            "valid_candidates": len(valid),
            "scoring": rows[0].get("scoring") if rows else None,
            "best_raw_score": best.get("raw_score") if best else None,
            "best_candidate_id": best.get("candidate_id") if best else None,
        }
    valid_count = sum(result.get("valid") is True for result in results)
    return {
        "dataset": "openarena",
        "candidates": len(results),
        "valid_candidates": valid_count,
        "valid_rate": valid_count / len(results) if results else 0.0,
        "problems": len(by_slug),
        "valid_at_k": sum(
            value["valid_candidates"] > 0 for value in per_problem.values()
        ),
        "per_problem": per_problem,
    }

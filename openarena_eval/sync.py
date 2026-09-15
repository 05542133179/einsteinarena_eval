from __future__ import annotations

import ast
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    read_json,
    read_jsonl,
    sha256_bytes,
    write_json_atomic,
    write_jsonl_atomic,
    write_text_atomic,
)


DEFAULT_BASE_URL = "https://einsteinarena.com"
FINAL_MARKER = "FINAL_CANDIDATE_JSON:"


class _RedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow HTTP 308 the same way as the other permanent redirects.

    Python 3.10's stock redirect handler implements 301/302/303/307 only.
    The official problem endpoint answers with a 308, so without this the
    refresh aborts with ``HTTP Error 308: Permanent Redirect``.
    """

    def http_error_308(self, req, fp, code, msg, headers):  # type: ignore[override]
        return self.http_error_301(req, fp, code, msg, headers)


_OPENER = urllib.request.build_opener(_RedirectHandler)
DEFAULT_EXCLUSIONS = {
    "erdos-142",
    "heilbronn-convex",
    "hexagon-packing",
    "kissing-number-d11",
    "kissing-number-d12",
    "kissing-number-d16",
    "lean-sum-test",
    "sum-difference-2",
}


def request_json(url: str, *, timeout: float, retries: int) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "openarena-eval-kit/0.1",
        },
    )
    last_error: BaseException | None = None
    for attempt in range(retries + 1):
        try:
            with _OPENER.open(request, timeout=timeout) as response:
                return json.load(response)
        except (
            OSError,
            urllib.error.URLError,
            json.JSONDecodeError,
        ) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 5))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}") from last_error


def _listing(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        payload = payload.get("problems")
    if not isinstance(payload, list):
        raise TypeError("Official /api/problems response must be an array")
    result: list[dict[str, Any]] = []
    for index, value in enumerate(payload):
        if not isinstance(value, dict):
            raise TypeError(f"Problem listing item {index} is not an object")
        slug = value.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError(f"Problem listing item {index} has no slug")
        result.append(value)
    return result


def _normalize_problem(
    slug: str,
    payload: Any,
    *,
    source_url: str,
    fetched_at: str,
    fallback_title: str | None = None,
    fallback_description: str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError(f"Official problem response must be an object: {slug}")
    if isinstance(payload.get("problem"), dict):
        payload = payload["problem"]
    payload = dict(payload)
    if not payload.get("title") and fallback_title:
        payload["title"] = fallback_title
    if not payload.get("description") and fallback_description:
        payload["description"] = fallback_description
    returned_slug = payload.get("slug")
    if returned_slug is not None and returned_slug != slug:
        raise ValueError(f"Official API returned {returned_slug!r} for {slug!r}")
    required_strings = ("title", "description", "verifier")
    for key in required_strings:
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"Official response for {slug} has no valid {key}")
    verifier = str(payload["verifier"])
    tree = ast.parse(verifier, filename=f"{slug}:official_verifier")
    if not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "evaluate"
        for node in tree.body
    ):
        raise ValueError(f"Official verifier for {slug} has no evaluate function")
    schema = payload.get("solutionSchema")
    scoring = payload.get("scoring")
    improvement = payload.get("minImprovement")
    if not isinstance(schema, dict):
        raise ValueError(f"Official response for {slug} has invalid solutionSchema")
    if scoring not in {"maximize", "minimize"}:
        raise ValueError(f"Official response for {slug} has invalid scoring")
    if (
        not isinstance(improvement, (int, float))
        or isinstance(improvement, bool)
    ):
        raise ValueError(f"Official response for {slug} has invalid minImprovement")
    return {
        "id": payload.get("id"),
        "slug": slug,
        "title": payload["title"],
        "description": payload["description"],
        "scoring": scoring,
        "minImprovement": float(improvement),
        "evaluationMode": payload.get("evaluationMode"),
        "solutionSchema": schema,
        "verifier": verifier,
        "verifier_sha256": sha256_bytes(verifier.encode("utf-8")),
        "source_url": source_url,
        "fetched_at": fetched_at,
    }


def _question(problem: dict[str, Any]) -> str:
    direction = "larger" if problem["scoring"] == "maximize" else "smaller"
    schema = json.dumps(
        problem["solutionSchema"], ensure_ascii=False, indent=2
    )
    return (
        f"# Construction task: {problem['title']}\n\n"
        f"{problem['description']}\n\n"
        f"The official verifier accepts one JSON object. Only finite scores are "
        f"valid, and {direction} scores are better.\n\n"
        f"## Candidate schema\n\n```json\n{schema}\n```\n\n"
        "## Exact official Python verifier\n\n"
        f"```python\n{str(problem['verifier']).rstrip()}\n```\n\n"
        "End a model response with the following marker and exactly one strict "
        "JSON object. Do not add text after the object.\n\n"
        f"{FINAL_MARKER}\n"
        "<candidate JSON object>"
    )


def materialize(data_dir: Path) -> dict[str, Any]:
    data_dir = data_dir.resolve()
    snapshot_root = data_dir / "official_snapshot"
    snapshot_manifest = read_json(snapshot_root / "manifest.json")
    slugs = snapshot_manifest.get("problem_slugs")
    if not isinstance(slugs, list) or not slugs:
        raise ValueError("Official snapshot manifest has no problem_slugs")
    problems = [
        read_json(snapshot_root / "problems" / f"{slug}.json") for slug in slugs
    ]
    fetched_at = str(snapshot_manifest.get("fetched_at") or "")
    snapshot_date = fetched_at[:10]
    rows: list[dict[str, Any]] = []
    manifest_problems: list[dict[str, Any]] = []
    for problem in problems:
        slug = str(problem["slug"])
        verifier = str(problem["verifier"])
        digest = sha256_bytes(verifier.encode("utf-8"))
        if problem.get("verifier_sha256") != digest:
            raise ValueError(f"Snapshot verifier hash mismatch: {slug}")
        question = _question(problem)
        metadata = {
            "slug": slug,
            "title": problem["title"],
            "status": "active",
            "task_type": "construction",
            "evaluation_mode": "construction",
            "scoring": problem["scoring"],
            "min_improvement": problem["minImprovement"],
            "baseline_score": None,
            "solution_schema": problem["solutionSchema"],
            "source_url": problem["source_url"],
            "snapshot_date": snapshot_date,
            "problem_dir": f"problems/{slug}",
            "verifier_path": f"problems/{slug}/code/verifier.py",
            "verifier_sha256": digest,
            "verifier_origin": "einsteinarena_public_problem_api",
            "verifier_snapshot_id": snapshot_manifest.get("snapshot_id"),
            "official_problem_id": problem.get("id"),
            "final_answer_marker": FINAL_MARKER,
        }
        row = {
            "id": f"openarena_{slug}",
            "context": problem["description"],
            "question": question,
            "answer": [],
            "subject": ["mathematical_optimization", "open_problem"],
            "source": "EinsteinArena",
            "prompt": [{"role": "user", "content": question}],
            "label": [],
            "metadata": metadata,
        }
        rows.append(row)
        problem_root = data_dir / "problems" / slug
        markdown = (
            f"# {problem['title']}\n\n"
            f"{problem['description']}\n\n"
            f"- Scoring: `{problem['scoring']}`\n"
            f"- Minimum improvement: `{problem['minImprovement']}`\n"
            f"- Official API: {problem['source_url']}\n\n"
            f"## Candidate schema\n\n```json\n"
            f"{json.dumps(problem['solutionSchema'], ensure_ascii=False, indent=2)}"
            "\n```\n"
        )
        write_text_atomic(problem_root / "problem.md", markdown)
        write_text_atomic(problem_root / "code" / "verifier.py", verifier)
        write_json_atomic(
            problem_root / "eval" / "config.json",
            {
                "adapter": "openarena",
                "scoring": problem["scoring"],
                "min_improvement": problem["minImprovement"],
                "timeout_seconds": 120,
                "memory_gb": 8,
                "required_final_marker": FINAL_MARKER,
                "verifier_sha256": digest,
            },
        )
        write_json_atomic(
            problem_root / "source" / "source.json",
            {
                "official_api_url": problem["source_url"],
                "official_api_fetched_at": problem["fetched_at"],
                "official_snapshot_id": snapshot_manifest.get("snapshot_id"),
                "verifier_sha256": digest,
            },
        )
        manifest_problems.append(
            {
                "slug": slug,
                "title": problem["title"],
                "status": "active",
                "source_url": problem["source_url"],
                "verifier_sha256": digest,
                "verifier_origin": "einsteinarena_public_problem_api",
            }
        )
    write_jsonl_atomic(data_dir / "openarena.jsonl", rows)
    old_manifest_path = data_dir / "manifest.json"
    old_manifest = read_json(old_manifest_path) if old_manifest_path.is_file() else {}
    manifest = {
        **old_manifest,
        "dataset": "openarena",
        "upstream_name": "EinsteinArena",
        "snapshot_date": snapshot_date,
        "problem_count": len(rows),
        "open_problem_slugs": list(slugs),
        "problems": manifest_problems,
        "excluded_problem_definitions": snapshot_manifest.get(
            "excluded_problem_slugs",
            old_manifest.get(
                "excluded_problem_definitions", sorted(DEFAULT_EXCLUSIONS)
            ),
        ),
        "official_verifier_snapshot": {
            "snapshot_id": snapshot_manifest.get("snapshot_id"),
            "base_url": snapshot_manifest.get("base_url"),
            "fetched_at": fetched_at,
            "problem_count": len(rows),
        },
    }
    write_json_atomic(data_dir / "manifest.json", manifest)
    return manifest


def refresh(
    data_dir: Path,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 30,
    retries: int = 3,
    exclude_slugs: set[str] | None = None,
    include_slugs: set[str] | None = None,
    allow_removals: bool = False,
    problems_payload: Any | None = None,
    problem_payloads: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data_dir = data_dir.resolve()
    manifest_path = data_dir / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    existing = [str(value) for value in manifest.get("open_problem_slugs", [])]
    exclusions = {
        str(value)
        for value in manifest.get(
            "excluded_problem_definitions", sorted(DEFAULT_EXCLUSIONS)
        )
    }
    exclusions.update(exclude_slugs or set())
    inclusions = include_slugs or set()
    problems_url = f"{base_url.rstrip('/')}/api/problems"
    listing_payload = (
        problems_payload
        if problems_payload is not None
        else request_json(problems_url, timeout=timeout, retries=retries)
    )
    listed = _listing(listing_payload)
    by_slug = {str(problem["slug"]): problem for problem in listed}
    selectable = {
        slug
        for slug, problem in by_slug.items()
        if problem.get("evaluationMode") in {None, "construction"}
        and (slug not in exclusions or slug in inclusions)
    }
    unknown_inclusions = sorted(inclusions - set(by_slug))
    if unknown_inclusions:
        raise ValueError(
            f"Included slugs are absent from official listing: {unknown_inclusions}"
        )
    removed = sorted(set(existing) - selectable)
    if removed and not allow_removals:
        raise ValueError(
            "Refresh would remove existing problems; review upstream and pass "
            f"--allow-removals: {removed}"
        )
    retained = [slug for slug in existing if slug in selectable]
    added = sorted(selectable - set(existing))
    selected = retained + added
    if not selected:
        raise ValueError("Refresh selected no construction problems")

    fetched_at = datetime.now(timezone.utc).isoformat()
    normalized: list[dict[str, Any]] = []
    existing_details: dict[str, dict[str, str]] = {}
    dataset_jsonl = data_dir / "openarena.jsonl"
    if dataset_jsonl.is_file():
        for row in read_jsonl(dataset_jsonl):
            metadata = row.get("metadata")
            if not isinstance(metadata, dict) or not metadata.get("slug"):
                continue
            existing_details[str(metadata["slug"])] = {
                "title": str(metadata.get("title") or ""),
                "description": str(row.get("context") or ""),
            }
    for slug in selected:
        source_url = (
            f"{base_url.rstrip('/')}/api/problems/{urllib.parse.quote(slug)}"
        )
        payload = (
            problem_payloads[slug]
            if problem_payloads is not None
            else request_json(source_url, timeout=timeout, retries=retries)
        )
        normalized.append(
            _normalize_problem(
                slug,
                payload,
                source_url=source_url,
                fetched_at=fetched_at,
                fallback_title=existing_details.get(slug, {}).get("title"),
                fallback_description=existing_details.get(slug, {}).get(
                    "description"
                ),
            )
        )
    previous_hashes: dict[str, str] = {}
    old_snapshot_manifest = data_dir / "official_snapshot" / "manifest.json"
    if old_snapshot_manifest.is_file():
        loaded_hashes = read_json(old_snapshot_manifest).get("verifier_hashes")
        if isinstance(loaded_hashes, dict):
            previous_hashes = {
                str(key): str(value) for key, value in loaded_hashes.items()
            }
    hashes = {
        problem["slug"]: problem["verifier_sha256"] for problem in normalized
    }
    material = "\n".join(f"{slug} {hashes[slug]}" for slug in selected)
    snapshot_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + sha256_bytes(material.encode("utf-8"))[:12]
    )
    snapshot_root = data_dir / "official_snapshot"
    for problem in normalized:
        write_json_atomic(
            snapshot_root / "problems" / f"{problem['slug']}.json", problem
        )
    snapshot_manifest = {
        "schema_version": 1,
        "snapshot_id": snapshot_id,
        "source": "einsteinarena_public_problem_api",
        "base_url": base_url.rstrip("/"),
        "fetched_at": fetched_at,
        "problem_count": len(normalized),
        "problem_slugs": selected,
        "excluded_problem_slugs": sorted(exclusions - inclusions),
        "listing_url": problems_url,
        "new_problem_slugs": added,
        "removed_problem_slugs": removed,
        "changed_verifier_slugs": sorted(
            slug
            for slug, digest in hashes.items()
            if slug in previous_hashes and previous_hashes[slug] != digest
        ),
        "verifier_hashes": hashes,
        "aggregate_sha256": sha256_bytes(material.encode("utf-8")),
    }
    write_json_atomic(snapshot_root / "manifest.json", snapshot_manifest)
    materialize(data_dir)
    return snapshot_manifest

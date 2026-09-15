#!/usr/bin/env python3
"""Reproduce the published rank-1 scores of a baseline snapshot offline.

Every row of ``baseline_top1/einsteinarena_initial_top1_<date>.jsonl`` carries
the exact rank-1 candidate (``top1_solution``) and its published score
(``top1_score``).  This script re-scores each candidate with the frozen local
verifier, which is the strongest available check that a refreshed snapshot
really contains the official evaluation code for every packaged problem.

It needs no network access: the baseline file and the verifier snapshot are
both in the repository.  Slow verifiers (for example
``prime-number-theorem``) need a generous ``--timeout``.

Exit code is non-zero when any candidate is invalid or does not reproduce.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from openarena_eval.common import (  # noqa: E402
    default_data_dir,
    read_jsonl,
    write_json_atomic,
)

EXACT = "reproduced"
CLOSE = "close"
MISMATCH = "mismatch"
INVALID = "invalid"
NOT_PACKAGED = "not_packaged"


def latest_baseline() -> Path:
    candidates = sorted((REPO_ROOT / "baseline_top1").glob("*.jsonl"))
    if not candidates:
        raise SystemExit("No baseline_top1/*.jsonl snapshot is packaged")
    return candidates[-1]


def _relative_gap(expected: float | None, observed: float | None) -> float | None:
    if expected is None or observed is None:
        return None
    scale = max(abs(expected), abs(observed), 1e-300)
    return abs(expected - observed) / scale


def _classify(
    expected: float | None, observed: float | None, valid: bool
) -> str:
    if not valid or observed is None:
        return INVALID
    if expected is None:
        return CLOSE
    if observed == expected:
        return EXACT
    gap = _relative_gap(expected, observed)
    if gap is not None and gap <= 1e-12:
        return CLOSE
    return MISMATCH


def verify(
    *,
    baseline: Path,
    data_dir: Path,
    timeout: float,
    slugs: list[str] | None,
) -> dict[str, Any]:
    from openarena_eval.evaluator import OpenArenaEvaluator

    rows = read_jsonl(baseline)
    evaluator = OpenArenaEvaluator(data_dir, timeout_seconds=timeout)
    selected = set(slugs) if slugs else None

    results: list[dict[str, Any]] = []
    for row in rows:
        slug = str(row.get("slug") or "")
        if not slug:
            raise ValueError("Baseline row has no slug")
        if selected is not None and slug not in selected:
            continue
        candidate = row.get("top1_solution")
        if not isinstance(candidate, dict):
            raise ValueError(f"Baseline row for {slug} has no top1_solution")
        if slug not in evaluator.by_slug:
            # Published leaderboard entries can cover problems the packaged
            # selection deliberately excludes (for example the legacy
            # `kissing-number-d11` definition).
            print(f"  {slug:<32}  {NOT_PACKAGED}", flush=True)
            results.append(
                {
                    "slug": slug,
                    "status": NOT_PACKAGED,
                    "valid": None,
                    "expected_score": row.get("top1_score"),
                    "observed_score": None,
                    "relative_gap": None,
                    "scoring": row.get("scoring"),
                    "top1_system": row.get("top1_system"),
                    "solution_id": row.get("solution_id"),
                    "seconds": 0.0,
                    "reason": "slug is not part of the packaged dataset",
                }
            )
            continue
        expected = row.get("top1_score")
        expected = float(expected) if isinstance(expected, (int, float)) else None
        started = time.monotonic()
        scored = evaluator.score_candidate(
            slug, candidate, candidate_id=f"baseline:{slug}"
        )
        elapsed = time.monotonic() - started
        observed = scored.get("raw_score")
        observed = float(observed) if isinstance(observed, (int, float)) else None
        status = _classify(expected, observed, bool(scored.get("valid")))
        print(
            f"  {slug:<32}  {status:<10}"
            f"  expected={expected!r}  observed={observed!r}"
            f"  {elapsed:6.2f}s",
            flush=True,
        )
        results.append(
            {
                "slug": slug,
                "status": status,
                "valid": bool(scored.get("valid")),
                "expected_score": expected,
                "observed_score": observed,
                "relative_gap": _relative_gap(expected, observed),
                "scoring": row.get("scoring"),
                "top1_system": row.get("top1_system"),
                "solution_id": row.get("solution_id"),
                "seconds": elapsed,
                "reason": scored.get("reason"),
            }
        )

    counts: dict[str, int] = {}
    for item in results:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return {
        "baseline": str(baseline),
        "data_dir": str(Path(data_dir).resolve()),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "timeout_seconds": timeout,
        "counts": counts,
        "results": results,
    }


def _print_report(report: dict[str, Any]) -> None:
    rows = report["results"]
    width = max((len(item["slug"]) for item in rows), default=20)
    print(f"baseline: {report['baseline']}")
    print(f"problems: {len(rows)}  timeout: {report['timeout_seconds']}s\n")
    for item in rows:
        expected = item["expected_score"]
        observed = item["observed_score"]
        expected_text = "n/a" if expected is None else f"{expected!r}"
        observed_text = "n/a" if observed is None else f"{observed!r}"
        print(
            f"  {item['slug']:<{width}}  {item['status']:<10}"
            f"  expected={expected_text:<24} observed={observed_text:<24}"
            f"  {item['seconds']:6.2f}s"
        )
        if item["status"] in {MISMATCH, INVALID}:
            print(f"      reason: {item['reason']}")
    print("\ncounts:", json.dumps(report["counts"], ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Baseline JSONL (default: newest baseline_top1/*.jsonl).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=default_data_dir(),
        help="Snapshot directory (default: packaged data/).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=900,
        help="Per-candidate verifier timeout in seconds (default: 900).",
    )
    parser.add_argument(
        "--slugs",
        nargs="*",
        default=None,
        help="Only verify these slugs (default: every baseline row).",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    baseline = args.baseline or latest_baseline()
    report = verify(
        baseline=baseline,
        data_dir=args.data_dir,
        timeout=args.timeout,
        slugs=args.slugs,
    )
    _print_report(report)
    if args.output:
        write_json_atomic(args.output, report)
        print(f"\nwrote {args.output}")
    failures = report["counts"].get(MISMATCH, 0) + report["counts"].get(INVALID, 0)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

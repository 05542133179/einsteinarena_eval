from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .common import (
    default_data_dir,
    default_output_dir,
    read_json,
    write_json_atomic,
    write_jsonl_atomic,
)
from .evaluator import OpenArenaEvaluator, summarize_results
from .leaderboard import pull_leaderboard
from .sync import DEFAULT_BASE_URL, refresh


def _path_or_stdin(path: Path) -> str:
    if str(path) == "-":
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


def _json_print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def _add_runtime_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--memory-gb", type=float, default=8)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="openarena-eval",
        description=(
            "Sync EinsteinArena tasks, reproduce official scores locally, "
            "and export current leaderboards."
        ),
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=default_data_dir(),
        help="Dataset/snapshot directory (default: repository data/).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List packaged problems.")

    show = subparsers.add_parser("show", help="Print one problem statement.")
    show.add_argument("--slug", required=True)

    subparsers.add_parser("validate", help="Validate snapshot and verifier hashes.")

    score = subparsers.add_parser("score", help="Score one candidate or model output.")
    score.add_argument("--slug", required=True)
    source = score.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--candidate",
        type=Path,
        help="Strict candidate JSON file; use - for stdin.",
    )
    source.add_argument(
        "--model-output",
        type=Path,
        help="Text ending in FINAL_CANDIDATE_JSON; use - for stdin.",
    )
    score.add_argument("--candidate-id")
    score.add_argument("--output", type=Path)
    _add_runtime_options(score)

    batch = subparsers.add_parser("batch", help="Score candidate JSONL in batch.")
    batch.add_argument("--input", type=Path, required=True)
    batch.add_argument("--output", type=Path, required=True)
    batch.add_argument("--summary", type=Path)
    _add_runtime_options(batch)

    sync_parser = subparsers.add_parser(
        "refresh", help="Fetch current task definitions and exact verifiers."
    )
    sync_parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    sync_parser.add_argument("--timeout", type=float, default=30)
    sync_parser.add_argument("--retries", type=int, default=3)
    sync_parser.add_argument("--exclude-slug", action="append", default=[])
    sync_parser.add_argument("--include-slug", action="append", default=[])
    sync_parser.add_argument("--allow-removals", action="store_true")
    sync_parser.add_argument(
        "--problems-json",
        type=Path,
        help="Offline fixture for /api/problems.",
    )
    sync_parser.add_argument(
        "--problem-responses-dir",
        type=Path,
        help="Offline directory with <slug>.json problem responses.",
    )

    leaderboard = subparsers.add_parser(
        "leaderboard", help="Fetch current official per-problem leaderboards."
    )
    leaderboard.add_argument("--base-url", default=DEFAULT_BASE_URL)
    leaderboard.add_argument("--output-dir", type=Path, default=default_output_dir())
    leaderboard.add_argument("--top-k", type=int, default=10)
    leaderboard.add_argument("--leaderboard-limit", type=int, default=100)
    leaderboard.add_argument("--timeout", type=float, default=30)
    leaderboard.add_argument("--retries", type=int, default=3)
    leaderboard.add_argument("--local-results", type=Path)
    leaderboard.add_argument("--local-label", default="local")
    leaderboard.add_argument("--snapshot")
    leaderboard.add_argument(
        "--problems-json",
        type=Path,
        help="Offline fixture for /api/problems.",
    )
    leaderboard.add_argument(
        "--leaderboards-dir",
        type=Path,
        help="Offline directory with <slug>.json leaderboard responses.",
    )
    return parser.parse_args(argv)


def _evaluator(args: argparse.Namespace) -> OpenArenaEvaluator:
    return OpenArenaEvaluator(
        args.data_dir,
        timeout_seconds=float(getattr(args, "timeout", 120)),
        memory_gb=float(getattr(args, "memory_gb", 8)),
    )


def _run_score(args: argparse.Namespace) -> int:
    evaluator = _evaluator(args)
    if args.candidate is not None:
        candidate = json.loads(_path_or_stdin(args.candidate))
        if not isinstance(candidate, dict):
            raise TypeError("Candidate JSON must be an object")
        result = evaluator.score_candidate(
            args.slug, candidate, candidate_id=args.candidate_id
        )
    else:
        result = evaluator.score_model_output(
            args.slug,
            _path_or_stdin(args.model_output),
            candidate_id=args.candidate_id,
        )
    if args.output:
        write_json_atomic(args.output, result)
    _json_print(result)
    return 0 if result.get("valid") is True else 1


def _run_batch(args: argparse.Namespace) -> int:
    evaluator = _evaluator(args)
    results: list[dict[str, Any]] = []
    with args.input.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{args.input}:{line_number}: invalid JSON: {exc}"
                ) from exc
            if not isinstance(row, dict):
                raise TypeError(f"{args.input}:{line_number}: row is not an object")
            slug = str(row.get("slug") or "")
            if not slug:
                raise ValueError(f"{args.input}:{line_number}: missing slug")
            candidate_id = (
                str(row["candidate_id"]) if row.get("candidate_id") is not None else None
            )
            if isinstance(row.get("candidate"), dict):
                result = evaluator.score_candidate(
                    slug,
                    row["candidate"],
                    candidate_id=candidate_id,
                )
            elif isinstance(row.get("model_output"), str):
                result = evaluator.score_model_output(
                    slug,
                    row["model_output"],
                    candidate_id=candidate_id,
                )
            else:
                raise ValueError(
                    f"{args.input}:{line_number}: require candidate object "
                    "or model_output string"
                )
            results.append(result)
    summary = summarize_results(results)
    summary_path = args.summary or args.output.with_suffix(".summary.json")
    write_jsonl_atomic(args.output, results)
    write_json_atomic(summary_path, summary)
    _json_print(
        {
            **summary,
            "results_path": str(args.output.resolve()),
            "summary_path": str(summary_path.resolve()),
        }
    )
    return 0


def _run_refresh(args: argparse.Namespace) -> int:
    if bool(args.problems_json) != bool(args.problem_responses_dir):
        raise ValueError(
            "--problems-json and --problem-responses-dir must be used together"
        )
    listing = read_json(args.problems_json) if args.problems_json else None
    responses = None
    if args.problem_responses_dir:
        manifest = read_json(args.data_dir / "manifest.json")
        slugs = {
            str(value) for value in manifest.get("open_problem_slugs", [])
        }
        payload = listing if isinstance(listing, list) else listing.get("problems", [])
        slugs.update(str(row["slug"]) for row in payload if isinstance(row, dict))
        responses = {
            slug: read_json(args.problem_responses_dir / f"{slug}.json")
            for slug in slugs
            if (args.problem_responses_dir / f"{slug}.json").is_file()
        }
    result = refresh(
        args.data_dir,
        base_url=args.base_url,
        timeout=args.timeout,
        retries=args.retries,
        exclude_slugs=set(args.exclude_slug),
        include_slugs=set(args.include_slug),
        allow_removals=args.allow_removals,
        problems_payload=listing,
        problem_payloads=responses,
    )
    _json_print(result)
    return 0


def _run_leaderboard(args: argparse.Namespace) -> int:
    if bool(args.problems_json) != bool(args.leaderboards_dir):
        raise ValueError(
            "--problems-json and --leaderboards-dir must be used together"
        )
    problems_payload = read_json(args.problems_json) if args.problems_json else None
    leaderboard_payloads = None
    if args.leaderboards_dir:
        manifest = read_json(args.data_dir / "manifest.json")
        leaderboard_payloads = {
            str(slug): read_json(args.leaderboards_dir / f"{slug}.json")
            for slug in manifest["open_problem_slugs"]
        }
    result = pull_leaderboard(
        args.data_dir,
        args.output_dir,
        base_url=args.base_url,
        top_k=args.top_k,
        leaderboard_limit=args.leaderboard_limit,
        timeout=args.timeout,
        retries=args.retries,
        local_results=args.local_results,
        local_label=args.local_label,
        snapshot=args.snapshot,
        problems_payload=problems_payload,
        leaderboard_payloads=leaderboard_payloads,
    )
    _json_print(result)
    return 0


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.command == "list":
        problems = _evaluator(args).list_problems()
        for problem in problems:
            print(
                f"{problem['slug']:<42} "
                f"{problem['scoring']:<8} {problem['title']}"
            )
        return
    if args.command == "show":
        evaluator = _evaluator(args)
        evaluator.item(args.slug)
        path = args.data_dir / "problems" / args.slug / "problem.md"
        print(path.read_text(encoding="utf-8").rstrip())
        return
    if args.command == "validate":
        result = _evaluator(args).validate()
        _json_print(result)
        if result.get("valid") is not True:
            raise SystemExit(1)
        return
    runners = {
        "score": _run_score,
        "batch": _run_batch,
        "refresh": _run_refresh,
        "leaderboard": _run_leaderboard,
    }
    try:
        code = runners[args.command](args)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    raise SystemExit(code)

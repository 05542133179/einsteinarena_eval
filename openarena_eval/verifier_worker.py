from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - resource is Unix-only
    resource = None  # type: ignore[assignment]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verifier", type=Path, required=True)
    parser.add_argument("--memory-gb", type=float, default=8.0)
    parser.add_argument("--cpu-seconds", type=int, default=120)
    return parser.parse_args()


def apply_limits(memory_gb: float, cpu_seconds: int) -> None:
    if resource is not None:
        memory_bytes = max(1, int(memory_gb * 1024**3))
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(
                resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1)
            )
        except (ValueError, OSError):
            pass
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")


def load_evaluate(path: Path):
    spec = importlib.util.spec_from_file_location("official_verifier", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    evaluate = getattr(module, "evaluate", None)
    if not callable(evaluate):
        raise AttributeError(f"Verifier has no callable evaluate(data): {path}")
    return evaluate


def main() -> int:
    args = parse_args()
    apply_limits(args.memory_gb, args.cpu_seconds)
    started = time.monotonic()
    try:
        candidate: Any = json.load(sys.stdin)
        if not isinstance(candidate, dict):
            raise TypeError("Candidate must be a JSON object")
        score = float(load_evaluate(args.verifier.resolve())(candidate))
        finite = math.isfinite(score)
        payload = {
            "ok": finite,
            "score": score if finite else None,
            "reason": "ok" if finite else f"non_finite_score:{score}",
            "seconds": time.monotonic() - started,
        }
    except BaseException as exc:
        payload = {
            "ok": False,
            "score": None,
            "reason": f"{type(exc).__name__}: {exc}",
            "seconds": time.monotonic() - started,
            "traceback": traceback.format_exc(limit=12),
        }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

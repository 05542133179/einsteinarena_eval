from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_data_dir() -> Path:
    configured = os.environ.get("OPENARENA_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    source_checkout = project_root() / "data"
    if source_checkout.is_dir():
        return source_checkout
    bundled = Path(__file__).resolve().parent / "_data"
    if bundled.is_dir():
        return bundled
    return source_checkout


def default_output_dir() -> Path:
    configured = os.environ.get("OPENARENA_OUTPUT_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return project_root() / "outputs"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            rows.append(value)
    return rows


def write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def write_json_atomic(path: Path, value: Any) -> None:
    write_text_atomic(
        path,
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
    )


def write_jsonl_atomic(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rendered = "".join(
        json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows
    )
    write_text_atomic(path, rendered)

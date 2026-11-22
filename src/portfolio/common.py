"""Shared paths, contracts, checksummed downloads and serialisation."""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(os.environ.get("PORTFOLIO_ROOT", Path(__file__).resolve().parents[2]))
SEED = 42


def require_columns(frame: pd.DataFrame, expected: list[str]) -> None:
    missing = sorted(set(expected) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value: dict | list) -> None:
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, (pd.Timestamp, Path)):
            return str(item)
        raise TypeError(f"Cannot encode {type(item)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=convert, allow_nan=False) + "\n")


def fetch_dataset(name: str) -> Path:
    """Download only the named member; validate both archive and extracted bytes."""
    sources = json.loads((ROOT / "data/sources.json").read_text())
    spec = sources[name]
    target = ROOT / "data/raw" / spec["member"]
    if target.exists():
        if sha256(target) != spec["file_sha256"]:
            raise ValueError(f"Checksum mismatch: {target}. Remove it and download again.")
        return target
    payload = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                spec["url"], headers={"User-Agent": "analytics-portfolio/1.0"}
            )
            with urllib.request.urlopen(req, timeout=90) as response:
                payload = response.read(40_000_001)
            break
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    if payload is None or len(payload) > 40_000_000:
        raise ValueError("Dataset response is missing or exceeds the 40 MB download limit")
    if hashlib.sha256(payload).hexdigest() != spec["archive_sha256"]:
        raise ValueError(
            f"Upstream archive changed for {name}; review its source before updating hashes"
        )
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        member = archive.getinfo(spec["member"])
        if member.file_size > 40_000_000:
            raise ValueError("Extracted dataset exceeds size limit")
        content = archive.read(member)
    if hashlib.sha256(content).hexdigest() != spec["file_sha256"]:
        raise ValueError(f"Extracted checksum mismatch for {name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(target)
    return target

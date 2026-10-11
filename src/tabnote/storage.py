"""Atomic persistence and external-change fingerprints."""

from __future__ import annotations

import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .format import serialize
from .model import Document


class ExternalModificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileStamp:
    digest: str


def stamp(path: Path) -> FileStamp:
    return FileStamp(hashlib.sha256(path.read_bytes()).hexdigest())


def save(document: Document, path: Path, expected: FileStamp | None = None) -> FileStamp:
    if expected is not None and path.exists() and stamp(path) != expected:
        raise ExternalModificationError("file changed outside Tabnote")
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(serialize(document))
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            os.chmod(temp_name, mode)
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return stamp(path)

"""Project utility helpers (non-test)."""
from pathlib import Path
from typing import Union


def chapter_id_from_path(path: Union[str, Path]) -> str:
    """Return the chapter id derived from filenames like 1000_zh.txt or 1000_vi.txt -> '1000'"""
    p = Path(path)
    return p.stem.split("_")[0]


__all__ = ["chapter_id_from_path"]

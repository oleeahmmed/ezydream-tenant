#!/usr/bin/env python3
"""Rebuild monolithic views.py from broken split (attach at top) + serializers.py, then re-run split_api_serializers."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


def _first_class_line_in_serializers(ser: str) -> int:
    m = re.search(r"^class \w+", ser, re.M)
    if not m:
        raise SystemExit("No class in serializers.py")
    return m.start()


def recover(api_dir: Path) -> None:
    views_path = api_dir / "views.py"
    ser_path = api_dir / "serializers.py"
    if not ser_path.exists():
        raise SystemExit(f"Missing {ser_path}")
    src = views_path.read_text(encoding="utf-8")
    ser_full = ser_path.read_text(encoding="utf-8")
    ser_body = ser_full[_first_class_line_in_serializers(ser_full) :].lstrip("\n")

    tree = ast.parse(src)
    attach_node = next(
        (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("attach_")), None
    )
    imp_node = next(
        (
            n
            for n in tree.body
            if isinstance(n, ast.ImportFrom) and n.level == 1 and n.module == "serializers"
        ),
        None,
    )
    if not attach_node or not imp_node:
        raise SystemExit("views.py does not look like broken split output")

    lines = src.splitlines(keepends=True)
    part1 = "".join(lines[: attach_node.lineno - 1])
    part4 = "".join(lines[imp_node.end_lineno :])
    attach_block = "".join(lines[attach_node.lineno - 1 : attach_node.end_lineno])

    merged = (
        part1.rstrip()
        + "\n\n"
        + ser_body.rstrip()
        + "\n\n"
        + part4.rstrip()
        + "\n\n\n"
        + attach_block.rstrip()
        + "\n"
    )
    views_path.write_text(merged, encoding="utf-8")
    ser_path.unlink()
    print("Recovered", views_path, "and removed", ser_path)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        recover(Path(arg).resolve())

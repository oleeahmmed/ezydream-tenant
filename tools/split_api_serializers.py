#!/usr/bin/env python3
"""
Split apps/<app>/api/views.py into serializers.py (Serializer subclasses) and views.py (APIView + routes).

Preserves blank lines between imports. Places ``from .serializers import`` before the first APIView
class and moves ``attach_*_routes`` functions to the end of views.py.

Usage: python tools/split_api_serializers.py apps/sales/api
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


def _is_serializer_class(node: ast.ClassDef) -> bool:
    for b in node.bases:
        s = ast.unparse(b)
        if "APIView" in s:
            return False
        if "Serializer" in s:
            return True
    return False


def _is_attach_routes_function(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.FunctionDef)
        and node.name.startswith("attach_")
        and node.name.endswith("_routes")
    )


def _strip_serializer_only_imports(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("from django_bolt.serializers import"):
            continue
        if s.startswith("from django_bolt.serializers.nested import"):
            continue
        out.append(line)
    return out


def _comment_prefix_start_line(lines: list[str], class_lineno: int) -> int:
    """First 1-based line index to include above ``class`` (comments/blanks), or ``class_lineno`` if none."""
    i = class_lineno - 1
    while i >= 1:
        stripped = lines[i - 1].strip()
        if stripped == "" or stripped.startswith("#"):
            i -= 1
            continue
        break
    return i + 1


def split_api_dir(api_dir: Path) -> None:
    views_path = api_dir / "views.py"
    if not views_path.exists():
        raise SystemExit(f"Missing {views_path}")

    src = views_path.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)

    serializer_spans: list[tuple[int, int]] = []
    serializer_nodes: list[ast.ClassDef] = []
    attach_spans: list[tuple[int, int]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if _is_serializer_class(node):
                serializer_spans.append((node.lineno, node.end_lineno or node.lineno))
                serializer_nodes.append(node)
        elif _is_attach_routes_function(node):
            attach_spans.append((node.lineno, node.end_lineno or node.lineno))

    ser_lines: list[str] = []
    prev_end = 0
    for node in serializer_nodes:
        end_ln = node.end_lineno or node.lineno
        prefix_start = _comment_prefix_start_line(lines, node.lineno)
        if prefix_start <= prev_end:
            prefix_start = node.lineno
        chunk = "".join(lines[prefix_start - 1 : end_ln])
        ser_lines.append(chunk)
        prev_end = end_ln

    bad_lines = set()
    for s, e in serializer_spans:
        bad_lines.update(range(s, e + 1))
    for s, e in attach_spans:
        bad_lines.update(range(s, e + 1))

    view_lines = [ln for i, ln in enumerate(lines, start=1) if i not in bad_lines]

    # Re-append attach_* bodies at end (preserve order of multiple attach funcs if any)
    attach_bodies: list[str] = []
    for s, e in sorted(attach_spans):
        attach_bodies.append("".join(lines[s - 1 : e]))

    # Insert serializers import before first APIView class line (in filtered file)
    import_block = (
        "\nfrom .serializers import (\n"
        + _build_serializers_import(serializer_nodes)
        + ")\n\n"
    )

    insert_at = 0
    for i, ln in enumerate(view_lines):
        if re.match(r"^class \w+.*\(APIView\)", ln.strip()):
            insert_at = i
            break

    preamble = _strip_serializer_only_imports(view_lines[:insert_at])
    rest = view_lines[insert_at:]

    ser_path = api_dir / "serializers.py"
    ser_header = '''"""Request/response serializers for Bolt API (see django_bolt_guide: input/output types)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

from apps.core.bolt_common import PAGE_MAX_ITEMS

'''
    ser_path.write_text(ser_header + "\n\n".join(s.rstrip() + "\n" for s in ser_lines), encoding="utf-8")

    views_out = (
        "".join(preamble).rstrip()
        + import_block
        + "".join(rest).rstrip()
        + ("\n\n\n" if attach_bodies else "")
        + "\n\n".join(b.rstrip() + "\n" for b in attach_bodies)
    )
    views_path.write_text(views_out, encoding="utf-8")
    print("Wrote", ser_path, "and updated", views_path)


def _build_serializers_import(serializer_nodes: list[ast.ClassDef]) -> str:
    names = [n.name for n in serializer_nodes]
    if not names:
        return "    # no serializers\n"
    return "".join(f"    {n},\n" for n in names)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: split_api_serializers.py <path-to-api-dir>")
    split_api_dir(Path(sys.argv[1]).resolve())

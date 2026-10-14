#!/usr/bin/env python3
"""Save one MCP business response locally or read selected fields from it."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import jmespath  # type: ignore
except ImportError:
    jmespath = None


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: str | None) -> Any:
    try:
        text = Path(path).read_text(encoding="utf-8-sig") if path else sys.stdin.read().lstrip("\ufeff")
        return json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON input: {exc}")


def resolve(data: Any, expression: str) -> Any:
    if jmespath is not None:
        return jmespath.search(expression, data)
    if any(char in expression for char in "[*"):
        fail("jmespath is required for array expressions")
    current = data
    for part in expression.split("."):
        current = current.get(part) if isinstance(current, dict) else None
    return current


def format_value(value: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(value, ensure_ascii=False, indent=2)
    if output_format == "jsonl":
        rows = value if isinstance(value, list) else [value]
        return "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
    if not isinstance(value, list) or not value or not all(isinstance(row, dict) for row in value):
        fail(f"{output_format} requires a non-empty array of objects")
    columns = list(dict.fromkeys(key for row in value for key in row))
    if output_format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=columns)
        writer.writeheader()
        writer.writerows(value)
        return buffer.getvalue().rstrip()
    widths = [max(len(str(column)), *(len(str(row.get(column, ""))) for row in value)) for column in columns]
    lines = [
        "  ".join(column.ljust(widths[index]) for index, column in enumerate(columns)),
        "  ".join("-" * width for width in widths),
    ]
    lines.extend("  ".join(str(row.get(column, "")).ljust(widths[index]) for index, column in enumerate(columns)) for row in value)
    return "\n".join(lines)


def command_save(args: argparse.Namespace) -> int:
    payload = load_json(args.file)
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    label = re.sub(r"[^0-9A-Za-z_-]+", "_", args.label).strip("_")[:64] or "response"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"{label}-{stamp}-{secrets.token_hex(3)}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(path))
    return 0


def command_read(args: argparse.Namespace) -> int:
    payload = load_json(args.file)
    if args.path:
        result = resolve(payload, args.path)
    else:
        fields = [field.strip() for field in args.fields.split(",") if field.strip()]
        result = {field: resolve(payload, field) for field in fields}
    if isinstance(result, list):
        start = args.offset or 0
        result = result[start : start + args.limit if args.limit is not None else None]
    print(format_value(result, args.format))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    save = commands.add_parser("save", help="validate and save one JSON response")
    save.add_argument("--file", help="input JSON file; omit to read stdin")
    save.add_argument("--out-dir", required=True)
    save.add_argument("--label", default="echotik-response")
    save.set_defaults(func=command_save)

    read = commands.add_parser("read", help="read selected fields from saved JSON")
    read.add_argument("file")
    query = read.add_mutually_exclusive_group(required=True)
    query.add_argument("--path")
    query.add_argument("--fields")
    read.add_argument("--limit", type=int)
    read.add_argument("--offset", type=int)
    read.add_argument("--format", choices=["json", "jsonl", "csv", "table"], default="json")
    read.set_defaults(func=command_read)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

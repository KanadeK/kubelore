"""Command-line entry point for read-only local bundle analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from kubelore.adapters.files import BundleFormatError
from kubelore.services.analyze import analyze_file
from kubelore.services.render import render_html, render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kubelore", description="Generate an offline Kubernetes fault chain.")
    parser.add_argument("--version", action="version", version="kubelore 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="analyze a local JSON bundle")
    analyze.add_argument("bundle", type=Path, help="KubeLore bundle or Kubernetes items JSON export")
    analyze.add_argument("--format", choices=("text", "json", "html"), default="text")
    analyze.add_argument("--output", type=Path, help="write the rendered report to this path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze_file(args.bundle)
    except (BundleFormatError, FileNotFoundError) as exc:
        raise SystemExit(f"kubelore: {exc}") from exc
    renderers = {"text": render_text, "json": render_json, "html": render_html}
    output = renderers[args.format](report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


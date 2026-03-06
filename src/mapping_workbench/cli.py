from __future__ import annotations

import argparse
from pathlib import Path

from mapping_workbench.mapper import format_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest mappings between two OpenAPI specs.")
    parser.add_argument("--source", required=True, help="Path to source OpenAPI spec")
    parser.add_argument("--target", required=True, help="Path to target OpenAPI spec")
    parser.add_argument("--output", help="Optional path to write the JSON report")
    args = parser.parse_args()

    report = format_report(args.source, args.target)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Wrote mapping report to {output_path}")
        return

    print(report)


if __name__ == "__main__":
    main()

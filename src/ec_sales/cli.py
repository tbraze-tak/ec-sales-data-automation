from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import PipelineError, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize synthetic EC sales CSV files.")
    parser.add_argument("--input", type=Path, default=Path("sample_data/input"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--contract", type=Path, default=Path("config/source_contracts.json"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        model = run_pipeline(args.input, args.output, args.contract)
    except PipelineError as exc:
        print(f"ERROR: {exc}")
        return 2
    quality = model["quality"]
    print(
        f"Processed {quality['input_rows']} rows: "
        f"accepted={quality['accepted_rows']}, "
        f"duplicates={quality['excluded_duplicate_rows']}, "
        f"rejected={quality['rejected_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

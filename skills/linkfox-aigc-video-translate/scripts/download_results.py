#!/usr/bin/env python3
"""Save successful media from a saved query response without another API call."""
import argparse
import json
from pathlib import Path
from material_runtime import check_output_directory, download_results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response_file", type=Path)
    args = parser.parse_args()
    check_output_directory()
    result = json.loads(args.response_file.read_text(encoding="utf-8"))
    if not isinstance(result, dict) or result.get("status") != "SUCCESS":
        parser.error("A successful task-query response is required; keep pending/failed task status")
    paths, _ = download_results(result, Path(__file__).resolve().parent)
    if not paths:
        print("Saved full response: " + str(args.response_file.resolve()))


if __name__ == "__main__":
    main()

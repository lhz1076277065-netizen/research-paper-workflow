#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_validation.package import validate_project
from research_validation.profiles import PROFILE_IDS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a complete research-paper project package.")
    parser.add_argument("project_root")
    parser.add_argument("--profile", choices=("auto",) + PROFILE_IDS, default="auto")
    parser.add_argument("--report", help="Write the JSON report to this path")
    parser.add_argument("--json", action="store_true", help="Print the complete JSON report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_project(Path(args.project_root), args.profile)
    payload = report.to_dict()
    output = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        destination = Path(args.report).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    if args.json:
        print(output, end="")
    else:
        print(f"Decision: {payload['decision']}")
        print(f"Profile: {payload['profile']}")
        for gate, status in payload["gates"].items():
            print(f"  {gate}: {status}")
        for item in payload["errors"]:
            location = f":{item['location']}" if item["location"] else ""
            print(f"ERROR [{item['gate']}/{item['code']}] {item['artifact']}{location} - {item['message']}")
        for item in payload["warnings"]:
            location = f":{item['location']}" if item["location"] else ""
            print(f"WARNING [{item['gate']}/{item['code']}] {item['artifact']}{location} - {item['message']}")
    return 0 if payload["decision"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())

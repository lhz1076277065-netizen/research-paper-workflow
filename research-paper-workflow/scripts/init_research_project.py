#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date
from pathlib import Path

from research_validation.profiles import PROFILE_IDS, load_profile


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return value or "research-project"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a validated research-paper project.")
    parser.add_argument("--profile", required=True, choices=PROFILE_IDS)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--project-id", default="")
    parser.add_argument("--title", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_profile(args.profile)
    destination = Path(args.dest).expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parent.parent
    template_root = skill_root / "assets" / "templates"
    for template in template_root.iterdir():
        if template.name == "research_manifest.json":
            continue
        shutil.copy2(template, destination / template.name)

    manifest = json.loads((template_root / "research_manifest.json").read_text(encoding="utf-8"))
    manifest["project_id"] = slugify(args.project_id or destination.name)
    manifest["title"] = args.title
    manifest["article_type"] = args.profile
    manifest["created_at"] = date.today().isoformat()
    manifest["updated_at"] = manifest["created_at"]
    (destination / "research_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    for name in ("data", "evidence", "figures", "manuscript", "outputs", "results", "validation"):
        (destination / name).mkdir(exist_ok=True)

    print(f"Initialized {args.profile} research project at {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

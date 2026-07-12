#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from research_validation.citations import parse_reference_export
from research_validation.common import load_csv, normalize_doi, write_json


USER_AGENT = "research-paper-workflow/2.0 (scholarly metadata verification)"


def fetch_json(url: str, timeout: float = 20.0) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def crossref_record(doi: str) -> dict:
    data = fetch_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}")
    message = data.get("message", {})
    return {
        "title": (message.get("title") or [""])[0],
        "publisher": message.get("publisher", ""),
        "container_title": (message.get("container-title") or [""])[0],
        "type": message.get("type", ""),
        "is_referenced_by_count": message.get("is-referenced-by-count"),
        "relation": message.get("relation", {}),
        "update_to": message.get("update-to", []),
    }


def openalex_record(doi: str) -> dict:
    query = urllib.parse.urlencode({"filter": f"doi:https://doi.org/{doi}", "per-page": 1})
    payload = fetch_json(f"https://api.openalex.org/works?{query}")
    results = payload.get("results", [])
    if not results:
        raise ValueError(f"OpenAlex has no record for DOI {doi}")
    data = results[0]
    return {
        "title": data.get("display_name", ""),
        "publication_year": data.get("publication_year"),
        "cited_by_count": data.get("cited_by_count"),
        "is_retracted": data.get("is_retracted"),
        "type": data.get("type", ""),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh public citation metadata and parse reference exports.")
    parser.add_argument("project_root")
    parser.add_argument("--online", action="store_true", help="Query Crossref and OpenAlex")
    parser.add_argument("--import", dest="imports", action="append", default=[], metavar="FILE", help="Parse CIW, RIS, BibTeX or CSV export")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between public API requests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    evidence = root / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)

    imported: list[dict[str, str]] = []
    for value in args.imports:
        path = Path(value).expanduser().resolve()
        imported.extend(parse_reference_export(path))
    if imported:
        write_json(evidence / "imported_references.json", {"records": imported})

    matrix = root / "literature_matrix.csv"
    if not matrix.exists():
        raise SystemExit(f"missing literature matrix: {matrix}")
    rows = load_csv(matrix)
    cache_path = evidence / "citation_metadata.json"
    existing = {}
    if cache_path.exists():
        existing = json.loads(cache_path.read_text(encoding="utf-8"))
    records = dict(existing.get("records", {}))
    errors: list[dict[str, str]] = []

    if args.online:
        for row in rows:
            doi = normalize_doi(row.get("doi", ""))
            if not doi:
                continue
            record = {"checked_at": datetime.now(timezone.utc).isoformat(), "crossref": {}, "openalex": {}, "retracted": None}
            try:
                record["crossref"] = crossref_record(doi)
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
                errors.append({"doi": doi, "source": "crossref", "error": str(error)})
            finally:
                time.sleep(max(0.0, args.delay))
            try:
                record["openalex"] = openalex_record(doi)
                record["retracted"] = record["openalex"].get("is_retracted")
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
                errors.append({"doi": doi, "source": "openalex", "error": str(error)})
            finally:
                time.sleep(max(0.0, args.delay))
            records[doi] = record

    write_json(cache_path, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "errors": errors,
        "note": "JCR quartiles must come from a legitimate user-provided JCR export; they are never inferred here.",
    })
    print(f"Wrote citation metadata cache: {cache_path}")
    if errors:
        print(f"Completed with {len(errors)} metadata error(s).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

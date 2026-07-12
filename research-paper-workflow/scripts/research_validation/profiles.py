from __future__ import annotations

import json
from pathlib import Path


PROFILE_IDS = (
    "empirical-general",
    "sem-survey",
    "ml-predictive",
    "simulation-computational",
    "lab-field",
    "observational-causal",
    "systematic-review-meta-analysis",
    "qualitative",
    "theoretical-methods",
)


def profiles_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "profiles"


def load_profile(profile_id: str) -> dict:
    if profile_id not in PROFILE_IDS:
        raise ValueError(f"unknown profile: {profile_id}")
    path = profiles_dir() / f"{profile_id}.json"
    with path.open("r", encoding="utf-8") as handle:
        profile = json.load(handle)
    if profile.get("id") != profile_id:
        raise ValueError(f"profile id mismatch: {path}")
    return profile

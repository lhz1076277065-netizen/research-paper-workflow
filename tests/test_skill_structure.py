from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "research-paper-workflow"


class SkillStructureTests(unittest.TestCase):
    def test_skill_frontmatter_and_size(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: research-paper-workflow\n"))
        self.assertLessEqual(len(text.splitlines()), 500)

    def test_all_direct_references_exist(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for relative in set(re.findall(r"`((?:references|scripts)/[^`]+)`", text)):
            self.assertTrue((SKILL / relative).exists(), relative)

    def test_nine_profiles_are_valid_json(self) -> None:
        profiles = sorted((SKILL / "assets" / "profiles").glob("*.json"))
        self.assertEqual(9, len(profiles))
        for path in profiles:
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.stem, value["id"])

    def test_all_nine_upgrade_surfaces_exist(self) -> None:
        required = [
            "scripts/validate_research_package.py",
            "scripts/refresh_literature_metadata.py",
            "scripts/init_research_project.py",
            "scripts/research_validation/results.py",
            "scripts/research_validation/figures.py",
            "scripts/research_validation/docx.py",
            "scripts/audit_manuscript_language.py",
            "assets/templates/research_manifest.json",
            "assets/profiles/sem-survey.json",
        ]
        for relative in required:
            self.assertTrue((SKILL / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()

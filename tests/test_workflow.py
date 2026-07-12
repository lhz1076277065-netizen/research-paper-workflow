from __future__ import annotations

import csv
import binascii
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "research-paper-workflow"
SCRIPTS = SKILL_ROOT / "scripts"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "complete-project"
sys.path.insert(0, str(SCRIPTS))

from audit_manuscript_language import audit_file  # noqa: E402
import refresh_literature_metadata as metadata_refresh  # noqa: E402
from research_validation.citations import parse_bibtex, parse_ciw, parse_ris  # noqa: E402
from research_validation.common import ValidationReport  # noqa: E402
from research_validation.docx import validate_docx  # noqa: E402
from research_validation.package import validate_project  # noqa: E402
from research_validation.profiles import PROFILE_IDS, load_profile  # noqa: E402


def issue_codes(report) -> set[str]:
    return {item.code for item in report.issues}


def rewrite_csv(path: Path, mutate) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0])
    mutate(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, width: int, height: int, dpi: int) -> None:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", binascii.crc32(name + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    ppm = round(dpi / 0.0254)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += chunk(b"pHYs", struct.pack(">IIB", ppm, ppm, 1))
    payload += chunk(b"IDAT", zlib.compress(rows))
    payload += chunk(b"IEND", b"")
    path.write_bytes(payload)


class ProjectValidationTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        destination = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, destination)
        return temp, destination

    def test_complete_project_passes_every_gate(self) -> None:
        report = validate_project(FIXTURE)
        self.assertEqual("ready", report.decision, report.to_dict())
        self.assertTrue(report.gates)
        self.assertTrue(all(status == "pass" for status in report.gates.values()), report.to_dict())

    def test_stale_data_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        rewrite_csv(project / "data_manifest.csv", lambda rows: rows[0].update({"latest_available_date": "2026-06-30", "freshness_justification": ""}))
        report = validate_project(project)
        self.assertEqual("not_ready", report.decision)
        self.assertIn("stale_data", issue_codes(report))

    def test_malformed_csv_fails_closed_without_crashing(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        with (project / "figure_manifest.csv").open("a", encoding="utf-8") as handle:
            handle.write("too,many,unexpected,fields,for,this,row,1,2,3,4,5,6,7,8,9,10\n")
        report = validate_project(project)
        self.assertEqual("not_ready", report.decision)
        self.assertIn("invalid_figure_manifest", issue_codes(report))

    def test_artifact_outside_project_root_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        rewrite_csv(project / "results_ledger.csv", lambda rows: rows[0].update({"source_artifact": "../outside.csv"}))
        report = validate_project(project)
        self.assertEqual("not_ready", report.decision)
        self.assertIn("validator_exception", issue_codes(report))

    def test_result_mismatch_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        manuscript = project / "manuscript" / "paper.md"
        manuscript.write_text(manuscript.read_text(encoding="utf-8").replace("0.12", "0.99"), encoding="utf-8")
        report = validate_project(project)
        self.assertIn("result_not_found", issue_codes(report))

    def test_source_result_mismatch_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        source = project / "results" / "result.csv"
        source.write_text(source.read_text(encoding="utf-8").replace("RES1,0.12", "RES1,0.99"), encoding="utf-8")
        report = validate_project(project)
        self.assertIn("result_source_mismatch", issue_codes(report))

    def test_result_value_and_sample_must_share_labeled_context(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        manuscript = project / "manuscript" / "paper.md"
        manuscript.write_text("Median absolute error was not reported.\n\nAn unrelated value was 0.12.\n\nA separate sample used n = 100.\n\nFigure 1.\n\n[R1] [R2]", encoding="utf-8")
        report = validate_project(project)
        self.assertIn("result_not_found", issue_codes(report))

    def test_nonfinite_result_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        rewrite_csv(project / "results_ledger.csv", lambda rows: rows[0].update({"value": "NaN"}))
        report = validate_project(project)
        self.assertIn("invalid_result_value", issue_codes(report))

    def test_missing_figure_source_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        (project / "figures" / "figure1_source.svg").unlink()
        report = validate_project(project)
        self.assertIn("missing_figure_source", issue_codes(report))

    def test_chinese_nonacademic_language_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        manuscript = project / "manuscript" / "paper.md"
        with manuscript.open("a", encoding="utf-8") as handle:
            handle.write("\n众所周知，本研究具有非常重要的意义。\n")
        report = validate_project(project)
        self.assertIn("zh_obviousness", issue_codes(report))
        self.assertEqual("not_ready", report.decision)

    def test_sem_profile_requires_native_model(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        manifest_path = project / "research_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["article_type"] = "sem-survey"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = validate_project(project)
        self.assertIn("missing_sem_model", issue_codes(report))

    def test_q1_q2_ratio_below_target_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        rewrite_csv(project / "literature_matrix.csv", lambda rows: rows[0].update({"jcr_quartile": "Q3"}))
        rewrite_csv(project / "journal_metrics.csv", lambda rows: rows[0].update({"jcr_quartile": "Q3"}))
        report = validate_project(project)
        self.assertIn("recent_q1q2_ratio", issue_codes(report))

    def test_documented_q1_q2_exception_is_warning_only(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        rewrite_csv(project / "literature_matrix.csv", lambda rows: rows[0].update({"jcr_quartile": "Q3"}))
        rewrite_csv(project / "journal_metrics.csv", lambda rows: rows[0].update({"jcr_quartile": "Q3"}))
        evidence = project / "evidence" / "q1q2_exception.txt"
        evidence.write_text("Documented exhaustive search found no additional eligible Q1/Q2 studies.", encoding="utf-8")
        manifest_path = project / "research_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["recent_q1q2_exception"] = {"approved": True, "reason": "Field scarcity after exhaustive search", "evidence_file": "evidence/q1q2_exception.txt"}
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        report = validate_project(project)
        self.assertEqual("ready", report.decision, report.to_dict())
        self.assertEqual("warning", report.gates["literature"])

    def test_low_dpi_raster_figure_fails(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        png = project / "figures" / "figure1.png"
        write_png(png, 100, 100, 72)
        rewrite_csv(project / "figure_manifest.csv", lambda rows: rows[0].update({"file": "figures/figure1.png", "vector_required": "false"}))
        report = validate_project(project)
        self.assertIn("low_dpi", issue_codes(report))

    def test_effective_dpi_uses_intended_publication_width(self) -> None:
        temp, project = self.copy_fixture()
        self.addCleanup(temp.cleanup)
        png = project / "figures" / "figure1.png"
        write_png(png, 100, 100, 1200)
        rewrite_csv(project / "figure_manifest.csv", lambda rows: rows[0].update({"file": "figures/figure1.png", "vector_required": "false", "intended_width_mm": "100"}))
        report = validate_project(project)
        self.assertIn("low_dpi", issue_codes(report))

    def test_all_profiles_load(self) -> None:
        for profile_id in PROFILE_IDS:
            self.assertEqual(profile_id, load_profile(profile_id)["id"])

    def test_each_profile_can_pass_with_complete_evidence(self) -> None:
        for profile_id in PROFILE_IDS:
            with self.subTest(profile=profile_id):
                temp, project = self.copy_fixture()
                try:
                    profile = load_profile(profile_id)
                    manifest_path = project / "research_manifest.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest["article_type"] = profile_id
                    if profile.get("require_sem"):
                        model = project / "outputs" / "sem-model.native"
                        model.write_text("native model evidence", encoding="utf-8")
                        manifest["sem_model_files"] = ["outputs/sem-model.native"]
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

                    def add_experiments(rows) -> None:
                        present = {row["experiment_class"] for row in rows}
                        for position, category in enumerate(profile.get("required_experiment_classes", []), start=10):
                            if category in present:
                                continue
                            output = project / "outputs" / f"{category}.log"
                            output.write_text(f"{category} complete", encoding="utf-8")
                            rows.append({
                                "experiment_id": f"EP{position}", "experiment_class": category,
                                "research_question": "RQ1", "input_data": "D1", "method": "Profile method",
                                "baseline_control": "Defined comparator", "metrics": "Prespecified metric",
                                "seeds_repeats": "Documented", "command": f"python run.py --mode {category}",
                                "environment": "Python 3.11; environment.lock", "output_artifact": f"outputs/{category}.log",
                                "acceptance_criterion": "Artifact generated", "status": "complete", "failure_reason": "",
                            })
                    rewrite_csv(project / "experiment_manifest.csv", add_experiments)

                    def add_domain(rows) -> None:
                        present = {row["element_type"] for row in rows}
                        for position, element in enumerate(profile.get("required_domain_elements", []), start=10):
                            if element in present:
                                continue
                            rows.append({
                                "knowledge_id": f"KP{position}", "element_type": element,
                                "knowledge_element": element.replace("_", " "), "current_understanding": "Verified profile knowledge.",
                                "authoritative_source": "R2", "competing_view": "Alternative documented.",
                                "relevance": "Profile requirement", "uncertainty": "Low",
                                "manuscript_location": "Methods", "status": "verified",
                            })
                    rewrite_csv(project / "domain_knowledge_map.csv", add_domain)

                    def add_diagnostics(rows) -> None:
                        present = {row["category"] for row in rows}
                        for position, category in enumerate(profile.get("required_analysis_diagnostics", []), start=10):
                            if category in present:
                                continue
                            rows.append({
                                "diagnostic_id": f"AP{position}", "category": category,
                                "metric": category.replace("_", " "), "value": "acceptable", "unit": "",
                                "threshold_or_comparator": "Prespecified", "method": "Profile diagnostic",
                                "source_artifact": "outputs/diagnostics.json", "status": "pass",
                                "interpretation": "Requirement passed",
                            })
                    rewrite_csv(project / "analysis_diagnostics.csv", add_diagnostics)

                    report = validate_project(project)
                    self.assertEqual("ready", report.decision, report.to_dict())
                finally:
                    temp.cleanup()


class ParserTests(unittest.TestCase):
    def test_reference_export_parsers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ciw = root / "refs.ciw"
            ciw.write_text("PT J\nAU Doe, J\nTI CIW Title\nSO Journal\nPY 2026\nDI 10.1/ciw\nER\n", encoding="utf-8")
            ris = root / "refs.ris"
            ris.write_text("TY  - JOUR\nAU  - Doe, J\nTI  - RIS Title\nJO  - Journal\nPY  - 2026\nDO  - 10.1/ris\nER  -\n", encoding="utf-8")
            bib = root / "refs.bib"
            bib.write_text("@article{key,\n title={Bib Title},\n author={Doe, J},\n year={2026},\n journal={Journal},\n doi={10.1/bib}\n}\n", encoding="utf-8")
            self.assertEqual("CIW Title", parse_ciw(ciw)[0]["title"])
            self.assertEqual("RIS Title", parse_ris(ris)[0]["title"])
            self.assertEqual("Bib Title", parse_bibtex(bib)[0]["title"])

    def test_docx_deep_audit_detects_revision_and_comment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.docx"
            document = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:ins w:id="1"><w:r><w:t>Inserted</w:t></w:r></w:ins><w:commentRangeStart w:id="0"/></w:p>
</w:body></w:document>'''
            comments = '''<?xml version="1.0" encoding="UTF-8"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:comment w:id="0"><w:p><w:r><w:t>Note</w:t></w:r></w:p></w:comment></w:comments>'''
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("word/comments.xml", comments)
            report = ValidationReport(directory, "test")
            validate_docx(path, report)
            codes = issue_codes(report)
            self.assertIn("tracked_insertions", codes)
            self.assertIn("comments_present", codes)

    def test_docx_detects_hidden_text_broken_ref_and_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.docx"
            document = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>Hidden</w:t></w:r><w:r><w:instrText> REF MissingBookmark </w:instrText></w:r></w:p>
</w:body></w:document>'''
            relationships = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="x" Target="file:///C:/Users/private/data.csv" TargetMode="External"/>
</Relationships>'''
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("word/_rels/document.xml.rels", relationships)
            report = ValidationReport(directory, "test")
            validate_docx(path, report)
            codes = issue_codes(report)
            self.assertIn("hidden_text", codes)
            self.assertIn("broken_cross_reference", codes)
            self.assertIn("private_relationship", codes)

    def test_docx_scans_headers_and_header_relationships(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-header.docx"
            document = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p/></w:body></w:document>'''
            header = '''<?xml version="1.0" encoding="UTF-8"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>Hidden</w:t></w:r></w:p></w:hdr>'''
            relationships = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="x" Target="missing.png"/></Relationships>'''
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("word/header1.xml", header)
                archive.writestr("word/_rels/header1.xml.rels", relationships)
            report = ValidationReport(directory, "test")
            validate_docx(path, report)
            codes = issue_codes(report)
            self.assertIn("hidden_text", codes)
            self.assertIn("broken_relationship", codes)

    def test_bilingual_language_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            english = Path(directory) / "en.md"
            chinese = Path(directory) / "zh.md"
            english.write_text("As an AI language model, I cannot verify this.", encoding="utf-8")
            chinese.write_text("众所周知，本文将深入探讨该问题。", encoding="utf-8")
            self.assertTrue(any(item.rule_id == "assistant_identity" for item in audit_file(english, [], "auto")))
            zh_ids = {item.rule_id for item in audit_file(chinese, [], "auto")}
            self.assertIn("zh_obviousness", zh_ids)
            self.assertIn("zh_section_announcement", zh_ids)

    def test_openalex_adapter_uses_doi_filter_results(self) -> None:
        response = {"results": [{"display_name": "Title", "publication_year": 2026, "cited_by_count": 4, "is_retracted": False, "type": "article"}]}
        with patch.object(metadata_refresh, "fetch_json", return_value=response) as mocked:
            record = metadata_refresh.openalex_record("10.1234/example")
        self.assertEqual("Title", record["title"])
        self.assertFalse(record["is_retracted"])
        self.assertIn("filter=doi%3Ahttps%3A%2F%2Fdoi.org%2F10.1234%2Fexample", mocked.call_args.args[0])

    def test_doi_normalization_handles_whitespace_and_prefixes(self) -> None:
        self.assertEqual("10.1234/example", metadata_refresh.normalize_doi("  https://doi.org/10.1234/Example  "))
        self.assertEqual("10.1234/example", metadata_refresh.normalize_doi(" DOI:10.1234/Example "))


class CommandTests(unittest.TestCase):
    def test_initializer_creates_all_templates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "new-project"
            command = [
                sys.executable,
                str(SCRIPTS / "init_research_project.py"),
                "--profile", "sem-survey",
                "--dest", str(destination),
                "--project-id", "Example Project",
            ]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(0, process.returncode, process.stderr)
            manifest = json.loads((destination / "research_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("sem-survey", manifest["article_type"])
            self.assertTrue((destination / "literature_matrix.csv").exists())
            self.assertTrue((destination / "validation").is_dir())

    def test_cli_missing_manifest_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            process = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_research_package.py"), directory],
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, process.returncode)
            self.assertIn("missing_manifest", process.stdout)


if __name__ == "__main__":
    unittest.main()

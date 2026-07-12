from __future__ import annotations

import re
import struct
from pathlib import Path
from xml.etree import ElementTree

from .common import Issue, ValidationReport, extract_text, load_csv, parse_bool, resolve_project_path, split_values


FIGURE_COLUMNS = {
    "figure_id", "file", "caption", "callout", "source_result_ids", "source_file",
    "generation_command", "intended_width_mm", "minimum_dpi", "vector_required", "status",
}
VECTOR_EXTENSIONS = {".svg", ".pdf", ".eps"}
RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
SCREEN_DIMENSIONS = {(1920, 1080), (1366, 768), (2560, 1440), (3840, 2160), (1536, 864)}


def png_metadata(path: Path) -> tuple[int, int, float | None]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("invalid PNG signature")
        width = height = 0
        dpi = None
        while True:
            length_data = handle.read(4)
            if len(length_data) != 4:
                break
            length = struct.unpack(">I", length_data)[0]
            chunk_type = handle.read(4)
            data = handle.read(length)
            handle.read(4)
            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", data[:8])
            elif chunk_type == b"pHYs" and len(data) >= 9:
                x_ppm, y_ppm, unit = struct.unpack(">IIB", data[:9])
                if unit == 1 and x_ppm and y_ppm:
                    dpi = min(x_ppm, y_ppm) * 0.0254
            elif chunk_type == b"IEND":
                break
        if not width or not height:
            raise ValueError("PNG dimensions are missing")
        return width, height, dpi


def jpeg_metadata(path: Path) -> tuple[int, int, float | None]:
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("invalid JPEG signature")
    offset = 2
    width = height = 0
    dpi = None
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            break
        length = struct.unpack(">H", data[offset:offset + 2])[0]
        segment = data[offset + 2:offset + length]
        if marker == 0xE0 and segment.startswith(b"JFIF\x00") and len(segment) >= 12:
            units = segment[7]
            x_density, y_density = struct.unpack(">HH", segment[8:12])
            if units == 1 and x_density and y_density:
                dpi = float(min(x_density, y_density))
            elif units == 2 and x_density and y_density:
                dpi = float(min(x_density, y_density)) * 2.54
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF} and len(segment) >= 5:
            height, width = struct.unpack(">HH", segment[1:5])
            break
        offset += length
    if not width or not height:
        raise ValueError("JPEG dimensions are missing")
    return width, height, dpi


def tiff_metadata(path: Path) -> tuple[int, int, float | None]:
    data = path.read_bytes()
    if len(data) < 8 or data[:2] not in {b"II", b"MM"}:
        raise ValueError("invalid TIFF byte order")
    endian = "<" if data[:2] == b"II" else ">"
    if struct.unpack(f"{endian}H", data[2:4])[0] != 42:
        raise ValueError("invalid TIFF signature")
    offset = struct.unpack(f"{endian}I", data[4:8])[0]
    if offset + 2 > len(data):
        raise ValueError("invalid TIFF directory")
    count = struct.unpack(f"{endian}H", data[offset:offset + 2])[0]
    values: dict[int, int] = {}
    for position in range(offset + 2, offset + 2 + count * 12, 12):
        if position + 12 > len(data):
            raise ValueError("truncated TIFF directory")
        tag, value_type, item_count = struct.unpack(f"{endian}HHI", data[position:position + 8])
        if tag not in {256, 257} or item_count != 1 or value_type not in {3, 4}:
            continue
        values[tag] = struct.unpack(f"{endian}{'H' if value_type == 3 else 'I'}", data[position + 8:position + (10 if value_type == 3 else 12)])[0]
    if not values.get(256) or not values.get(257):
        raise ValueError("TIFF dimensions are missing")
    return values[256], values[257], None


def validate_svg(path: Path) -> list[str]:
    root = ElementTree.fromstring(path.read_text(encoding="utf-8-sig"))
    warnings: list[str] = []
    if not root.get("viewBox") and not (root.get("width") and root.get("height")):
        warnings.append("SVG lacks viewBox or explicit dimensions")
    for element in root.iter():
        value = element.get("font-size", "")
        match = re.match(r"([0-9.]+)", value)
        if match and float(match.group(1)) < 6:
            warnings.append("SVG contains text smaller than 6 units")
            break
    return warnings


def validate_figures(
    root: Path,
    manifest: dict,
    profile: dict,
    report: ValidationReport,
    result_ids: set[str],
) -> None:
    gate = "figures"
    required = bool(profile.get("require_figures"))
    path = root / "figure_manifest.csv"
    if not path.exists():
        if required:
            report.add(Issue(gate, "error", "missing_figure_manifest", "Figure manifest is missing.", str(path), action="Create figure_manifest.csv and publication-grade figures."))
        return
    report.checked(path)
    try:
        rows = load_csv(path)
    except (OSError, ValueError) as error:
        report.add(Issue(gate, "error", "invalid_figure_manifest", str(error), str(path), action="Repair figure_manifest.csv."))
        return
    if not rows:
        if required:
            report.add(Issue(gate, "error", "empty_figure_manifest", "Figure manifest has no records.", str(path), action="Add claim-supporting figures."))
        return
    missing = FIGURE_COLUMNS - set(rows[0])
    if missing:
        report.add(Issue(gate, "error", "figure_columns", f"Missing columns: {', '.join(sorted(missing))}", str(path), action="Regenerate the figure manifest."))
        return

    manuscript_text = "\n".join(
        extract_text(resolve_project_path(root, value))
        for value in manifest.get("manuscript_files", [])
        if resolve_project_path(root, value).exists()
    )
    ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        location = f"row {index}"
        figure_id = row["figure_id"]
        if not figure_id or figure_id in ids:
            report.add(Issue(gate, "error", "figure_id", "Figure ID is missing or duplicated.", str(path), location, "Assign a unique figure_id."))
        ids.add(figure_id)
        if row["status"].lower() != "final":
            report.add(Issue(gate, "error", "nonfinal_figure", f"Figure {figure_id} is not final.", str(path), location, "Freeze or remove the figure."))
        figure = resolve_project_path(root, row["file"])
        if not row["file"] or not figure.exists():
            report.add(Issue(gate, "error", "missing_figure", f"Figure file is missing for {figure_id}.", str(figure), action="Generate the final figure."))
            continue
        report.checked(figure)
        if not row["caption"]:
            report.add(Issue(gate, "error", "missing_caption", f"Figure {figure_id} has no caption.", str(path), location, "Write a complete scientific caption."))
        if row["callout"] and row["callout"] not in manuscript_text:
            report.add(Issue(gate, "error", "missing_callout", f"Callout '{row['callout']}' was not found in the manuscript.", str(path), location, "Insert the figure callout in sequence."))
        source_file = resolve_project_path(root, row["source_file"]) if row["source_file"] else None
        if not source_file or not source_file.exists():
            report.add(Issue(gate, "error", "missing_figure_source", f"Editable or generation source is missing for {figure_id}.", str(path), location, "Preserve the editable source file."))
        else:
            report.checked(source_file)
        if not row["generation_command"]:
            report.add(Issue(gate, "error", "missing_generation_command", f"Figure {figure_id} has no generation command or export procedure.", str(path), location, "Record the reproducible generation command."))
        unknown_results = set(split_values(row["source_result_ids"])) - result_ids
        if unknown_results:
            report.add(Issue(gate, "error", "unknown_figure_results", f"Figure {figure_id} cites unknown result IDs: {', '.join(sorted(unknown_results))}", str(path), location, "Correct source_result_ids."))

        suffix = figure.suffix.lower()
        vector_required = parse_bool(row["vector_required"])
        if vector_required and suffix not in VECTOR_EXTENSIONS:
            report.add(Issue(gate, "error", "vector_required", f"Figure {figure_id} must be vector but is {suffix}.", str(figure), action="Export as SVG, PDF or EPS."))
        try:
            if suffix == ".png":
                width, height, dpi = png_metadata(figure)
            elif suffix in {".jpg", ".jpeg"}:
                width, height, dpi = jpeg_metadata(figure)
            elif suffix == ".svg":
                for warning in validate_svg(figure):
                    report.add(Issue(gate, "warning", "svg_quality", warning, str(figure), action="Repair SVG sizing and typography."))
                width = height = 0
                dpi = None
            elif suffix == ".pdf":
                if not figure.read_bytes().startswith(b"%PDF"):
                    raise ValueError("invalid PDF signature")
                width = height = 0
                dpi = None
            elif suffix in {".tif", ".tiff"}:
                width, height, dpi = tiff_metadata(figure)
            elif suffix == ".eps":
                width = height = 0
                dpi = None
            else:
                raise ValueError(f"unsupported figure format: {suffix}")
            if suffix in RASTER_EXTENSIONS:
                minimum_dpi = float(row["minimum_dpi"] or "300")
                intended_width = float(row["intended_width_mm"])
                if minimum_dpi <= 0 or intended_width <= 0:
                    raise ValueError("minimum_dpi and intended_width_mm must be positive")
                effective_dpi = width * 25.4 / intended_width
                if effective_dpi < minimum_dpi:
                    report.add(Issue(gate, "error", "low_dpi", f"Raster figure {figure_id} has {effective_dpi:.1f} effective DPI at {intended_width:.1f} mm; minimum is {minimum_dpi:.1f}.", str(figure), action="Increase pixel dimensions or reduce the intended publication width."))
                if dpi is not None and abs(dpi - effective_dpi) / max(effective_dpi, 1.0) > 0.25:
                    report.add(Issue(gate, "warning", "dpi_metadata_mismatch", f"Embedded DPI ({dpi:.1f}) differs from effective publication DPI ({effective_dpi:.1f}).", str(figure), action="Use pixel dimensions and intended publication width as the controlling resolution evidence."))
                if (width, height) in SCREEN_DIMENSIONS or (height, width) in SCREEN_DIMENSIONS:
                    report.add(Issue(gate, "warning", "screenshot_risk", f"Figure {figure_id} matches a common screen resolution.", str(figure), action="Confirm it is not a GUI screenshot and preserve the source."))
        except (OSError, ValueError, ElementTree.ParseError, struct.error) as error:
            report.add(Issue(gate, "error", "invalid_figure", str(error), str(figure), action="Regenerate a valid publication figure."))

from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Any


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _col_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    value = 0
    for ch in letters.upper():
        value = value * 26 + (ord(ch) - ord("A") + 1)
    return value - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in archive.namelist():
        return []

    root = ET.fromstring(archive.read(name))
    strings: list[str] = []
    for item in root.findall(f"{{{MAIN_NS}}}si"):
        parts = [
            node.text or ""
            for node in item.iter(f"{{{MAIN_NS}}}t")
        ]
        strings.append("".join(parts))
    return strings


def _sheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")
    }

    result: dict[str, str] = {}
    sheets = workbook.find(f"{{{MAIN_NS}}}sheets")
    if sheets is None:
        return result

    for sheet in sheets:
        name = sheet.attrib["name"]
        rel_id = sheet.attrib[f"{{{REL_NS}}}id"]
        target = targets[rel_id].lstrip("/")
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        result[name] = target
    return result


def _cell_value(
    cell: ET.Element,
    shared: list[str],
) -> Any:
    cell_type = cell.attrib.get("t")
    value_node = cell.find(f"{{{MAIN_NS}}}v")

    if cell_type == "inlineStr":
        return "".join(
            node.text or ""
            for node in cell.iter(f"{{{MAIN_NS}}}t")
        )

    if value_node is None:
        return ""

    raw = value_node.text or ""

    if cell_type == "s":
        return shared[int(raw)]

    if cell_type == "b":
        return raw == "1"

    if cell_type in {"str", "e"}:
        return raw

    try:
        number = float(raw)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return raw


def _read_sheet(
    archive: zipfile.ZipFile,
    path: str,
    shared: list[str],
) -> list[list[Any]]:
    root = ET.fromstring(archive.read(path))
    sheet_data = root.find(f"{{{MAIN_NS}}}sheetData")
    if sheet_data is None:
        return []

    rows: list[list[Any]] = []
    for row in sheet_data.findall(f"{{{MAIN_NS}}}row"):
        values: dict[int, Any] = {}
        max_col = -1
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            ref = cell.attrib.get("r", "A1")
            index = _col_index(ref)
            values[index] = _cell_value(cell, shared)
            max_col = max(max_col, index)

        if max_col < 0:
            rows.append([])
            continue

        rows.append([values.get(i, "") for i in range(max_col + 1)])

    return rows


def _value(row: list[Any], index: int) -> Any:
    return row[index] if index < len(row) else ""


def _clean(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def _find_pair(rows: list[list[Any]], label: str) -> Any:
    target = label.strip().lower()
    for row in rows:
        if _clean(_value(row, 0)).lower() == target:
            return _value(row, 1)
    raise ValueError(f"Excel project is missing '{label}'.")


def _coerce(value: Any, value_type: str) -> Any:
    kind = value_type.strip().lower()
    text = _clean(value)

    if kind == "yes/no":
        lowered = text.lower()
        if lowered in {"yes", "true", "y", "1"}:
            return True
        if lowered in {"no", "false", "n", "0"}:
            return False
        raise ValueError(f"Expected Yes/No value, got '{text}'.")

    if kind == "number":
        number = float(text)
        return int(number) if number.is_integer() else number

    if kind == "list":
        return [
            item.strip()
            for item in re.split(r"[;,]", text)
            if item.strip()
        ]

    # Date values intentionally remain ISO-like strings so the deterministic
    # engine can compare/annotate them safely.
    return text


def _state_from_table(
    rows: list[list[Any]],
    value_header: str,
) -> dict[str, Any]:
    header_index = None

    for index, row in enumerate(rows):
        headers = [_clean(item).lower() for item in row]
        if (
            "category" in headers
            and "field" in headers
            and value_header.lower() in headers
            and "value type" in headers
        ):
            header_index = index
            break

    if header_index is None:
        raise ValueError(
            f"Excel project is missing the '{value_header}' state table."
        )

    header = [_clean(item).lower() for item in rows[header_index]]
    category_col = header.index("category")
    field_col = header.index("field")
    value_col = header.index(value_header.lower())
    type_col = header.index("value type")

    state: dict[str, Any] = {}

    for row in rows[header_index + 1 :]:
        field = _clean(_value(row, field_col))
        if not field:
            continue

        category = _clean(_value(row, category_col))
        raw_value = _value(row, value_col)
        value_type = _clean(_value(row, type_col)) or "Text"
        parsed = _coerce(raw_value, value_type)

        field_key = _normalize_key(field)
        if category:
            category_key = _normalize_key(category)
            nested = state.setdefault(category_key, {})
            if not isinstance(nested, dict):
                raise ValueError(
                    f"Category '{category}' conflicts with another field."
                )
            nested[field_key] = parsed
        else:
            state[field_key] = parsed

    if not state:
        raise ValueError("Excel project contains no state fields.")

    return state


def xlsx_to_document(data: bytes) -> dict[str, Any]:
    """Convert a DecisionReady business Excel workbook to an internal document."""

    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ValueError("The uploaded file is not a valid .xlsx workbook.") from exc

    with archive:
        required = {"Project", "Approved Baseline", "Proposed Change"}
        paths = _sheet_paths(archive)
        missing = sorted(required - set(paths))
        if missing:
            raise ValueError(
                "Excel project is missing required sheet(s): "
                + ", ".join(missing)
            )

        shared = _shared_strings(archive)
        project_rows = _read_sheet(archive, paths["Project"], shared)
        baseline_rows = _read_sheet(
            archive, paths["Approved Baseline"], shared
        )
        change_rows = _read_sheet(
            archive, paths["Proposed Change"], shared
        )

    project_name = _clean(_find_pair(project_rows, "Project Name"))
    project_id = _clean(_find_pair(project_rows, "Project ID"))
    industry = _clean(
        _find_pair(project_rows, "Program Type / Industry")
    )
    scenario_name = _clean(_find_pair(project_rows, "Scenario Name"))

    baseline_version = int(
        _find_pair(baseline_rows, "Baseline Version")
    )

    change_id = _clean(_find_pair(change_rows, "Change ID"))
    change_title = _clean(_find_pair(change_rows, "Change Title"))
    requested_by = _clean(_find_pair(change_rows, "Requested By"))
    description = _clean(_find_pair(change_rows, "Description"))

    baseline_state = _state_from_table(
        baseline_rows, "Approved Value"
    )
    proposed_state = _state_from_table(
        change_rows, "Proposed Value"
    )

    return {
        "scenario_name": scenario_name or project_name,
        "industry": industry,
        "project": {
            "project_id": project_id,
            "name": project_name,
        },
        "baseline": {
            "version": baseline_version,
            "state": baseline_state,
        },
        "change": {
            "change_id": change_id,
            "title": change_title,
            "description": description,
            "requested_by": requested_by,
        },
        "proposed_state": proposed_state,
    }

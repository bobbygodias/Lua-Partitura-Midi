#!/usr/bin/env python3
"""Audit MusicXML/MXL structure and notation consistency."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET


TYPE_QUARTERS = {
    "maxima": Fraction(32),
    "long": Fraction(16),
    "breve": Fraction(8),
    "whole": Fraction(4),
    "half": Fraction(2),
    "quarter": Fraction(1),
    "eighth": Fraction(1, 2),
    "16th": Fraction(1, 4),
    "32nd": Fraction(1, 8),
    "64th": Fraction(1, 16),
    "128th": Fraction(1, 32),
    "256th": Fraction(1, 64),
    "512th": Fraction(1, 128),
    "1024th": Fraction(1, 256),
}


class ScoreError(ValueError):
    pass


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(parent: ET.Element, path: str) -> str | None:
    node = parent.find(path)
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def integer_of(parent: ET.Element, path: str, label: str) -> int:
    value = text_of(parent, path)
    if value is None:
        raise ScoreError(f"{label} ausente")
    try:
        return int(value)
    except ValueError as exc:
        raise ScoreError(f"{label} não inteiro: {value}") from exc


def load_score(path: Path) -> tuple[bytes, str | None]:
    if path.suffix.lower() != ".mxl":
        return path.read_bytes(), None
    with zipfile.ZipFile(path) as archive:
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
        except (KeyError, ET.ParseError) as exc:
            raise ScoreError("MXL sem META-INF/container.xml válido") from exc
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ScoreError("MXL sem rootfile")
        member = rootfile.get("full-path")
        try:
            return archive.read(member), member
        except KeyError as exc:
            raise ScoreError(f"rootfile MXL ausente: {member}") from exc


def pitch_identity(note: ET.Element) -> str:
    pitch = note.find("./{*}pitch")
    if pitch is not None:
        step = text_of(pitch, "./{*}step") or "?"
        alter = text_of(pitch, "./{*}alter") or "0"
        octave = text_of(pitch, "./{*}octave") or "?"
        return f"{step}:{alter}:{octave}"
    unpitched = note.find("./{*}unpitched")
    if unpitched is not None:
        step = text_of(unpitched, "./{*}display-step") or "?"
        octave = text_of(unpitched, "./{*}display-octave") or "?"
        instrument = note.find("./{*}instrument")
        inst_id = instrument.get("id", "") if instrument is not None else ""
        return f"unpitched:{step}:{octave}:{inst_id}"
    if note.find("./{*}rest") is not None:
        return "rest"
    return "missing"


def notated_duration(note: ET.Element) -> Fraction | None:
    note_type = text_of(note, "./{*}type")
    if note_type is None:
        return None
    if note_type not in TYPE_QUARTERS:
        raise ScoreError(f"tipo de nota desconhecido: {note_type}")
    dots = len(note.findall("./{*}dot"))
    dot_factor = Fraction(2) - Fraction(1, 2**dots) if dots else Fraction(1)
    result = TYPE_QUARTERS[note_type] * dot_factor
    time_mod = note.find("./{*}time-modification")
    if time_mod is not None:
        actual = integer_of(time_mod, "./{*}actual-notes", "actual-notes")
        normal = integer_of(time_mod, "./{*}normal-notes", "normal-notes")
        if actual <= 0 or normal <= 0:
            raise ScoreError("razão de quiáltera não positiva")
        result *= Fraction(normal, actual)
    return result


def audit(path: Path, schema: Path | None = None) -> dict:
    xml_bytes, mxl_member = load_score(path)
    errors: list[str] = []
    warnings: list[str] = []

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ScoreError(f"XML malformado: {exc}") from exc
    root_type = local(root.tag)
    if root_type != "score-partwise":
        errors.append(f"raiz não suportada para auditoria estrita: {root_type}")

    if schema is not None:
        try:
            from lxml import etree

            schema_doc = etree.parse(str(schema))
            validator = etree.XMLSchema(schema_doc)
            validator.assertValid(etree.fromstring(xml_bytes))
        except ImportError:
            errors.append("lxml ausente; validação XSD solicitada não executada")
        except Exception as exc:  # lxml exposes several schema exception types
            errors.append(f"MusicXML não passou no XSD: {exc}")

    title = (
        text_of(root, "./{*}work/{*}work-title")
        or text_of(root, "./{*}movement-title")
    )
    if not title:
        warnings.append("título ausente")
    creators = [
        (node.get("type") or "creator", (node.text or "").strip())
        for node in root.findall("./{*}identification/{*}creator")
        if (node.text or "").strip()
    ]

    part_defs: dict[str, str] = {}
    for score_part in root.findall("./{*}part-list/{*}score-part"):
        part_id = score_part.get("id")
        if not part_id:
            errors.append("score-part sem id")
            continue
        if part_id in part_defs:
            errors.append(f"id de parte duplicado na part-list: {part_id}")
        part_defs[part_id] = text_of(score_part, "./{*}part-name") or ""
        if not part_defs[part_id]:
            warnings.append(f"parte {part_id} sem part-name")

    seen_parts: set[str] = set()
    part_reports = []
    for part in root.findall("./{*}part"):
        part_id = part.get("id") or ""
        if not part_id:
            errors.append("part sem id")
            continue
        if part_id in seen_parts:
            errors.append(f"part duplicada: {part_id}")
        seen_parts.add(part_id)
        if part_id not in part_defs:
            errors.append(f"part {part_id} não declarada na part-list")

        divisions: int | None = None
        meter: tuple[int, int] | None = None
        active_ties: set[tuple[str, str, str]] = set()
        active_tuplets: set[tuple[str, str, str]] = set()
        measures = []
        measure_numbers: set[str] = set()

        part_measures = part.findall("./{*}measure")
        for measure_index, measure in enumerate(part_measures):
            number = measure.get("number") or str(measure_index + 1)
            context = f"{part_id} compasso {number}"
            if number in measure_numbers:
                warnings.append(f"{part_id}: número de compasso repetido: {number}")
            measure_numbers.add(number)

            cursor = Fraction(0)
            max_extent = Fraction(0)
            last_note_onset: Fraction | None = None
            notes_count = 0

            for child in list(measure):
                kind = local(child.tag)
                if kind == "attributes":
                    value = text_of(child, "./{*}divisions")
                    if value is not None:
                        try:
                            divisions = int(value)
                        except ValueError:
                            errors.append(f"{context}: divisions não inteiro")
                        if divisions is not None and divisions <= 0:
                            errors.append(f"{context}: divisions deve ser positivo")
                    time_node = child.find("./{*}time")
                    if time_node is not None and not time_node.get("symbol") == "senza-misura":
                        try:
                            beats = integer_of(time_node, "./{*}beats", "beats")
                            beat_type = integer_of(time_node, "./{*}beat-type", "beat-type")
                            if beats <= 0 or beat_type <= 0:
                                raise ScoreError("compasso não positivo")
                            meter = (beats, beat_type)
                        except ScoreError as exc:
                            errors.append(f"{context}: {exc}")
                    continue

                if kind in ("backup", "forward"):
                    try:
                        raw_duration = integer_of(child, "./{*}duration", "duration")
                    except ScoreError as exc:
                        errors.append(f"{context}: {exc}")
                        continue
                    if divisions is None or divisions <= 0:
                        errors.append(f"{context}: duração antes de divisions")
                        continue
                    amount = Fraction(raw_duration, divisions)
                    cursor += -amount if kind == "backup" else amount
                    if cursor < 0:
                        errors.append(f"{context}: backup move cursor antes do início")
                        cursor = Fraction(0)
                    max_extent = max(max_extent, cursor)
                    last_note_onset = None
                    continue

                if kind != "note":
                    continue

                notes_count += 1
                is_grace = child.find("./{*}grace") is not None
                is_chord = child.find("./{*}chord") is not None
                voice = text_of(child, "./{*}voice") or "1"
                staff = text_of(child, "./{*}staff") or "1"
                identity = pitch_identity(child)
                if identity == "missing":
                    errors.append(f"{context}: nota sem pitch, unpitched ou rest")

                duration_q = Fraction(0)
                raw_duration = text_of(child, "./{*}duration")
                if not is_grace:
                    if raw_duration is None:
                        errors.append(f"{context}: nota não-grace sem duration")
                    elif divisions is None or divisions <= 0:
                        errors.append(f"{context}: nota antes de divisions")
                    else:
                        try:
                            duration_value = int(raw_duration)
                            if duration_value <= 0:
                                errors.append(f"{context}: duração de nota não positiva")
                            duration_q = Fraction(duration_value, divisions)
                        except ValueError:
                            errors.append(f"{context}: duration não inteiro")

                if is_chord:
                    if last_note_onset is None:
                        errors.append(f"{context}: membro de acorde sem nota-base anterior")
                        onset = cursor
                    else:
                        onset = last_note_onset
                else:
                    onset = cursor
                    last_note_onset = onset
                    if not is_grace:
                        cursor += duration_q
                max_extent = max(max_extent, onset + duration_q, cursor)

                if not is_grace and duration_q > 0:
                    try:
                        display_duration = notated_duration(child)
                        if display_duration is not None and display_duration != duration_q:
                            warnings.append(
                                f"{context}: type/dots/time-modification ({display_duration}) "
                                f"difere de duration/divisions ({duration_q})"
                            )
                    except ScoreError as exc:
                        errors.append(f"{context}: {exc}")

                sound_ties = {
                    node.get("type") for node in child.findall("./{*}tie") if node.get("type")
                }
                visual_ties = {
                    node.get("type")
                    for node in child.findall("./{*}notations/{*}tied")
                    if node.get("type")
                }
                relevant_sound = sound_ties & {"start", "stop"}
                relevant_visual = visual_ties & {"start", "stop"}
                if relevant_sound != relevant_visual:
                    warnings.append(f"{context}: tie e tied divergentes em {identity}")
                tie_types = relevant_sound | relevant_visual
                tie_key = (voice, staff, identity)
                if "stop" in tie_types:
                    if tie_key not in active_ties:
                        warnings.append(f"{context}: tie stop sem start em {identity}")
                    else:
                        active_ties.remove(tie_key)
                if "start" in tie_types:
                    if tie_key in active_ties:
                        warnings.append(f"{context}: tie start duplicado em {identity}")
                    active_ties.add(tie_key)

                for tuplet in child.findall("./{*}notations/{*}tuplet"):
                    tuplet_type = tuplet.get("type")
                    number_attr = tuplet.get("number") or "1"
                    tuplet_key = (voice, staff, number_attr)
                    if tuplet_type == "stop":
                        if tuplet_key not in active_tuplets:
                            warnings.append(f"{context}: tuplet stop sem start")
                        else:
                            active_tuplets.remove(tuplet_key)
                    elif tuplet_type == "start":
                        if tuplet_key in active_tuplets:
                            warnings.append(f"{context}: tuplet start duplicado")
                        active_tuplets.add(tuplet_key)

            expected = None
            if meter is not None:
                expected = Fraction(meter[0] * 4, meter[1])
                if max_extent > expected:
                    errors.append(
                        f"{context}: conteúdo excede compasso ({max_extent} > {expected} semínimas)"
                    )
                if cursor != expected:
                    implicit = measure.get("implicit") == "yes"
                    if implicit and cursor < expected:
                        pass
                    elif measure_index == len(part_measures) - 1 and cursor < expected:
                        warnings.append(
                            f"{context}: compasso final incompleto ({cursor}/{expected})"
                        )
                    else:
                        errors.append(
                            f"{context}: duração final {cursor}, esperada {expected} semínimas"
                        )
            else:
                warnings.append(f"{context}: métrica ainda não definida")
            measures.append(
                {
                    "number": number,
                    "notes": notes_count,
                    "cursor_quarters": str(cursor),
                    "expected_quarters": str(expected) if expected is not None else None,
                }
            )

        if active_ties:
            errors.append(f"{part_id}: {len(active_ties)} tie(s) sem encerramento")
        if active_tuplets:
            errors.append(f"{part_id}: {len(active_tuplets)} tuplet(s) sem encerramento")
        part_reports.append(
            {
                "id": part_id,
                "name": part_defs.get(part_id, ""),
                "measure_count": len(part_measures),
                "measures": measures,
            }
        )

    missing_parts = sorted(set(part_defs) - seen_parts)
    for part_id in missing_parts:
        errors.append(f"parte declarada sem conteúdo: {part_id}")
    if not part_reports:
        errors.append("nenhuma parte musical encontrada")

    return {
        "file": str(path),
        "mxl_rootfile": mxl_member,
        "root_type": root_type,
        "musicxml_version": root.get("version"),
        "title": title,
        "creators": creators,
        "parts": part_reports,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    parser.add_argument("--schema", type=Path, help="MusicXML XSD para validação adicional")
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args()
    try:
        report = audit(args.score, args.schema)
    except (OSError, ScoreError, zipfile.BadZipFile) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_path:
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
